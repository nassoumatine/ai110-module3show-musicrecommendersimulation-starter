"""Content-based music recommender with scoring modes and diversity logic."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Default (balanced) weights
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5
POPULARITY_WEIGHT = 0.5
DECADE_BONUS = 0.4
MOOD_TAG_BONUS = 0.8
INSTRUMENTAL_BONUS = 0.3

ARTIST_DIVERSITY_PENALTY = 1.0
GENRE_DIVERSITY_PENALTY = 0.5

NUMERIC_FIELDS = (
    "energy",
    "tempo_bpm",
    "valence",
    "danceability",
    "acousticness",
    "popularity",
    "release_decade",
    "instrumentalness",
    "speechiness",
)


@dataclass
class Song:
    """Represents a song and its attributes."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float = 50.0
    release_decade: float = 2020.0
    mood_tag: str = ""
    instrumentalness: float = 0.0
    speechiness: float = 0.0


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    preferred_mood_tag: Optional[str] = None
    likes_instrumental: bool = False
    min_popularity: float = 0.0


@dataclass
class ScoringWeights:
    """Point weights for one scoring strategy."""

    genre: float
    mood: float
    energy: float
    acoustic: float = ACOUSTIC_BONUS
    popularity: float = POPULARITY_WEIGHT
    decade: float = DECADE_BONUS
    mood_tag: float = MOOD_TAG_BONUS
    instrumental: float = INSTRUMENTAL_BONUS


class ScoringStrategy(ABC):
    """Strategy pattern: different ways to weight song attributes."""

    name: str

    @abstractmethod
    def weights(self) -> ScoringWeights:
        """Return the weight configuration for this mode."""


class BalancedStrategy(ScoringStrategy):
    """Default balanced mix of genre, mood, and energy."""

    name = "balanced"

    def weights(self) -> ScoringWeights:
        return ScoringWeights(genre=2.0, mood=1.0, energy=1.5)


class GenreFirstStrategy(ScoringStrategy):
    """Prioritize genre matches over mood and energy."""

    name = "genre_first"

    def weights(self) -> ScoringWeights:
        return ScoringWeights(genre=4.0, mood=0.5, energy=0.75)


class MoodFirstStrategy(ScoringStrategy):
    """Prioritize mood and mood-tag matches."""

    name = "mood_first"

    def weights(self) -> ScoringWeights:
        return ScoringWeights(genre=0.5, mood=3.0, energy=1.0, mood_tag=1.5)


class EnergyFocusedStrategy(ScoringStrategy):
    """Prioritize energy closeness for workout / vibe matching."""

    name = "energy_focused"

    def weights(self) -> ScoringWeights:
        return ScoringWeights(genre=1.0, mood=0.5, energy=3.0)


SCORING_MODES: Dict[str, ScoringStrategy] = {
    BalancedStrategy.name: BalancedStrategy(),
    GenreFirstStrategy.name: GenreFirstStrategy(),
    MoodFirstStrategy.name: MoodFirstStrategy(),
    EnergyFocusedStrategy.name: EnergyFocusedStrategy(),
}


def get_strategy(mode: str) -> ScoringStrategy:
    """Look up a scoring strategy by name, defaulting to balanced."""
    return SCORING_MODES.get(mode, SCORING_MODES["balanced"])


def _energy_similarity(
    song_energy: float, target_energy: float, energy_weight: float
) -> Tuple[float, str]:
    """Reward songs whose energy is close to the user's target."""
    gap = abs(song_energy - target_energy)
    points = max(0.0, 1.0 - gap) * energy_weight
    return points, f"energy similarity ({points:.2f})"


def _score_attributes(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    likes_acoustic: bool = False,
    popularity: float = 50.0,
    release_decade: float = 2020.0,
    mood_tag: str = "",
    instrumentalness: float = 0.0,
    preferred_decade: Optional[int] = None,
    preferred_mood_tag: Optional[str] = None,
    likes_instrumental: bool = False,
    min_popularity: float = 0.0,
    weights: Optional[ScoringWeights] = None,
) -> Tuple[float, List[str]]:
    """Apply the algorithm recipe to a song's attributes."""
    w = weights or ScoringWeights(genre=GENRE_WEIGHT, mood=MOOD_WEIGHT, energy=ENERGY_WEIGHT)
    score = 0.0
    reasons: List[str] = []

    if genre.lower() == favorite_genre.lower():
        score += w.genre
        reasons.append(f"genre match (+{w.genre})")

    if mood.lower() == favorite_mood.lower():
        score += w.mood
        reasons.append(f"mood match (+{w.mood})")

    energy_pts, energy_reason = _energy_similarity(energy, target_energy, w.energy)
    score += energy_pts
    reasons.append(energy_reason)

    if likes_acoustic and acousticness >= 0.5:
        score += w.acoustic
        reasons.append(f"acoustic preference (+{w.acoustic})")

    # Advanced features
    if popularity >= min_popularity and popularity > 0:
        pop_pts = (popularity / 100.0) * w.popularity
        score += pop_pts
        reasons.append(f"popularity boost (+{pop_pts:.2f})")

    if preferred_decade is not None and int(release_decade) == int(preferred_decade):
        score += w.decade
        reasons.append(f"decade match (+{w.decade})")

    if preferred_mood_tag and mood_tag.lower() == preferred_mood_tag.lower():
        score += w.mood_tag
        reasons.append(f"mood tag match (+{w.mood_tag})")

    if likes_instrumental and instrumentalness >= 0.6:
        score += w.instrumental
        reasons.append(f"instrumental preference (+{w.instrumental})")

    return score, reasons


