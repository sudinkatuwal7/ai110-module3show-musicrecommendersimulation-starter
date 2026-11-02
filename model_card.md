# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

<!--
Give your model a short, descriptive name.
Example: **VibeFinder 1.0**
-->

**VibeScore 1.0**, a content-based music recommender that scores each song in a 20-song catalog against one listener's taste and returns a ranked top five with explanations. *(You can rename it; the name is only a label.)*

---

## 2. Intended Use  

<!--
Describe what your recommender is designed to do and who it is for.
Prompts:
- What kind of recommendations does it generate
- What assumptions does it make about the user
- Is this for real users or classroom exploration
-->

This recommender suggests songs from a small 20-song catalog that best match one listener's stated taste. It returns a ranked top-5 list, and each song comes with a score and a short explanation.

It assumes the user can describe their taste with one favorite genre, one favorite mood, a target energy level from 0 to 1, and, optionally, whether they prefer acoustic or electronic-sounding music. It is built for **classroom exploration** of how recommenders work, not for real users. The song attributes are hand-assigned estimates, not real audio measurements.

---

## 3. How the Model Works  

<!--
Explain your scoring approach in simple language.
Prompts:
- What features of each song are used (genre, energy, mood, etc.)
- What user preferences are considered
- How does the model turn those into a score
- What changes did you make from the starter logic
Avoid code here. Pretend you are explaining the idea to a friend who does not program.
-->

**What it looks at.** Every song has a genre (like pop or lofi), a mood (like happy or chill), an energy level (calm to intense), and an acousticness level (electronic to acoustic). The listener says which genre and mood they like, how energetic they want the music to be, and, optionally, whether they like an acoustic sound. Tempo, valence and danceability are in the data but are not used yet.

**How a song earns points.** Think of a 1-point scorecard split into four parts:

- **Genre (0.35 points):** full points if the song's genre is the listener's favorite, otherwise nothing. Capital letters and extra spaces are ignored, but the words must match exactly, so "indie pop" does not count as "pop".
- **Mood (0.30 points):** the same idea for mood.
- **Energy (0.25 points):** the closer the song's energy is to the listener's target, the more points it gets. A song that is exactly on target gets all 0.25, and one that is far away gets few. More energy isn't automatically better; *closeness* is what counts.
- **Acoustic sound (0.10 points):** acoustic-sounding songs earn more if the listener likes acoustic music, and electronic-sounding songs earn more if they don't.

Genre and mood are worth the most because together they capture a song's overall vibe. If the listener doesn't say anything about acoustic sound, that part is skipped and the score is scaled back up, so the best possible score is still 1.

**How songs are ranked.** Every song in the catalog gets a score. The songs are then lined up from highest score to lowest, and the top five are recommended. If two songs tie, the one listed earlier in the catalog comes first, so the results are always the same.

**Why it explains itself.** Each recommendation lists the points it earned, for example "Mood matches happy (+0.3000)". The explanation is built from the same numbers as the score, so it never claims a match that didn't happen, and you can see exactly why one song beat another.

**Changes from the starter logic.** The starter code returned the first few songs unscored. Now every song is scored, ranked and explained. The example listener in `src/main.py` was changed to use the same preference names as the `UserProfile` (favorite genre, favorite mood, target energy, likes acoustic). For the Phase 4 experiment, the scoring can also take a different set of weights for a single run. The normal app always uses the four weights above.

---

## 4. Data  

<!--
Describe the dataset the model uses.
Prompts:
- How many songs are in the catalog
- What genres or moods are represented
- Did you add or remove data
- Are there parts of musical taste missing in the dataset
-->

**Size and source.** `data/songs.csv` has **20 songs** by 13 artists. Songs 1–10 came with the starter project and use fictional artists. Songs 11–20 were added in Phase 1: two songs each by J. Cole, Justin Bieber, Michael Jackson, Narayan Gopal and Purna Rai. They were added to bring the catalog up to the required size and to add more genres, more moods, sadder songs, and more mid-energy songs. No songs were removed.

**Columns.** Each song has `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability` and `acousticness`. The model uses only genre, mood, energy and acousticness.

**What's represented.**

