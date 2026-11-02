# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

---

## Phase 1 Design Session (Claude Code)

> A summary of AI-assisted work during Phase 1: research, dataset expansion, feature selection, and scoring design.

**Tool:** Claude Code (VS Code extension), working in this repository.

**Prompts (summarized):**

1. Explain how Spotify and YouTube recommend music using listening history, likes, skips, playlists and song attributes. Compare collaborative and content-based filtering, and say which suits a beginner Python project. Do not modify files.
2. Analyze `data/songs.csv`: columns, feature meanings, song count, missing or invalid values, the most useful features, and whether the dataset meets the 15–20 song requirement. Do not modify files.
3. Propose 10 more songs (J. Cole, Justin Bieber, Michael Jackson, Purna Rai, Narayan Gopal) to improve genre, mood, low-valence and energy coverage, and wait for approval before editing.
4. Complete Phase 1 Step 3 (algorithm recipe) and Step 4 (README documentation), plus this log. Do not implement code.
5. Finalize Phase 1: keep the weights, renormalize weights when optional preferences are missing, fix arithmetic in the hand-calculated examples, and make small documentation corrections without another review cycle.

**Recommendations and decisions:**

- **Approach:** content-based weighted scoring rather than collaborative filtering, because there is one user, a small catalog and no interaction data. *Accepted.*
- **Dataset analysis:** the original file had 10 songs with no missing or invalid values. Claude flagged that this was below the 15–20 song requirement, that `"indie pop"` ≠ `"pop"` under exact matching, that `tempo_bpm` is on a different scale, that several genres and moods had only one song, and that valence was narrow (0.48–0.84).
- **Dataset expansion:** Claude proposed rows 11–20 with estimated attribute values. It did not supply Purna Rai song titles because it was not confident of them, and used placeholders instead. *Revised by the student:* the student supplied the titles "Kalo Seto" and "Sparsha Sangeet" and kept the proposed numeric values. Claude then appended the 10 rows. The values for all 10 added songs are estimates, not measured audio features.
- **Scoring design:** weights of genre 0.35, mood 0.30, energy 0.25 and acousticness 0.10 (sum 1.0), closeness scoring `1 - abs(song - target)`, and an acoustic target of 1.0 or 0.0 derived from `likes_acoustic`. Ranking sorts by score with ties broken by `id`, then takes the top k. Explanations are built from the scoring components. An artist-diversity rule (at most one song per artist) is planned as an improvement. *Accepted by the student,* who kept the weights unchanged in the final Phase 1 request.
- **Feature selection:** the scoring uses genre, mood, energy and acousticness, matching the existing `UserProfile` fields. `tempo_bpm`, `valence` and `danceability` were left for future work (tempo would need normalization). *Accepted.*
- **Missing preferences:** the first draft simply skipped the acoustic part when `likes_acoustic` was missing, which capped scores at 0.90. *Revised at the student's request:* the remaining weights are now renormalized (the score is divided by 0.90) so scores stay on a 0–1 scale.
- **Arithmetic fix:** the first README draft showed component values rounded to two decimals that didn't add up to the totals (e.g. Library Rain's parts summed to 0.98 while its total was listed as 0.97). The examples now use exact four-decimal values that add up.

