# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation for classroom exploration.

---

## 2. Intended Use

**Designed for:** Demonstrating how song attributes and user taste profiles combine into ranked recommendations. Useful for learning how scoring rules, ranking logic, and explainable AI work in recommendation systems.

**Assumptions:** The user can describe their taste using a single genre, a single mood, and a target energy level. The catalog is small and every song has complete feature data.

**Not for:** Real-world music discovery, commercial deployment, or users with complex or evolving tastes. This is an educational simulation, not a Spotify replacement.

---

## 3. How the Model Works

VibeFinder scores each song in the catalog against a user's taste profile, then returns the highest-scoring tracks.

**Song features used:** genre, mood, energy, acousticness (bonus only).

**User preferences used:** favorite genre, favorite mood, target energy, optional acoustic preference.

**Scoring rules (plain language):**

1. If the song's genre matches the user's favorite genre → +2 points.
2. If the song's mood matches the user's favorite mood → +1 point.
3. Energy similarity → up to +1.5 points, based on how close the song's energy is to the user's target (closer = more points).
4. If the user likes acoustic music and the song is acoustic → +0.5 bonus.

**Ranking:** Every song gets a total score. The system sorts all songs from highest to lowest and returns the top 5 (or any *K* you choose). Each recommendation includes a list of reasons so you can see exactly why it was suggested.

---

## 4. Data

- **Catalog size:** 18 songs (10 starter + 8 added).
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, edm, classical, hip-hop, country, reggae, metal, folk, r&b.
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, euphoric, peaceful, confident, nostalgic, aggressive, warm, sensual.
- **Numerical features:** energy, tempo_bpm, valence, danceability, acousticness (all on 0.0–1.0 except tempo).
- **Data added:** 8 new songs to improve genre and mood diversity.
- **Missing from data:** Lyrics, language, artist popularity, release year, user listening history, and regional/cultural context.

---

## 5. Strengths

- **Transparent explanations:** Every recommendation lists exactly which rules fired (e.g., "genre match (+2.0)").
- **Works for new users:** No listening history needed — just a taste profile.
- **Differentiates clear vibes:** Chill Lofi and Gym EDM profiles produce distinctly different top-5 lists.
- **Chill Lofi profile** correctly surfaces Midnight Coding and Library Rain (genre + mood + acoustic bonus).
- **Gym EDM profile** correctly puts Bass Drop Nation at #1 (genre + mood + high energy).

---

## 6. Limitations and Bias

- **Genre over-weighting:** At +2.0, genre is the strongest signal. Gym Hero (pop, intense) outranks Rooftop Lights (indie pop, happy) for a "Happy Pop" user, even though Rooftop Lights has the right mood.
- **Exact string matching:** "indie pop" ≠ "pop," so related genres are treated as completely different.
- **No sad-pop in catalog:** The adversarial profile (pop + sad + high energy) cannot find a true match. Gym Hero wins on genre + energy alone, creating a misleading "recommendation."
- **Filter bubble:** Users who always pick "pop" will only see pop songs at the top, never discovering jazz, folk, or classical tracks that might match their mood.
- **Energy gap blind spot:** Two songs equally close in energy score the same, even if one is a better overall fit.

---

## 7. Evaluation

### Profiles Tested

| Profile | Genre | Mood | Energy |
|---------|-------|------|--------|
| Happy Pop | pop | happy | 0.8 |
| Chill Lofi | lofi | chill | 0.4 |
| Deep Intense Rock | rock | intense | 0.9 |
| Gym EDM | edm | euphoric | 0.95 |
| Conflicting | pop | sad | 0.9 |

### Sample Outputs

**Chill Lofi:**

```
Rank  Title                       Score   Reasons
------------------------------------------------------------
1     Midnight Coding             4.97    genre match (+2.0); mood match (+1.0); energy similarity (1.47); acoustic preference (+0.5)
2     Library Rain                4.92    genre match (+2.0); mood match (+1.0); energy similarity (1.42); acoustic preference (+0.5)
3     Focus Flow                  4.00    genre match (+2.0); energy similarity (1.50); acoustic preference (+0.5)
4     Spacewalk Thoughts          2.82    mood match (+1.0); energy similarity (1.32); acoustic preference (+0.5)
5     Coffee Shop Stories         1.96    energy similarity (1.46); acoustic preference (+0.5)
```

**Deep Intense Rock:**