| | Values (number of songs) |
|---|---|
| Genres (11) | pop 4, lofi 3, rock 2, hip hop 2, nepali classic 2, nepali folk 2, ambient 1, jazz 1, synthwave 1, indie pop 1, funk 1 |
| Moods (10) | happy 3, chill 3, intense 3, moody 2, reflective 2, sad 2, romantic 2, relaxed 1, focused 1, groovy 1 |
| Ranges | energy 0.25–0.93, acousticness 0.03–0.92, valence 0.18–0.84, tempo 60–152 BPM |

**Important caveat.** All attribute values are **hand-assigned estimates**, not measurements from an audio-analysis service. Values for the real songs were estimated from each song's general style.

**What's missing.**
- Most genres and moods have only one or two songs.
- No song is both sad and high-energy.
- There are no lyrics, language, release year or popularity data.
- There is no listening history from real users, so the model cannot learn taste the way streaming apps do.

---

## 5. Strengths  

<!--
Where does your system seem to work well
Prompts:
- User types for which it gives reasonable results
- Any patterns you think your scoring captures correctly
- Cases where the recommendations matched your intuition
-->

- **It matches clear tastes well.** When the listener's genre and mood both exist in the catalog, the top two results match on genre, mood and energy every time. The scores were 0.966–0.991 for the High-Energy Pop, Chill Lofi Study and Intense Rock Workout profiles (section 7).
- **Weighted features balance several preferences.** Rather than filtering on one rule, each song gets partial credit across four features. A song that misses on genre can still rank well if its mood and energy fit, like *Rooftop Lights* at #4 for the pop profile.
- **Closeness, not "more is better".** Energy is scored by how *near* it is to the target, so a calm listener gets calm songs. All five Chill Lofi picks have energy 0.28–0.42.
- **It always gives a ranked list.** Every song is scored, then sorted from best to worst, so the user always sees an ordered top five.
- **Every recommendation explains itself.** Each result lists the points it earned for each feature. The parts always add up to the score, so anyone can check a ranking by hand (see the Beat It example in section 7).
- **The results are repeatable.** The same profile always gives the same list, and ties are broken by song ID, so results don't change between runs.
- **It's safe to experiment with.** A different set of weights can be tried for one run (the Phase 4 experiment) without changing the default weights. Tests check that the defaults stay at 0.35 / 0.30 / 0.25 / 0.10.

---

## 6. Limitations and Bias 

<!--
Where the system struggles or behaves unfairly.
Prompts:
- Features it does not consider
- Genres or moods that are underrepresented
- Cases where the system overfits to one preference
- Ways the scoring might unintentionally favor some users
-->

The biggest weakness is **genre bias**. A genre match alone is worth 0.35 points, so *Love Yourself*, a slow acoustic ballad (energy 0.38), still made the High-Energy Pop top five just for being pop. In the adversarial profile, two loud, electronic rock songs beat every sad song. **Exact matching** is a second weakness: related moods like `chill`, `relaxed` and `focused` earn nothing for each other, so *Coffee Shop Stories*, a relaxed jazz track that suits studying, came fifth for the lofi profile with no mood credit. **The same artist can take several spots** (Justin Bieber twice in the pop top five, LoRoom twice in the lofi top five). Along with always favoring the same genre, this points toward a filter bubble, although we only saw single runs and did not measure it over time. Finally, the **catalog is tiny and uneven**, and every song attribute is a hand-made estimate rather than a measured value. Rock and intense music have only 3 matching songs, so the rock profile's 4th and 5th picks are happy pop songs chosen on energy alone, and any wrong estimate shifts results.

---

## 7. Evaluation  

<!--
How you checked whether the recommender behaved as expected.
Prompts:
- Which user profiles you tested
- What you looked for in the recommendations
- What surprised you
- Any simple tests or comparisons you ran
No need for numeric metrics unless you created some.
-->

All results below come from running `python -m src.evaluate`, which uses the project's real `score_song()` and `recommend_songs()` on all 20 songs. The output is pasted exactly as printed. Remarks about whether songs "fit" a listener are our own musical judgments, not something the program measures.

### A. Profiles tested