**What was checked (by Claude, using Python's `csv` module in the terminal):**

- `data/songs.csv` has 20 data rows and the 10 expected columns, with IDs 1–20, no blank values, and all 0–1 features within range.
- Running `python -m src.main` currently fails with `ModuleNotFoundError: No module named 'recommender'` (the import in `src/main.py`). This was not fixed, because Phase 1 excludes source changes.
- The worked score examples in README.md are hand calculations from the proposed formula, not program output; the recommender is not implemented yet. To check the arithmetic, Claude recomputed the example scores with a one-off Python expression in the terminal (not saved to the repository) over all 20 songs. This also confirmed the example's rank order, with and without the acoustic preference.

**What I verified manually:**

I reviewed the selected song features, user preferences, and weighted scoring design. I confirmed that the recommendation approach matches my understanding of content-based filtering. I also reviewed the README explanation and the distinction between scoring individual songs and ranking the complete dataset.

**Files changed:** `data/songs.csv` (10 rows appended), `README.md` ("How The System Works" section, plus a closing code fence added to the unclosed Setup code block), `ai_interactions.md` (this section). No Python source, test or requirements files were modified.

---

## Phase 2 Design Session (Claude Code)

> A record of AI-assisted work during Phase 2: confirming the dataset, designing the user profile, finalizing the scoring and data flow, and documenting biases.

**Prompt (summarized):** Complete Phase 2 Steps 1–5 in one pass: confirm the 20-song dataset, design a chill-lofi study profile that matches the `UserProfile` fields, get and record an AI critique of whether the profile is too narrow, keep the agreed weights, formula and renormalization, finalize the algorithm recipe and data flow in README.md, and document at least one realistic bias. Do not modify source, tests or requirements; do not fix the `src/main.py` import yet.

**Dataset (Step 1):** Claude confirmed `data/songs.csv` is unchanged since Phase 1: 20 rows, IDs 1–20, 10 columns, no blank values, no duplicate titles, 11 genres and 10 moods. No songs were added.

**User profile (Step 2):** Claude proposed `{"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.40, "likes_acoustic": True}`, using the `UserProfile` field names.
- It first tried `target_energy` 0.38, then chose 0.40. The two produce the same top four songs, 0.40 sits in the middle of the lofi range (average 0.39), and it keeps the Phase 1 worked examples valid.
- To show the profile separates chill lofi from intense rock, Claude compared it with a contrast profile (rock / intense / 0.90 / `likes_acoustic=False`).

**AI critique of the profile (by Claude):** The profile is partly too narrow.
- Exact matching gives genre or mood credit to only 4 of 20 songs, so scores drop from 0.6120 at rank 4 to 0.3315 at rank 5.
- Near-synonym moods (`focused`, `relaxed`) get no credit for `chill`.
- A single favorite genre and mood can't express mixed tastes.
- `target_energy` is not too narrow, because closeness scoring is gradual.

**Decisions:**
- Weights (0.35 / 0.30 / 0.25 / 0.10), the `1 - abs(song_value - target_value)` formula and renormalization were kept unchanged, as the student required.
- In response to the critique, nothing in the code or scoring was changed. Claude documented the narrowness, noted that explanations make weak matches visible, added *mood families* to planned improvements, and added the intense-rock profile as an evaluation contrast.
- README.md gained an example-profile section with the critique, a scoring vs. ranking explanation, a final algorithm recipe, an updated data-flow diagram (scoring → normalize → ranking → output), and a "Potential biases" list (genre outweighing mood, repeating artists, exact labels, uneven catalog, estimated attributes).
- Claude also removed a leftover duplicated table header in the filter-bubble table.

**What was checked (by Claude, in the terminal):**
- Dataset validity, using Python's `csv` module (results above).
- All 20 songs were scored by hand for the chill-lofi profile (with and without `likes_acoustic`) and the intense-rock profile, using one-off Python expressions not saved to the repository. Every score and rank in the README comes from these calculations; they are not output from the project's code, which is not implemented yet.
- `git diff --stat` confirmed that `src/`, `tests/` and `requirements.txt` are unmodified.

**What I verified manually:**

I reviewed the chill-lofi user profile and compared it conceptually with an intense-rock profile. I confirmed that the selected preferences and scoring weights are appropriate for the planned recommender. I also reviewed the dataset expansion and documented the limitations of exact genre and mood matching.

**Files changed:** `README.md` ("How The System Works" section), `ai_interactions.md` (this section). No Python source, test, requirements or data files were modified in Phase 2.

---

## Phase 3 Implementation Session (Claude Code)

> A record of AI-assisted implementation in Phase 3: loading data, scoring, ranking, the CLI, tests and documentation.

**Prompts (summarized):**
1. *Step 1:* Implement `load_songs()` with the `csv` module, convert numeric fields, fix the `ModuleNotFoundError` in `src/main.py`, run `python -m src.main` and report the actual output.
2. *Steps 2–5:* Implement `score_song()` and `recommend_songs()` following the README design, update `src/main.py` to use the `UserProfile` key names and print the top 5 with explanations, paste real CLI output into the README, add docstrings, update the model card (algorithm only), add focused tests, and suggest a commit message without committing.

**What was generated or changed:**
- `src/recommender.py`
  - `load_songs()` reads the CSV with `csv.DictReader` and converts `id` to `int` and the five numeric columns to `float`.
  - New weight constants (0.35 / 0.30 / 0.25 / 0.10).
  - A small `_normalize_label()` helper so matching ignores case and whitespace.
  - `score_song()` returns `(score, reasons)`.
  - `recommend_songs()` returns the top k as `(song, score, explanation)`.
  - `Recommender.recommend()` and `explain_recommendation()` now reuse `score_song()` instead of being starter stubs.
- `src/main.py`
  - The import is now `from src.recommender import ...`.
  - It prints the number of songs loaded.
  - It uses the profile `{"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.80, "likes_acoustic": False}`.
  - It prints rank, title, artist, score and reasons for each recommendation.
- `tests/test_recommender.py`: 16 new tests. The 2 starter tests are unchanged.
- `README.md`: real CLI output in "Sample Recommendation Output", plus updated status and key-name notes in "How The System Works".
- `model_card.md`: sections 2 (Intended Use) and 3 (How the Model Works). The instructor prompts are kept as HTML comments.

**Design decisions preserved:** weights 0.35 / 0.30 / 0.25 / 0.10; `1 - abs(song_value - target_value)` for energy; an acoustic target of 1.0 or 0.0 from `likes_acoustic`; dividing by 0.90 when `likes_acoustic` is missing; sorting by score, highest first, with ties broken by lowest `id`; explanations built from the same components as the score; exact matching of genre and mood labels, ignoring case and whitespace. No diversity rule, ranking modes or extra features were added.

**Problems encountered and how they were resolved:**
- **The `ModuleNotFoundError`.** `python -m src.main` failed because `src/main.py` used `from recommender import ...`. The import was changed to `from src.recommender import ...`, which matches the tests.
- **Rounding in the displayed reasons.** In the first CLI run, contributions shown to 3 decimals didn't always add up to the shown score (Gym Hero: parts 0.350 + 0.217 + 0.095 vs. score 0.663, because 0.2175 rounded down). Display was changed to 4 decimals; scores are still calculated at full precision.
- **The starter sorting test passed by coincidence.** Before Phase 3 it passed only because the stub returned the songs in their original order. It now runs against real scoring.

**Commands and tests actually run (by Claude):**
- `python -m src.main`: exit code 0, 20 songs loaded, 5 recommendations printed. The output in README.md is copied from this run.
- `python -m pytest -q`: 18 passed, 0 failed.
- A one-off Python check confirmed that `recommend_songs()` reproduces the README's hand-calculated chill-lofi scores (0.9735, 0.9660, 0.6780, 0.6120, and 0.9944 / 0.9861 without the acoustic preference).

**Observations noted, not evaluated (that is Phase 4):** in the default pop/happy run, Justin Bieber appears twice in the top 5. Love Yourself (a low-energy, acoustic ballad) ranks 5th mainly because of its genre match. Both match biases already listed in the README.

**What I verified manually:**

I reviewed the terminal output from `python -m src.main` and confirmed that the program loaded 20 songs and displayed five ranked recommendations. I checked that the highest-scoring songs appeared first and that the recommendations matched the pop/happy user profile. I also reviewed the reported test results of 18 passed tests.

**Files changed in Phase 3:** `src/recommender.py`, `src/main.py`, `tests/test_recommender.py`, `README.md`, `model_card.md`, `ai_interactions.md`. `data/songs.csv` and `requirements.txt` were not changed in Phase 3.

---

## Phase 4 Evaluation Session (Claude Code)

> A record of AI-assisted evaluation in Phase 4: stress-testing profiles, analyzing rankings, a weight-shift experiment, and documenting bias.

**Prompt (summarized):** Complete Phase 4 Steps 1–5 in one pass:
- Run three main profiles (High-Energy Pop, Chill Lofi Study, Intense Rock Workout) plus an adversarial profile through the real recommender.
- Analyze accuracy and surprises, and explain a #1 result mathematically.
- Run one weight experiment (genre 0.175, energy 0.50, normalized by 1.075) without permanently changing the default weights.
- Complete the model card's Limitations and Bias and Evaluation sections from actual output.
- Do not start Phase 5, add bonus features, or commit.

**How AI helped design the profiles:** Profiles A–C were given in the prompt. Claude used the suggested adversarial profile (rock / sad / energy 0.95 / acoustic) and explained from the dataset why it conflicts: the catalog's sad songs are calm and acoustic, its rock songs are loud and electronic, and no song is both rock and sad.

**How AI helped analyze the rankings:**
- Claude ran all profiles through `recommend_songs()` and checked each observation against the output and `data/songs.csv`.
- It identified repeated artists, genre-only matches, the score "cliffs" once exact matches run out, songs shared across profiles, and the cross-profile ranks used in the pairwise comparisons (from full 20-song rankings).
- It explained Beat It's #1 score for profile C component by component (0.3500 + 0.3000 + 0.2450 + 0.0960 = 0.9910).

**How the weight experiment was run:**
- `score_song()` and `recommend_songs()` gained an optional `weights` argument. When it is omitted, they use `DEFAULT_WEIGHTS` (0.35 / 0.30 / 0.25 / 0.10), so the normal app is unchanged.
- The experimental weights are passed only by the new `src/evaluate.py`. They are normalized automatically, because the score is already divided by the sum of the weights used.
- Profile A was the main experiment profile; the same change was also applied to profiles B–D for comparison.

**Commands actually run (by Claude):**
- `python -m src.evaluate`: exit code 0. The model card's code blocks were copied directly from this run's saved output by a script, not retyped.
- `python -m src.main`: exit code 0. Its output was compared with the README's Phase 3 sample and is identical apart from line endings.
- `python -m pytest -q`: 23 passed, 0 failed (18 existing and 5 new).
- One-off Python checks (not saved to the repository) to get exact tie values, full 20-song rankings for the pairwise comparisons, and the new rank of Love Yourself under the experiment.

**Code and documentation changes:**
- `src/recommender.py`:
  - Added `DEFAULT_WEIGHTS` and an optional `weights` argument to `score_song()` and `recommend_songs()`.
  - Added a "Total divided by …" reason, shown only when custom weights don't sum to 1.
  - Default scoring is unchanged.
- `src/main.py`: the printing code was moved into `print_recommendations()` so `src/evaluate.py` can reuse it. The output is unchanged.
- `src/evaluate.py` (new): the Phase 4 evaluation runner.
- `tests/test_recommender.py`: 5 new tests. They check that the default weights are unchanged, that passing the defaults explicitly gives identical results, that custom weights are normalized, that a perfect match still scores 1.0, and that an experiment run doesn't affect later default runs. No existing tests were changed.
- `model_card.md`: sections 6 (Limitations and Bias) and 7 (Evaluation). The instructor prompts are kept as HTML comments.
- `README.md`: a short "Experiments You Tried" summary with how to run the evaluation.

**Problems encountered and how they were resolved:**
- **An apparent swap that was really a tie.** The experiment seemed to swap Sorry and Sunrise City at #1. Checking exact values showed both total 1.047 / 1.075, differing only by floating-point rounding (0.9739534883720932 vs. 0.973953488372093). It is documented as a tie, not a genuine ranking change.
- **A false diff.** The first comparison of `python -m src.main` against the README sample reported every line as different. The cause was Windows line endings in README.md. With line endings ignored, the outputs are identical.

**Decisions:**
- *Accepted:* passing weights as an argument instead of editing the weight constants, so the default recommender stays stable.
- *Accepted:* keeping the original weights after the experiment, because the change traded one mismatch for another rather than clearly improving results.
- *Not done (out of scope):* fixing the ties caused by floating-point rounding, a "no good match" signal, mood families, and an artist-diversity rule. These are noted in the model card as weaknesses only.

**What I verified manually:**

I reviewed the recommendation results for the High-Energy Pop, Chill Lofi Study, and Intense Rock Workout profiles. I compared the rankings and observed how the recommendations changed when the scoring weights were adjusted. I also reviewed the reported test results and confirmed that the evaluation identified limitations such as repeated artists, genre bias, and weak matches.

---

## Phase 5 Reflection and Model Card Session (Claude Code)

> A record of AI-assisted documentation work in Phase 5.

**Prompt (summarized):** Complete Phase 5 only:
- Finish the unfinished model card sections and write Strengths and Future Work from the actual implementation and evaluation.
- Prepare a personal reflection *template* with placeholders, not an invented reflection.
- Make sure README.md covers purpose, setup, running the app, the evaluation and the tests.
- Add this log entry and run the final verification.
- Do not change code, scoring or data; do not commit.

**What AI generated or changed:**
- `model_card.md`
  - Filled section 1 (Model Name: "VibeScore 1.0", marked as renamable), section 4 (Data, with genre and mood counts and value ranges recomputed from `data/songs.csv`), section 5 (Strengths), section 8 (Future Work, every item described as not implemented) and section 9 (a labeled reflection template).
  - Added one sentence to section 3 about running the experiment with different weights.
  - Sections 2, 6 and 7 (including all Phase 4 outputs) were not changed. The instructor prompts are kept as HTML comments.
- `README.md`
  - Replaced the Project Summary placeholder.
  - Added a step for `python -m src.evaluate` and a note about `python -m pytest`.
  - Filled "Limitations and Risks" with the Phase 4 findings.
  - Added a clearly marked student placeholder under "Reflection".
  - The Phase 3 sample output and the Phase 4 experiment summary were not changed.

**Decisions:**
- *The personal reflection was not written by AI.* Claude first added a template with project facts and bracketed prompts. The student then wrote their own reflection for model card section 9 and the README Reflection. Claude pasted those texts in word for word, replacing the template.
- *Strengths and Future Work were based only on observed evidence.* Each strength cites a Phase 3 or 4 result. Each future idea is tied to a weakness found in Phase 4 and is described as a possibility.
- *The model name was a suggestion only.* The student can rename it.
- *No code, tests, data or weights were changed in Phase 5.*

**Commands actually run (by Claude):**
- A dataset recount with `load_songs()`: 20 songs, 13 artists, 11 genres, 10 moods. The ranges were used in model card section 4.
- `python -m pytest`, `python -m src.main` and `python -m src.evaluate` (results are in the final verification below).
- A script checked that every Phase 4 output block in model_card.md still matches a fresh run of `python -m src.evaluate`.
- `git diff` was reviewed to confirm no earlier-phase content was removed.

**What I verified manually:**

I personally ran the music recommender and reviewed its top-five recommendations. I checked the ranking order and looked at how the recommended songs matched the selected user preferences. I also considered the unexpected results identified during the evaluation, especially how genre matching could influence rankings even when energy levels differed.