```
Rank  Title                       Score   Reasons
------------------------------------------------------------
1     Storm Runner                4.48    genre match (+2.0); mood match (+1.0); energy similarity (1.48)
2     Gym Hero                    2.46    mood match (+1.0); energy similarity (1.46)
3     Bass Drop Nation            1.41    energy similarity (1.41)
4     Iron Forge                  1.40    energy similarity (1.40)
5     Sunrise City                1.38    energy similarity (1.38)
```

**Gym EDM:**

```
Rank  Title                       Score   Reasons
------------------------------------------------------------
1     Bass Drop Nation            4.48    genre match (+2.0); mood match (+1.0); energy similarity (1.48)
2     Gym Hero                    1.47    energy similarity (1.47)
3     Iron Forge                  1.47    energy similarity (1.47)
4     Storm Runner                1.44    energy similarity (1.44)
5     Sunrise City                1.30    energy similarity (1.30)
```

**Conflicting (high energy + sad mood):**

```
Rank  Title                       Score   Reasons
------------------------------------------------------------
1     Gym Hero                    3.46    genre match (+2.0); energy similarity (1.46)
2     Sunrise City                3.38    genre match (+2.0); energy similarity (1.38)
3     Storm Runner                1.48    energy similarity (1.48)
4     Bass Drop Nation            1.41    energy similarity (1.41)
5     Iron Forge                  1.40    energy similarity (1.40)
```

### Profile Comparisons

**Happy Pop vs. Chill Lofi:** Happy Pop surfaces Sunrise City (pop + happy + high energy). Chill Lofi surfaces Midnight Coding and Library Rain (lofi + chill + low energy + acoustic). The genre and mood weights successfully separate upbeat pop from relaxed study music.

**Deep Intense Rock vs. Gym EDM:** Both want high energy, but rock/intense picks Storm Runner while edm/euphoric picks Bass Drop Nation. After the #1 pick, both lists fill with high-energy songs from other genres — showing that energy similarity alone cannot distinguish subcultures.

**Happy Pop vs. Conflicting:** The conflicting profile removes the mood bonus entirely (no sad songs exist). Gym Hero — an intense workout pop track — ranks #1 instead of a calm happy song. This proves the system can be "tricked" when the catalog lacks songs matching all preferences.

### Weight-Shift Experiment

Doubling energy weight (1.5 → 3.0) and halving genre weight (2.0 → 1.0) moved Rooftop Lights from #3 to #2 for Happy Pop, because its energy (0.76) is closer to the target (0.8) than Gym Hero's (0.93). The change made rankings more energy-driven but did not fix the genre-over-weighting problem.

### Surprises

- Gym Hero appears in almost every high-energy profile, even when mood does not match.
- The adversarial "sad pop" profile cannot fail gracefully — it recommends intense workout music instead.
- Chill Lofi results felt the most "correct" because the catalog has strong lofi/chill representation.

---

## 8. Future Work

1. **Use valence and danceability** in scoring to better capture "happy" vs. "sad" when mood tags are missing.
2. **Fuzzy genre matching** — treat "indie pop" as partially matching "pop."
3. **Diversity penalty** — reduce scores for songs whose artist or genre already appears in the top results, to prevent filter bubbles.
4. **Collaborative filtering layer** — blend content scores with "users like you also liked" signals.
5. **Expand the catalog** to at least 100 songs with balanced genre representation.

---

## 9. Personal Reflection

**Biggest learning moment:** Tracing why Gym Hero ranked #1 for the "sad pop" profile. I expected the system to return nothing useful, but instead it confidently recommended workout music because genre (+2.0) and energy similarity overpowered the missing mood match. That showed me how explainable scoring can reveal bugs that a black-box system would hide.

**Using AI tools:** AI helped brainstorm the algorithm recipe, generate diverse songs for the CSV, and structure the ranking logic. I still had to verify every result manually — the adversarial profile was a case where the math was "correct" but the recommendation was wrong for the user. Human judgment remains essential.

**Simple algorithms that feel real:** When Chill Lofi returned Midnight Coding with a perfect explanation ("genre match, mood match, acoustic preference"), it genuinely felt like a personalized suggestion — even though it is just addition and sorting. That helped me appreciate why Spotify starts with simple signals before adding complexity.

**What I would try next:** Add a diversity penalty so the top 5 is not dominated by one artist (Neon Echo appears twice in some mental rankings), and incorporate valence so "happy" and "sad" can be distinguished numerically even when mood tags do not match exactly.