| Profile | Preferences | Top result | Expected? |
|---|---|---|---|
| A: High-Energy Pop | pop, happy, energy 0.80, not acoustic | Sorry (0.9820) | Mostly. #1–2 are upbeat happy pop. #5 Love Yourself (slow ballad) is a surprise. |
| B: Chill Lofi Study | lofi, chill, energy 0.40, acoustic | Library Rain (0.9735) | Yes. All top 5 are calm (energy 0.28–0.42) and acoustic (0.71–0.92). |
| C: Intense Rock Workout | rock, intense, energy 0.90, not acoustic | Beat It (0.9910) | Top 3 yes. #4–5 (happy pop) are filler, because only 3 songs match rock or intense. |
| D: Adversarial | rock, **sad**, energy **0.95**, **acoustic** | Storm Runner (0.6000) | It reveals a weakness, as intended (see below). |

**Profile A output:**

```
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

**Profile B output:**

```
User profile: genre=lofi, mood=chill, target_energy=0.40, likes_acoustic=True

Top 5 recommendations:

1. Library Rain - Paper Lanterns
   Score: 0.9735
   - Genre matches lofi (+0.3500)
   - Mood matches chill (+0.3000)
   - Energy 0.35 is 0.05 from target 0.40 (+0.2375)
   - Acousticness 0.86 vs acoustic preference (+0.0860)

2. Midnight Coding - LoRoom
   Score: 0.9660
   - Genre matches lofi (+0.3500)
   - Mood matches chill (+0.3000)
   - Energy 0.42 is 0.02 from target 0.40 (+0.2450)
   - Acousticness 0.71 vs acoustic preference (+0.0710)

3. Focus Flow - LoRoom
   Score: 0.6780
   - Genre matches lofi (+0.3500)
   - Energy 0.40 is 0.00 from target 0.40 (+0.2500)
   - Acousticness 0.78 vs acoustic preference (+0.0780)

4. Spacewalk Thoughts - Orbit Bloom
   Score: 0.6120
   - Mood matches chill (+0.3000)
   - Energy 0.28 is 0.12 from target 0.40 (+0.2200)
   - Acousticness 0.92 vs acoustic preference (+0.0920)

5. Coffee Shop Stories - Slow Stereo
   Score: 0.3315
   - Energy 0.37 is 0.03 from target 0.40 (+0.2425)
   - Acousticness 0.89 vs acoustic preference (+0.0890)
```

**Profile C output:**

```
User profile: genre=rock, mood=intense, target_energy=0.90, likes_acoustic=False

Top 5 recommendations:

1. Beat It - Michael Jackson
   Score: 0.9910
   - Genre matches rock (+0.3500)
   - Mood matches intense (+0.3000)
   - Energy 0.88 is 0.02 from target 0.90 (+0.2450)
   - Acousticness 0.04 vs non-acoustic preference (+0.0960)

2. Storm Runner - Voltline
   Score: 0.9875
   - Genre matches rock (+0.3500)
   - Mood matches intense (+0.3000)
   - Energy 0.91 is 0.01 from target 0.90 (+0.2475)
   - Acousticness 0.10 vs non-acoustic preference (+0.0900)

3. Gym Hero - Max Pulse
   Score: 0.6375
   - Mood matches intense (+0.3000)
   - Energy 0.93 is 0.03 from target 0.90 (+0.2425)
   - Acousticness 0.05 vs non-acoustic preference (+0.0950)

4. Sunrise City - Neon Echo
   Score: 0.3120
   - Energy 0.82 is 0.08 from target 0.90 (+0.2300)
   - Acousticness 0.18 vs non-acoustic preference (+0.0820)

5. Sorry - Justin Bieber
   Score: 0.3070
   - Energy 0.76 is 0.14 from target 0.90 (+0.2150)
   - Acousticness 0.08 vs non-acoustic preference (+0.0920)
```

**Why profile D is adversarial.** Its preferences contradict the catalog. The sad songs are calm and acoustic (energy 0.25–0.40, acousticness 0.68–0.80). The rock songs are loud and electronic (energy 0.88–0.91, acousticness 0.04–0.10). No song is both rock and sad, so no song can satisfy everything.

```
User profile: genre=rock, mood=sad, target_energy=0.95, likes_acoustic=True

Top 5 recommendations:

