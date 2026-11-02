# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

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

**Changes from the starter logic.** The starter code returned the first few songs unscored. Now every song is scored, ranked and explained. The example listener in `src/main.py` was changed to use the same preference names as the `UserProfile` (favorite genre, favorite mood, target energy, likes acoustic).

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
