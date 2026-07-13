"""
Command line runner for the Music Recommender Simulation.
"""

from src.recommender import (
    SCORING_MODES,
    format_recommendations_table,
    load_songs,
    recommend_songs,
)

USER_PROFILES = {
    "Happy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "preferred_mood_tag": "euphoric",
        "preferred_decade": 2020,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "likes_acoustic": True,
        "likes_instrumental": True,
        "preferred_mood_tag": "nostalgic",
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "preferred_mood_tag": "aggressive",
    },
    "Gym EDM": {
        "genre": "edm",
        "mood": "euphoric",
        "energy": 0.95,
        "preferred_mood_tag": "euphoric",
        "min_popularity": 50,
    },
    "Conflicting (high energy + sad)": {
        "genre": "pop",
        "mood": "sad",
        "energy": 0.9,
    },
}

# Switch this to try genre_first, mood_first, or energy_focused
ACTIVE_MODE = "balanced"


def print_recommendations(
    profile_name: str,
    user_prefs: dict,
    songs: list,
    k: int = 5,
    mode: str = "balanced",
) -> None:
    """Print a formatted table of top recommendations for a user profile."""
    recommendations = recommend_songs(
        user_prefs, songs, k=k, mode=mode, apply_diversity=True
    )

    print(f"\n{'=' * 72}")
    print(f"Profile: {profile_name}  |  Mode: {mode}")
    print(
        f"Preferences: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']}"
    )
    print(f"{'=' * 72}")
    print(format_recommendations_table(recommendations))
    print()


def demo_scoring_modes(songs: list) -> None:
    """Show how the same Happy Pop profile ranks under each scoring mode."""
    prefs = USER_PROFILES["Happy Pop"]
    print(f"\n{'#' * 72}")
    print("SCORING MODE COMPARISON (Happy Pop profile)")
    print(f"{'#' * 72}")
    for mode_name in SCORING_MODES:
        print_recommendations(
            f"Happy Pop [{mode_name}]", prefs, songs, k=5, mode=mode_name
        )


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Available scoring modes: {', '.join(SCORING_MODES)}")
    print(f"Active mode: {ACTIVE_MODE}")
    print("Diversity penalty: ON (artist -1.0, genre -0.5)")

    for profile_name, user_prefs in USER_PROFILES.items():
        print_recommendations(
            profile_name, user_prefs, songs, k=5, mode=ACTIVE_MODE
        )

    demo_scoring_modes(songs)


if __name__ == "__main__":
    main()