class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song], mode: str = "balanced"):
        self.songs = songs
        self.strategy = get_strategy(mode)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score every song and return the top k ranked results."""
        weights = self.strategy.weights()
        scored = []
        for song in self.songs:
            score, _ = _score_attributes(
                song.genre,
                song.mood,
                song.energy,
                song.acousticness,
                user.favorite_genre,
                user.favorite_mood,
                user.target_energy,
                user.likes_acoustic,
                song.popularity,
                song.release_decade,
                song.mood_tag,
                song.instrumentalness,
                user.preferred_decade,
                user.preferred_mood_tag,
                user.likes_instrumental,
                user.min_popularity,
                weights,
            )
            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        weights = self.strategy.weights()
        _, reasons = _score_attributes(
            song.genre,
            song.mood,
            song.energy,
            song.acousticness,
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.likes_acoustic,
            song.popularity,
            song.release_decade,
            song.mood_tag,
            song.instrumentalness,
            user.preferred_decade,
            user.preferred_mood_tag,
            user.likes_instrumental,
            user.min_popularity,
            weights,
        )
        return "; ".join(reasons) if reasons else "No strong matches found"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = dict(row)
            song["id"] = int(song["id"])
            for field in NUMERIC_FIELDS:
                if field in song and song[field] != "":
                    song[field] = float(song[field])
            songs.append(song)
    return songs


def score_song(
    user_prefs: Dict, song: Dict, mode: str = "balanced"
) -> Tuple[float, List[str]]:
    """Score a single song against user preferences and return score with reasons."""
    weights = get_strategy(mode).weights()
    return _score_attributes(
        song["genre"],
        song["mood"],
        song["energy"],
        song["acousticness"],
        user_prefs["genre"],
        user_prefs["mood"],
        user_prefs["energy"],
        user_prefs.get("likes_acoustic", False),
        float(song.get("popularity", 50)),
        float(song.get("release_decade", 2020)),
        song.get("mood_tag", ""),
        float(song.get("instrumentalness", 0)),
        user_prefs.get("preferred_decade"),
        user_prefs.get("preferred_mood_tag"),
        user_prefs.get("likes_instrumental", False),
        float(user_prefs.get("min_popularity", 0)),
        weights,
    )


def apply_diversity_penalty(
    ranked: List[Tuple[Dict, float, List[str]]], k: int
) -> List[Tuple[Dict, float, List[str]]]:
    """Re-rank greedily, penalizing repeated artists and genres in the top results."""
    selected: List[Tuple[Dict, float, List[str]]] = []
    seen_artists: set = set()
    seen_genres: set = set()
    remaining = list(ranked)

    while remaining and len(selected) < k:
        best_idx = 0
        best_adjusted = float("-inf")
        best_reasons: List[str] = []

        for i, (song, base_score, reasons) in enumerate(remaining):
            adjusted = base_score
            extra: List[str] = []
            if song["artist"] in seen_artists:
                adjusted -= ARTIST_DIVERSITY_PENALTY
                extra.append(f"artist diversity (-{ARTIST_DIVERSITY_PENALTY})")
            if song["genre"] in seen_genres:
                adjusted -= GENRE_DIVERSITY_PENALTY
                extra.append(f"genre diversity (-{GENRE_DIVERSITY_PENALTY})")
            if adjusted > best_adjusted:
                best_adjusted = adjusted
                best_idx = i
                best_reasons = reasons + extra

        song, _, _ = remaining.pop(best_idx)
        selected.append((song, best_adjusted, best_reasons))
        seen_artists.add(song["artist"])
        seen_genres.add(song["genre"])

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    apply_diversity: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, optionally diversify, and return the top k with explanations."""
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        scored.append((song, score, reasons))

    scored.sort(key=lambda item: item[1], reverse=True)

    if apply_diversity:
        top = apply_diversity_penalty(scored, k)
    else:
        top = scored[:k]

    return [
        (song, score, "; ".join(reasons) if reasons else "No strong matches found")
        for song, score, reasons in top
    ]


def format_recommendations_table(
    recommendations: List[Tuple[Dict, float, str]],
) -> str:
    """Build a readable ASCII table of recommendations including reasons."""
    try:
        from tabulate import tabulate

        rows = []
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            rows.append(
                [
                    rank,
                    song["title"],
                    song["artist"],
                    song["genre"],
                    f"{score:.2f}",
                    explanation,
                ]
            )
        return tabulate(
            rows,
            headers=["Rank", "Title", "Artist", "Genre", "Score", "Reasons"],
            tablefmt="grid",
            maxcolwidths=[None, 22, 16, 12, None, 48],
        )
    except ImportError:
        lines = [
            f"{'Rank':<6}{'Title':<24}{'Artist':<16}{'Score':<8}Reasons",
            "-" * 90,
        ]
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            lines.append(
                f"{rank:<6}{song['title']:<24}{song['artist']:<16}{score:<8.2f}{explanation}"
            )
        return "\n".join(lines)