1. Storm Runner - Voltline
   Score: 0.6000
   - Genre matches rock (+0.3500)
   - Energy 0.91 is 0.04 from target 0.95 (+0.2400)
   - Acousticness 0.10 vs acoustic preference (+0.0100)

2. Beat It - Michael Jackson
   Score: 0.5865
   - Genre matches rock (+0.3500)
   - Energy 0.88 is 0.07 from target 0.95 (+0.2325)
   - Acousticness 0.04 vs acoustic preference (+0.0040)

3. Sparsha Sangeet - Purna Rai
   Score: 0.4805
   - Mood matches sad (+0.3000)
   - Energy 0.40 is 0.55 from target 0.95 (+0.1125)
   - Acousticness 0.68 vs acoustic preference (+0.0680)

4. Euta Manchhe Ko Maya Le Kati - Narayan Gopal
   Score: 0.4550
   - Mood matches sad (+0.3000)
   - Energy 0.25 is 0.70 from target 0.95 (+0.0750)
   - Acousticness 0.80 vs acoustic preference (+0.0800)

5. Gym Hero - Max Pulse
   Score: 0.2500
   - Energy 0.93 is 0.02 from target 0.95 (+0.2450)
   - Acousticness 0.05 vs acoustic preference (+0.0050)
```

What this shows:

- **Genre beats mood.** The rock songs win because a genre match (0.35) plus close energy (about 0.24) beats a mood match (0.30) plus far-off energy (0.08–0.11).
- **The acoustic preference barely matters.** It added only +0.0100 and +0.0040 to the top two songs.
- **No "no good match" signal.** The best score is only 0.6000, yet the system still returns five songs with confidence. It has no way to say nothing fits well.

### B. Explaining a #1 result: Beat It for profile C

| Component | Calculation | Points |
|---|---|---|
| Genre | rock = rock → 0.35 × 1 | 0.3500 |
| Mood | intense = intense → 0.30 × 1 | 0.3000 |
| Energy | 0.25 × (1 − abs(0.88 − 0.90)) = 0.25 × 0.98 | 0.2450 |
| Acousticness | not acoustic, so target 0.0: 0.10 × (1 − abs(0.04 − 0.0)) = 0.10 × 0.96 | 0.0960 |
| **Total** | 0.3500 + 0.3000 + 0.2450 + 0.0960 (weights sum to 1.0, so no division) | **0.9910** |

Storm Runner has closer energy (0.91 → +0.2475) but is slightly more acoustic (0.10 → +0.0900), so it finishes 0.0035 behind at 0.9875.

### C. Surprises and why they happen

- **Repeated artists.** Justin Bieber has #1 and #5 for profile A, and LoRoom has #2 and #3 for profile B. Nothing in the score looks at artist.
- **Genre match with very different energy.** *Love Yourself* (A, #5) gets 0.35 for being pop even though its energy is 0.42 away from the target and it is very acoustic (+0.0160). That beats any non-pop, non-happy song, because those can earn at most 0.35 (energy + acousticness).
- **Genre match without mood.** *Gym Hero* (A, #3) is pop but `intense`, not `happy`. *Focus Flow* (B, #3) is lofi but `focused`, not `chill`.
- **The same songs in several profiles.** *Gym Hero* appears in the top five for A, C and D, because high energy and low acousticness match all three. *Sunrise City* and *Sorry* appear for both A and C.
- **Exact-match cliffs.** For profile B, scores fall from 0.6120 (#4) to 0.3315 (#5) once no songs are left that match genre or mood. Profile C has the same cliff after #3 (0.6375 → 0.3120).

### D. Pairwise comparisons

1. **High-Energy Pop vs. Chill Lofi Study.** The two top-five lists share no songs. Changing all four preferences at once (genre, mood, energy 0.80 → 0.40, acoustic no → yes) reorders the whole catalog. Pop's #1–3 (Sorry, Sunrise City, Gym Hero) rank #16, #17 and #20 for the lofi listener. The one exception is *Love Yourself*: it is #5 for pop (via genre) and #6 for lofi (via its low energy and high acousticness). That shows energy and acousticness alone can pull a song toward a profile.
2. **High-Energy Pop vs. Intense Rock Workout.** These overlap a lot: *Gym Hero*, *Sunrise City* and *Sorry* appear in both top fives. The two profiles share a high energy target and a non-acoustic preference, so once the genre or mood matches run out, the same energetic, electronic songs fill the list. Only the genre and mood matches (pop/happy vs. rock/intense) decide who is on top.
3. **Chill Lofi Study vs. Intense Rock Workout.** These are complete opposites. Every lofi top-five song ranks #12 or lower for the rock profile (Midnight Coding #12, Focus Flow #14, Coffee Shop Stories #16, Library Rain #17, Spacewalk Thoughts #20). The profiles disagree on every component, so a song that scores high on one scores low on the other.

### E. Weight-shift experiment

- **Original weights:** genre 0.35, mood 0.30, energy 0.25, acousticness 0.10.
- **Experimental weights:** genre halved to 0.175 and energy doubled to 0.50. Mood (0.30) and acousticness (0.10) stay the same. These sum to 1.075, so each score is divided by 1.075, which is the same as dividing each weight by 1.075.
- **How it was run:** the experimental weights were passed to `recommend_songs()` as an optional `weights` argument. The default weights in `src/recommender.py` were never edited, so the normal app was unaffected.
- **Profile used:** A (High-Energy Pop), the main profile. The same change was also applied to the other three profiles for comparison.

```
Weight experiment on profile A: High-Energy Pop
Baseline weights:     {'genre': 0.35, 'mood': 0.3, 'energy': 0.25, 'acoustic': 0.1}
Experimental weights: {'genre': 0.175, 'mood': 0.3, 'energy': 0.5, 'acoustic': 0.1} (sum 1.075, normalized)

