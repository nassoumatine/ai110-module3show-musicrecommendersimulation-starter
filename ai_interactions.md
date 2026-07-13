# AI Interactions Log

> **Stretch features only.** Documents the optional extensions added to VibeFinder 1.0.

---

## Agentic Workflow (SF8) — Challenge 1: Advanced Song Features

**What task did you give the agent?**

Expand `data/songs.csv` with five new attributes (popularity, release decade, detailed mood tags, instrumentalness, speechiness), then update scoring in `src/recommender.py` so those attributes affect rankings.

**Prompts used:**

> Add five advanced song features to songs.csv that are not in the baseline data: Song Popularity (0–100), Release Decade, Detailed Mood Tags (e.g. nostalgic, aggressive, euphoric), Instrumentalness (0–1), and Speechiness (0–1). Update both the CSV and the scoring logic in recommender.py so scoring accounts for the new attributes. Keep existing tests working by giving new Song fields default values.

**What did the agent generate or change?**

- Extended every row in `data/songs.csv` with: `popularity`, `release_decade`, `mood_tag`, `instrumentalness`, `speechiness`
- Updated `Song` dataclass with optional defaults so starter tests still pass
- Extended `_score_attributes` / `score_song` with:
  - popularity boost (scaled 0–0.5)
  - decade match bonus (+0.4)
  - mood tag match bonus (+0.8)
  - instrumental preference bonus (+0.3)

**What did you verify or fix manually?**

- Confirmed Happy Pop with `preferred_mood_tag=euphoric` and `preferred_decade=2020` boosts Sunrise City and Rooftop Lights
- Confirmed Chill Lofi with `likes_instrumental=True` rewards Midnight Coding / Library Rain
- Ran core OOP tests (`Song` / `UserProfile` / `Recommender`) — still pass with defaulted new fields

---

## Design Pattern (SF10) — Challenge 2: Multiple Scoring Modes

**Which design pattern did you use?**

**Strategy pattern** — each scoring mode is a small class that returns a `ScoringWeights` configuration. The recommender picks a strategy by name without changing the scoring loop.

**How did AI help you brainstorm or implement it?**

> Brainstorm a Strategy-pattern design so users can switch between Genre-First, Mood-First, and Energy-Focused modes in main.py without rewriting score_song. Keep the code modular.

The suggestion was to define an abstract `ScoringStrategy` with a `weights()` method, concrete subclasses for each mode, and a registry dict (`SCORING_MODES`) so `main.py` can switch modes with one string.

**How does the pattern appear in your final code?**

- `ScoringStrategy` (ABC) + `BalancedStrategy`, `GenreFirstStrategy`, `MoodFirstStrategy`, `EnergyFocusedStrategy` in `src/recommender.py`
- `SCORING_MODES` registry and `get_strategy(mode)`
- `recommend_songs(..., mode="balanced")` and `ACTIVE_MODE` in `src/main.py`
- Mode comparison demo prints the same Happy Pop profile under all four modes

Observed behavior for Happy Pop:

| Mode | #1 | Notable change |
|------|----|----------------|
| balanced | Sunrise City | Gym Hero #3 |
| genre_first | Sunrise City | Gym Hero rises to #2 (genre +4.0) |
| mood_first | Sunrise City | Rooftop Lights #2; Gym Hero drops to #5 |
| energy_focused | Sunrise City | Bass Drop Nation rises; energy dominates |

---

## Challenge 3: Diversity and Fairness Logic

**Rule implemented:**

While building the top-K list greedily:

- If an artist is already in the selected results → subtract **1.0** (`artist diversity`)
- If a genre is already in the selected results → subtract **0.5** (`genre diversity`)

Implemented in `apply_diversity_penalty()` and enabled by default via `recommend_songs(..., apply_diversity=True)`.

**Manual verification:**

- Chill Lofi: Focus Flow (also by LoRoom) receives `artist diversity (-1.0)` after Midnight Coding is selected, so Library Rain / Spacewalk Thoughts stay higher
- Happy Pop: Gym Hero receives `genre diversity (-0.5)` after Sunrise City (also pop) is selected, which helps Rooftop Lights (indie pop) stay at #2

---

## Challenge 4: Visual Summary Table

**Approach:**

`format_recommendations_table()` uses the `tabulate` library with `tablefmt="grid"` when available, and falls back to a plain ASCII column layout if `tabulate` is not installed. The table always includes Rank, Title, Artist, Genre, Score, and Reasons.

**Dependency:** `tabulate` added to `requirements.txt`.

**Prompt used:**

> Suggest a way to display top recommendations as a formatted table that must include the reasons for each score. Prefer tabulate with an ASCII fallback so the CLI still works without the package.
