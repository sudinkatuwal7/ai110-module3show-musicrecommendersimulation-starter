# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**This version** is a content-based recommender written in plain Python. It loads a 20-song catalog from `data/songs.csv` and scores every song against one listener's profile (favorite genre, favorite mood, target energy, and optionally whether they like acoustic music). The scoring uses fixed weights: genre 0.35, mood 0.30, energy 0.25, acousticness 0.10. It prints the top five songs, each with a score and a line-by-line explanation of how that score was earned. An evaluation script tests four listener profiles, including a deliberately conflicting one, and runs a weight-change experiment. The [model card](model_card.md) documents what works, what doesn't, and why.

---

## How The System Works

<!--
Instructor prompts for this section (kept for reference):
- What features does each `Song` use in your system (e.g. genre, mood, energy, tempo)
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend
You can include a simple diagram or bullet list if helpful.
-->

> **Status:** Implemented in Phase 3. `score_song()`, `recommend_songs()` and the `Recommender` class follow the design below. The worked examples in this section are hand calculations from the design; real program output is in [Sample Recommendation Output](#sample-recommendation-output).

### Real-world recommenders

Platforms like Spotify and YouTube learn taste from **implicit signals** (plays, repeat listens, listening time, skips) and **explicit signals** (likes, saves, playlist adds), and combine two main approaches:

- **Collaborative filtering** — "people who liked what you liked also liked X." It uses only the user–song interaction history, not what the songs sound like. It finds surprising cross-genre matches but needs many users, and it cannot recommend brand-new songs (the *cold-start* problem).
- **Content-based filtering** — "this song has attributes similar to what you like." It compares song features (genre, mood, energy, acousticness…) to a user's preferences. It works with one user and a small catalog and is easy to explain, but it tends to recommend more of the same.

Production systems are **hybrids**: they quickly narrow millions of tracks down to a few hundred candidates, then a ranking model orders them.

**This simulation is content-based**, because we have one user profile and 20 songs with descriptive attributes but no interaction data from many users.

### Four separate pieces

| Piece | Meaning | In this project |
|---|---|---|
| **Song input features** | Facts about each song; same for every user | `Song` fields from `data/songs.csv` |
| **User preferences** | What this particular user wants | `UserProfile` fields |
| **Scoring rule** | Compares one song to the preferences and returns a number | `score_song()` |
| **Ranking rule** | Scores every song, sorts them, keeps the top *k* | `recommend_songs()` / `Recommender.recommend()` |

### Song features

`data/songs.csv` contains **20 songs** with 10 columns, matching the `Song` dataclass in `src/recommender.py`:

| Field | Type | Used in scoring? |
|---|---|---|
| `id`, `title`, `artist` | identifiers | No (`artist` is used by the optional diversity rule) |
| `genre` | category (11 values, e.g. pop, lofi, hip hop, nepali classic) | **Yes** |
| `mood` | category (10 values, e.g. happy, chill, sad, romantic) | **Yes** |
| `energy` | 0–1 | **Yes** |
| `acousticness` | 0–1 | **Yes** |
| `tempo_bpm`, `valence`, `danceability` | BPM / 0–1 / 0–1 | Not in v1 (candidates for future work) |

> **Data note:** The attribute values are **hand-assigned, illustrative estimates**, not verified Spotify audio-feature measurements. Songs 1–10 come from the starter file (fictional artists). Songs 11–20 were added for this project and include real artists (J. Cole, Justin Bieber, Michael Jackson, Narayan Gopal, Purna Rai), with values estimated from each song's general style.

### User preferences

The `UserProfile` dataclass stores:

| Field | Meaning |
|---|---|
| `favorite_genre` | Genre to match, e.g. `"lofi"` |
| `favorite_mood` | Mood to match, e.g. `"chill"` |
| `target_energy` | Desired energy level from 0 to 1 |
| `likes_acoustic` | `True` = prefers acoustic/organic sound; `False` = prefers electronic/produced |

`src/main.py` passes the same preferences as a dictionary with the same key names (`"favorite_genre"`, `"favorite_mood"`, `"target_energy"`, `"likes_acoustic"`). `"likes_acoustic"` is **optional**. When it is missing, the acoustic part is left out and the remaining weights are renormalized (see *Missing preferences* below).

### Example user profile: chill-lofi study listener

This is the main profile used in the examples below. Its keys match the `UserProfile` fields:

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "likes_acoustic": True,
}
```

| Field | Value | Why |
|---|---|---|
| `favorite_genre` | `"lofi"` | The catalog's study-music genre (3 songs) |
| `favorite_mood` | `"chill"` | Calm, low-stress listening (3 songs) |
| `target_energy` | `0.40` | The middle of the lofi range (0.35–0.42), which averages 0.39 |
| `likes_acoustic` | `True` | Lofi and study music in the catalog are mostly warm and acoustic (0.71–0.86) |

**How it separates chill lofi from intense rock.** The two profiles differ on all four components. They share no genre or mood (worth 0.65 together). Their energy targets differ (0.40 vs. about 0.90), so a rock song with 0.91 energy gets an energy similarity of only 0.49. And their acoustic preferences are opposite. Using a contrast profile `{"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.90, "likes_acoustic": False}`, hand calculations over all 20 songs give:

| Profile | Its top 2 | Where the *other* profile's top 2 land |
|---|---|---|
| chill lofi | Library Rain 0.9735, Midnight Coding 0.9660 | Beat It #18 (0.1340), Storm Runner #19 (0.1325) |
| intense rock | Beat It 0.9910, Storm Runner 0.9875 | Midnight Coding #12 (0.1590), Library Rain #17 (0.1265) |

**AI critique: is the profile too narrow?** Partly, yes. The main findings:

1. **Only 4 of 20 songs get any credit for genre or mood.** Matching is exact, so after rank 4 the score drops from 0.6120 to 0.3315. The 5th recommendation (Coffee Shop Stories) is chosen only on energy and acousticness.
2. **Near-synonym moods earn nothing.** A study listener would probably enjoy `focused` (Focus Flow) or `relaxed` (Coffee Shop Stories) songs, but neither counts as `chill`.
3. **There's only one favorite genre and one favorite mood**, so the profile can't express "lofi *or* ambient."
4. **`target_energy` is not too narrow.** Closeness scoring is gradual, so nearby songs still score well.

**Design adjustments (documentation only; the agreed weights and formulas are unchanged):**

- Keep single-value fields so the profile matches the existing `UserProfile` dataclass.
- Accept that low-ranked results will be weaker matches, and make that visible: explanations list only the parts of the score that actually contributed, so a song with no genre or mood match won't claim one.
- Add *mood families* (e.g. chill ≈ relaxed ≈ focused) to the planned improvements as a fix for point 2.
- Use the intense-rock profile as a contrast case when evaluating the implementation.

### Scoring rule (one song)

```
score = 0.35 * genre_match
      + 0.30 * mood_match
      + 0.25 * energy_similarity
      + 0.10 * acoustic_fit
```

| Component | Weight | Formula (each part is between 0 and 1) |
|---|---|---|
| `genre_match` | 0.35 | 1 if `song.genre == favorite_genre` (case-insensitive), else 0 |
| `mood_match` | 0.30 | 1 if `song.mood == favorite_mood` (case-insensitive), else 0 |
| `energy_similarity` | 0.25 | `1 - abs(song.energy - target_energy)` |
| `acoustic_fit` | 0.10 | `1 - abs(song.acousticness - acoustic_target)`, where `acoustic_target` is 1.0 if `likes_acoustic` else 0.0 |

The weights add up to **1.0**, so every score falls between 0 and 1.

**Missing preferences (renormalization):** if an optional preference is absent (currently only `likes_acoustic`), its component is left out and the score is divided by the sum of the weights that were used:

```
score = (0.35 * genre_match + 0.30 * mood_match + 0.25 * energy_similarity) / 0.90
```

This keeps every score on the same 0–1 scale, so a user with no acoustic preference isn't capped at 0.90. In effect, the weights become genre ≈ 0.389, mood ≈ 0.333 and energy ≈ 0.278.

**Why genre and mood get the most weight:** together they describe a song's overall vibe. Genre sets the sound world (lofi vs. rock), and mood sets the emotional intent (chill vs. intense). Genre is weighted slightly higher because a wrong genre is usually the more jarring mismatch. Energy is the most important continuous dimension (study music vs. workout music). Acousticness is a texture preference, so it acts as a tie-breaker.

**Why closeness instead of "higher is better":** `1 - abs(song_value - target_value)` rewards songs *near* the user's target, not songs with the largest value. Because energy and acousticness are already on a 0–1 scale, the result also stays between 0 and 1. With a target energy of 0.40, a 0.42-energy song scores 0.98, while a 0.93-energy song scores only 0.47, even though it has more energy. For acousticness, the target is 1.0 or 0.0, so the same formula reduces to `acousticness` if the user likes acoustic and `1 - acousticness` if they don't.

Exact matching means `"indie pop"` does **not** count as `"pop"`. This is a known limitation of v1.

### Ranking rule (all songs)

1. Run the scoring rule on every song in the catalog.
2. Sort by score, highest first. Break ties by `id` (lowest first) so results are repeatable.
3. Return the top `k` (default 5).

**Scoring vs. ranking:** *scoring* looks at one song and one user and returns a number; it knows nothing about other songs. *Ranking* uses those numbers to compare the whole catalog and decides which songs to show and in what order. Keeping them separate means the scoring formula can change without touching the ranking step, and rules about the whole list (such as artist diversity) can be added to ranking without touching scoring.

### Algorithm recipe (final)

1. **Load** all songs from `data/songs.csv`.
2. **Read** the user's preferences: `favorite_genre`, `favorite_mood`, `target_energy` and, optionally, `likes_acoustic`.
3. **Score each song:**
   - genre match → 0 or 1
   - mood match → 0 or 1
   - energy similarity → `1 - abs(song.energy - target_energy)`
   - acoustic fit → `1 - abs(song.acousticness - acoustic_target)`, only if `likes_acoustic` is given
   - Weighted sum with genre 0.35, mood 0.30, energy 0.25, acousticness 0.10.
4. **Normalize when needed:** if `likes_acoustic` is missing, divide by 0.90 (the sum of the weights used).
5. **Record reasons** for every component that contributed.
6. **Rank:** sort by score, highest first, with ties broken by lowest `id`.
7. **Return** the top `k` songs, each with its score and explanation.

### Explanations

Each recommendation's explanation comes from the same components that produced its score, so it never claims a reason that didn't count. The scorer records a reason for each component that contributed:

```
Library Rain — score 0.9735
  genre matches "lofi" (+0.3500); mood matches "chill" (+0.3000);
  energy 0.35 is close to your target 0.40 (+0.2375); acousticness 0.86 fits your acoustic preference (+0.0860)
```

*(This example was calculated by hand from the formulas above for the profile lofi / chill / energy 0.40 / `likes_acoustic=True`; it is not program output. 0.3500 + 0.3000 + 0.2375 + 0.0860 = 0.9735. The program uses the same reasons in a slightly different wording, shown in [Sample Recommendation Output](#sample-recommendation-output).)*

### Data flow

```
data/songs.csv ──load_songs()──► CSV song data (Song objects / song dicts)
                                          │
UserProfile / user_prefs dict ────────────┤   user preferences
                                          ▼
        SCORING   score_song(): weighted score + reasons for EACH song
                                          │
                                          ▼
        NORMALIZE divide by the weights used if likes_acoustic is missing
                                          │
                                          ▼
        RANKING   sort all songs by score, highest first (tie → lowest id)
                                          │
                                          ▼
        OUTPUT    top k: (song, score, explanation)
```

### Filter bubbles and diversity

Content-based scoring rewards similarity, so it can trap a user in a **filter bubble**. A hand calculation for the chill-lofi example profile gives this top four:

| Rank | Song | Artist | genre | mood | energy | acoustic | Score |
|---|---|---|---|---|---|---|---|
| 1 | Library Rain | Paper Lanterns | 0.3500 | 0.3000 | 0.2375 | 0.0860 | 0.9735 |
| 2 | Midnight Coding | LoRoom | 0.3500 | 0.3000 | 0.2450 | 0.0710 | 0.9660 |
| 3 | Focus Flow | LoRoom | 0.3500 | 0 | 0.2500 | 0.0780 | 0.6780 |
| 4 | Spacewalk Thoughts | Orbit Bloom | 0 | 0.3000 | 0.2200 | 0.0920 | 0.6120 |

All of the top three are lofi, and two are by the same artist. A planned **artist-diversity rule** would re-rank the sorted list and allow at most one song per artist in the top *k*. If that leaves fewer than *k* songs, the skipped songs fill the remaining slots. In the example, Focus Flow would be replaced in the top three by the next-best song from a different artist, Spacewalk Thoughts (ambient/chill, 0.6120).

*Renormalization example:* if the same user has no acoustic preference, the scores become (0.35 + 0.30 + 0.2450) / 0.90 = 0.9944 for Midnight Coding and (0.35 + 0.30 + 0.2375) / 0.90 = 0.9861 for Library Rain, so the top two swap places. Library Rain's lead came from acousticness alone.

### Potential biases

- **Genre outweighs mood.** With all else equal, a genre-only match always beats a mood-only match. Focus Flow (lofi but `focused`) scores 0.6780, above Spacewalk Thoughts (ambient but `chill`) at 0.6120, even though the profile's mood is chill.
- **Repeating artists.** LoRoom has two of the top three songs for the chill-lofi profile. Seven artists have two songs each, so this can happen for other profiles too.
- **Exact labels exclude close matches.** `indie pop` gets no credit for `pop`, and `relaxed` or `focused` get none for `chill`. Users whose taste falls between labels get weaker results.
- **Uneven catalog.** `pop` has 4 songs, but ambient, jazz, synthwave, indie pop and funk have 1 each, so some users have far fewer strong matches than others.
- **Estimated attributes.** All song values are hand-assigned estimates. If the Nepali songs, or any others, are mis-estimated, those songs are consistently over- or under-recommended.

### Planned improvements

- **Diversity:** the artist-diversity rule above, and possibly a limit per genre.
- **Ranking modes:** for example "strict match" (the default weights), "mood-first", or "discovery" (lower genre weight to cross genres).
- **More features:** valence and normalized tempo; partial genre matches (e.g. `indie pop` ≈ `pop`); mood families (e.g. `chill` ≈ `relaxed` ≈ `focused`).
- **Evaluation:** test profiles with expected top results (e.g. the starter test that the pop/happy song ranks first, and the chill-lofi vs. intense-rock contrast above), plus checks for edge cases such as genres with a single song.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

4. Run the evaluation (four profiles plus the weight experiment):

```bash
python -m src.evaluate
```

Run every command from the project's root folder so the `src` package and `data/songs.csv` are found.

### Running Tests

Run the starter tests with:

```bash
pytest
```

(`python -m pytest` also works and uses the active virtual environment's Python.)

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

Actual output of `python -m src.main` with the default pop/happy profile:

```
Loading songs from data/songs.csv...
Loaded 20 songs

User profile: genre=pop, mood=happy, target_energy=0.80, likes_acoustic=False

Top 5 recommendations:

1. Sorry - Justin Bieber
   Score: 0.9820
   - Genre matches pop (+0.3500)
   - Mood matches happy (+0.3000)
   - Energy 0.76 is 0.04 from target 0.80 (+0.2400)
   - Acousticness 0.08 vs non-acoustic preference (+0.0920)

2. Sunrise City - Neon Echo
   Score: 0.9770
   - Genre matches pop (+0.3500)
   - Mood matches happy (+0.3000)
   - Energy 0.82 is 0.02 from target 0.80 (+0.2450)
   - Acousticness 0.18 vs non-acoustic preference (+0.0820)

3. Gym Hero - Max Pulse
   Score: 0.6625
   - Genre matches pop (+0.3500)
   - Energy 0.93 is 0.13 from target 0.80 (+0.2175)
   - Acousticness 0.05 vs non-acoustic preference (+0.0950)

4. Rooftop Lights - Indigo Parade
   Score: 0.6050
   - Mood matches happy (+0.3000)
   - Energy 0.76 is 0.04 from target 0.80 (+0.2400)
   - Acousticness 0.35 vs non-acoustic preference (+0.0650)

5. Love Yourself - Justin Bieber
   Score: 0.5110
   - Genre matches pop (+0.3500)
   - Energy 0.38 is 0.42 from target 0.80 (+0.1450)
   - Acousticness 0.84 vs non-acoustic preference (+0.0160)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

Run the full Phase 4 evaluation with:

```bash
python -m src.evaluate
```

It runs four profiles (High-Energy Pop, Chill Lofi Study, Intense Rock Workout, and a deliberately conflicting "sad, very high-energy, acoustic rock" profile), then repeats them with experimental weights. The default app (`python -m src.main`) is unaffected. Full outputs and analysis are in [model_card.md, section 7](model_card.md#7-evaluation). Key findings:

- **Different users get very different lists.** Chill Lofi and Intense Rock share no top-five songs. High-Energy Pop and Intense Rock share three (Gym Hero, Sunrise City, Sorry), because both want energetic, non-acoustic music.
- **Weight shift (genre 0.35 → 0.175, energy 0.25 → 0.50, normalized by 1.075):**
  - High-Energy Pop: the slow ballad *Love Yourself* dropped from #5 to #9, and *Beat It* entered at #5. Sorry and Sunrise City became an exact tie for #1.
  - Chill Lofi: the mood-only match now beats the genre-only match.
  - Intense Rock and the conflicting profile: their top fives didn't change.
  - The default weights were kept.
- **The conflicting profile exposed genre bias.** Two loud, electronic rock songs ranked above every sad song, even though the user asked for sad, acoustic music.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

Limitations of this recommender, all observed in the Phase 4 evaluation (details in [model_card.md, section 6](model_card.md#6-limitations-and-bias)):

- **Genre bias:** a genre match alone is worth 0.35, so a slow ballad made the high-energy pop top five, and loud rock beat every sad song for a "sad acoustic rock" listener.
- **Exact matching:** related moods (`chill` / `relaxed` / `focused`) and genres (`indie pop` / `pop`) get no credit for each other.
- **Repeated artists:** nothing stops one artist from filling several spots in the top five.
- **Tiny, estimated catalog:** 20 songs with hand-assigned attributes. Once the real matches run out, the remaining picks are weak filler.
- **No "nothing fits" warning:** the system returns five songs even when the best score is low.
- **No understanding of lyrics or language:** it only sees the four numeric and label features.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

The most interesting thing I learned from this project was how recommendation systems can produce biased or unexpected results. I was surprised that a song could rank highly because its genre matched, even when its energy level was not what the user wanted. This showed me how much the scoring weights influence recommendations.

AI helped me test different user profiles and understand unexpected results. I also ran the recommender myself and checked its top-five recommendations. This project taught me that recommendation systems need both a scoring algorithm and proper evaluation to produce useful results.