Baseline top 5:
  1. Sorry - Justin Bieber  0.9820
  2. Sunrise City - Neon Echo  0.9770
  3. Gym Hero - Max Pulse  0.6625
  4. Rooftop Lights - Indigo Parade  0.6050
  5. Love Yourself - Justin Bieber  0.5110

Experimental top 5 (change vs. baseline rank):
  1. Sunrise City - Neon Echo  0.9740  (was #2)
  2. Sorry - Justin Bieber  0.9740  (was #1)
  3. Rooftop Lights - Indigo Parade  0.7860  (was #4)
  4. Gym Hero - Max Pulse  0.6558  (was #3)
  5. Beat It - Michael Jackson  0.5172  (was #6)

Same weight change applied to every profile (top 5 titles):

  A: High-Energy Pop (changed)
    baseline:     Sorry, Sunrise City, Gym Hero, Rooftop Lights, Love Yourself
    experimental: Sunrise City, Sorry, Rooftop Lights, Gym Hero, Beat It

  B: Chill Lofi Study (changed)
    baseline:     Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories
    experimental: Midnight Coding, Library Rain, Spacewalk Thoughts, Focus Flow, Coffee Shop Stories

  C: Intense Rock Workout (unchanged)
    baseline:     Beat It, Storm Runner, Gym Hero, Sunrise City, Sorry
    experimental: Beat It, Storm Runner, Gym Hero, Sunrise City, Sorry

  D: Adversarial (sad, very high-energy, acoustic rock) (unchanged)
    baseline:     Storm Runner, Beat It, Sparsha Sangeet, Euta Manchhe Ko Maya Le Kati, Gym Hero
    experimental: Storm Runner, Beat It, Sparsha Sangeet, Euta Manchhe Ko Maya Le Kati, Gym Hero
```

**What changed and why (profile A):**

- **Sorry and Sunrise City are now exactly tied.** Each totals 1.047 / 1.075 ≈ 0.9740. Doubling energy rewards Sunrise City's closer energy (0.82 vs. Sorry's 0.76) by the same 0.01 that Sorry gains from lower acousticness. In the program the two totals differ only in the 16th decimal place (floating-point rounding), and that puts Sunrise City first. The ID tie-break would also choose Sunrise City (id 1 vs. 13), so treat this as a tie, not a real preference change.
- **Rooftop Lights #4 → #3, Gym Hero #3 → #4.** Rooftop Lights is happy with energy 0.76, so it doesn't need a genre match. Gym Hero relied on its pop label (now worth only 0.175), and its 0.13 energy gap now costs twice as much.
- **Love Yourself #5 → #9 (0.5110 → 0.4474).** Its genre points were halved and its large energy gap (0.42) now costs double.
- **Beat It #6 → #5.** It matches neither genre nor mood, but its energy (0.88) is close to the target, which now counts for more.
- **Profile B also changed.** Spacewalk Thoughts (mood match only) now beats Focus Flow (genre match only), because mood now outweighs genre. Midnight Coding passes Library Rain because its energy is closer to the target.
- **Profiles C and D did not change.** Their top songs already matched well on energy, so shifting weight toward energy left the order the same.

**What it teaches.** The clear winners (two or more matches plus close energy) barely moved. The middle of the list is sensitive to the weights. The change mainly helped the "high-energy" part of profile A by removing the slow ballad, but it let in *Beat It*, which is neither pop nor happy. That makes it a different trade-off rather than a clear improvement. We kept the original weights as the default because genre and mood still describe a listener's stated taste better than energy alone.

### F. Overall evaluation

- **What it does well.** When a listener's genre and mood exist in the catalog, the top two results are strong matches every time (scores 0.966–0.991 for profiles A–C). Each explanation adds up exactly to its score, so every ranking can be checked by hand.
- **Where it struggles.** It struggles after the exact matches run out (filler with scores around 0.3), with conflicting preferences (profile D), and with repeated artists. It never signals when nothing fits well.
- **Are the weights reasonable?** For this catalog, yes. The experiment showed that halving genre and doubling energy changed only the middle of the lists, and it traded one kind of mismatch for another rather than clearly improving results.
- **What we learned about evaluation.** Testing only "normal" profiles hides problems. The adversarial profile and side-by-side comparisons exposed the genre bias and the lack of a "no good match" signal. A single top-5 list can look sensible while the scores underneath show weak matches.

---

## 8. Future Work  

<!--
Ideas for how you would improve the model next.
Prompts:
- Additional features or preferences
- Better ways to explain recommendations
- Improving diversity among the top results
- Handling more complex user tastes
-->

None of these are implemented. They are possible next steps, each tied to a weakness found in Phase 4.

- **A bigger, more balanced catalog.** Several songs for every genre and mood would mean fewer weak "filler" picks, like the happy pop songs at #4–5 for the rock profile.
- **More reliable song features.** Measured audio features from a trusted source would replace the hand-made estimates.
- **Related moods and genres.** Partial credit for close labels (e.g. `chill` ≈ `relaxed` ≈ `focused`, `indie pop` ≈ `pop`) would stop exact matching from throwing away good matches like *Coffee Shop Stories*.
- **Avoiding repeated artists.** Allowing at most one song per artist in the top five (re-ranking after scoring) would spread out results like Bieber ×2 and LoRoom ×2.
- **Detecting weak matches.** The system could warn when even the best score is low (e.g. 0.60 for the adversarial profile) instead of confidently returning five poor fits.
- **Clear tie handling.** Rounding scores slightly before sorting would let mathematically equal scores fall back to the ID tie-break, instead of tiny floating-point differences deciding the order (seen in the weight experiment).
- **More features and richer tastes.** Valence and tempo could be used, and listeners could give more than one favorite genre or mood.
- **User feedback.** Likes and skips could gradually adjust a listener's profile, which moves toward how real streaming apps learn.

---

## 9. Personal Reflection  

<!--
A few sentences about your experience.
Prompts:
- What you learned about recommender systems
- Something unexpected or interesting you discovered
- How this changed the way you think about music recommendation apps
-->

Throughout this project, the most interesting thing I learned was how recommendation systems can produce biased or unexpected results. Before testing different user profiles, I did not fully realize how much the scoring weights could influence which songs appeared in the recommendations.

One thing that surprised me was how a song could rank highly simply because its genre matched the user's preference, even when its energy level was different. For example, *Love Yourself* appeared in the High-Energy Pop recommendations despite having a lower energy level than the user wanted. This helped me understand that a high similarity score does not always mean a recommendation is a perfect match.

AI helped me test different user profiles and analyze unexpected results. It helped me understand why certain songs ranked higher and how the scoring formula influenced the recommendations.

I also ran the recommender myself and checked its top-five recommendations. Overall, this project helped me understand why recommendation systems need careful evaluation instead of relying only on numerical scores.
