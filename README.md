# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommender that scores songs against a user's taste profile and ranks the catalog to produce personalized suggestions. Each song is judged individually using weighted rules for genre, mood, and energy similarity, then the highest-scoring tracks are returned with plain-language explanations.

---

## How The System Works

### Real-World Recommendations vs. This Simulation

Major platforms like Spotify and YouTube Music use a mix of **collaborative filtering** (learning from what similar users liked, skipped, or replayed) and **content-based filtering** (matching song attributes like tempo, energy, and genre to a user's profile). Collaborative filtering can surface hidden gems because it does not need to know why two users are alike — it only needs their behavior. Content-based filtering works even for brand-new users with no listening history, because it compares song features directly to stated or inferred preferences.

This simulation uses **content-based filtering only**. It cannot learn from other users' playlists or discover trends. Instead, it prioritizes explicit matches on genre and mood, plus numerical closeness on energy. That makes it transparent and easy to debug, but much simpler than production systems that blend dozens of signals at scale.

### Data Flow

```
User Preferences (genre, mood, energy)
        ↓
   Load songs.csv
        ↓
   For each song → score_song() → (score, reasons)
        ↓
   Sort all songs by score (highest first)
        ↓
   Return top K recommendations with explanations
```

### Song Features

Each `Song` in the catalog uses:

| Feature | Type | Role |
|---------|------|------|
| `genre` | text | Primary taste category (pop, lofi, rock, etc.) |
| `mood` | text | Emotional tone (happy, chill, intense, etc.) |
| `energy` | 0.0–1.0 | How intense/active the track feels |
| `tempo_bpm` | number | Beats per minute |
| `valence` | 0.0–1.0 | Musical positivity |
| `danceability` | 0.0–1.0 | How suitable for dancing |
| `acousticness` | 0.0–1.0 | How acoustic vs. electronic |
| `popularity` | 0–100 | Chart / play popularity boost |
| `release_decade` | year | Decade match bonus (e.g. 2020) |
| `mood_tag` | text | Detailed tag (euphoric, nostalgic, aggressive…) |
| `instrumentalness` | 0.0–1.0 | Instrumental preference bonus |
| `speechiness` | 0.0–1.0 | Spoken-word content (available for future use) |

### UserProfile / User Preferences

The `UserProfile` (OOP) and dictionary-based `user_prefs` (CLI) store:

- `favorite_genre` / `genre` — the user's preferred genre
- `favorite_mood` / `mood` — the user's preferred mood
- `target_energy` / `energy` — desired energy level (0.0–1.0)
- `likes_acoustic` (optional) — bonus for acoustic tracks
- `preferred_decade`, `preferred_mood_tag`, `likes_instrumental`, `min_popularity` (optional advanced prefs)

### Algorithm Recipe

**Scoring Rule** (one song at a time, balanced mode):

| Rule | Points |
|------|--------|
| Genre match | +2.0 |
| Mood match | +1.0 |
| Energy similarity | `(1.0 − |song_energy − target_energy|) × 1.5` |
| Acoustic bonus (if `likes_acoustic`) | +0.5 when `acousticness ≥ 0.5` |
| Popularity boost | `(popularity / 100) × 0.5` |
| Decade match | +0.4 |
| Mood tag match | +0.8 |
| Instrumental bonus | +0.3 when `instrumentalness ≥ 0.6` |

Energy uses a **closeness reward**, not a "higher is better" rule. A song with energy 0.82 scores higher for a target of 0.8 than a song with energy 0.95, because the gap is smaller.

**Ranking Rule** (the full list):

After every song receives a score, the system sorts the catalog, then applies a **diversity penalty** while building the top *K* (artist −1.0, genre −0.5 if already selected). The scoring rule answers "how good is this one song?" while the ranking rule answers "which songs are best overall without repeating the same artist/genre?"

**Scoring modes** (Strategy pattern): switch `ACTIVE_MODE` in `src/main.py` between `balanced`, `genre_first`, `mood_first`, and `energy_focused`.

### Expected Biases

- **Genre dominance**: Genre is worth twice as much as mood, so a pop song with the wrong mood can still outrank a perfect-mood indie track.
- **No sad-pop songs in catalog**: A user who wants "pop + sad" gets high-energy pop anyway because genre and energy outweigh the missing mood match.
- **Small catalog**: With only 18 songs, the same tracks (like Gym Hero) appear frequently across profiles.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

---

## Sample Recommendation Output

Default "Happy Pop" profile with advanced features + diversity (mode=`balanced`):

```
Loaded songs: 18
Available scoring modes: balanced, genre_first, mood_first, energy_focused
Active mode: balanced
Diversity penalty: ON (artist -1.0, genre -0.5)

========================================================================
Profile: Happy Pop  |  Mode: balanced
Preferences: genre=pop, mood=happy, energy=0.8
========================================================================
Rank  Title                   Artist          Score   Reasons
------------------------------------------------------------------------------------------
1     Sunrise City            Neon Echo       6.06    genre match (+2.0); mood match (+1.0); energy similarity (1.47); popularity boost (+0.39); decade match (+0.4); mood tag match (+0.8)
2     Rooftop Lights          Indigo Parade   4.01    mood match (+1.0); energy similarity (1.44); popularity boost (+0.37); decade match (+0.4); mood tag match (+0.8)
3     Gym Hero                Max Pulse       3.63    genre match (+2.0); energy similarity (1.30); popularity boost (+0.42); decade match (+0.4); genre diversity (-0.5)
4     Bass Drop Nation        DJ Flux         2.90    energy similarity (1.26); popularity boost (+0.44); decade match (+0.4); mood tag match (+0.8)
5     Street Cipher           MC Verse        2.27    energy similarity (1.47); popularity boost (+0.41); decade match (+0.4)
```

Sunrise City ranks first because it matches genre, mood, decade, and mood tag while sitting close to the target energy. Diversity penalty pushes Gym Hero down slightly (`genre diversity (-0.5)`) so Rooftop Lights can stay at #2.

---

## Optional Extensions

All four stretch challenges are implemented. Details and prompts are in [`ai_interactions.md`](ai_interactions.md).

1. **Advanced features** — popularity, release decade, mood tags, instrumentalness, speechiness
2. **Scoring modes** — Strategy pattern: `balanced`, `genre_first`, `mood_first`, `energy_focused` (set `ACTIVE_MODE` in `src/main.py`)
3. **Diversity penalty** — artist (−1.0) and genre (−0.5) penalties while building top-K
4. **Visual table** — `format_recommendations_table()` via `tabulate` (ASCII fallback if missing)

---

## Experiments You Tried

### Weight Shift: Double Energy, Halve Genre

Changed `GENRE_WEIGHT` from 2.0 → 1.0 and `ENERGY_WEIGHT` from 1.5 → 3.0, then re-ran the Happy Pop profile:

| Rank | Baseline | Experiment |
|------|----------|------------|
| 1 | Sunrise City (4.47) | Sunrise City (4.94) |
| 2 | Gym Hero (3.30) | **Rooftop Lights (3.88)** |
| 3 | Rooftop Lights (2.44) | Gym Hero (3.61) |

Rooftop Lights moved from #3 to #2 because it has energy 0.76 (very close to 0.8) even though its genre is "indie pop" not "pop." With weaker genre weighting, energy similarity mattered more. The top pick stayed the same, but the middle of the list reshuffled — the system became more "vibe-first" and less "genre-first."

### Scoring Mode Comparison

Same Happy Pop profile under all four Strategy modes: `genre_first` elevates Gym Hero; `mood_first` elevates Rooftop Lights; `energy_focused` elevates Bass Drop Nation. See `ai_interactions.md`.

### Diverse Profile Testing

Tested five profiles: Happy Pop, Chill Lofi, Deep Intense Rock, Gym EDM, and a conflicting high-energy/sad profile. See `model_card.md` for full output comparisons.

---

## Limitations and Risks

- **Tiny catalog** (18 songs) — not representative of real streaming libraries.
- **No collaborative signals** — cannot learn from listening history or other users.
- **Genre string matching only** — "indie pop" does not match "pop," even though they are related.
- **Filter bubble risk** — reduced by the diversity penalty, but still present for strong genre matches.
- **Unused features** — tempo, valence, danceability, and speechiness are in the data but not yet scored.

See the full analysis in [**Model Card**](model_card.md).

---

## Reflection

The biggest takeaway is how much a simple weighted formula can already *feel* like a real recommender — until you test edge cases. A user who wants "sad pop" still gets Gym Hero because genre points and energy similarity overpower the missing mood match. That taught me why production systems need many more signals, fallback logic, and diversity rules.

Working through the scoring math by hand (before coding) made debugging much faster. When Sunrise City ranked #1 for Happy Pop, I could trace every point back to the recipe instead of guessing. The weight-shift experiment and scoring-mode comparison confirmed that small constant changes can reshuffle results without changing the top pick — a reminder that "tuning" recommender weights is a real engineering task, not just a one-time design choice.

Full reflection: [**Model Card — Section 9**](model_card.md#9-personal-reflection).
