import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

GENRE_WEIGHT = 0.35
MOOD_WEIGHT = 0.30
ENERGY_WEIGHT = 0.25
ACOUSTIC_WEIGHT = 0.10

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for a UserProfile, best match first."""
        user_prefs = asdict(user)
        scored = [(song, score_song(user_prefs, asdict(song))[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: (-pair[1], pair[0].id))
        return [song for song, _ in ranked[:max(k, 0)]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation of how one song was scored for a user."""
        score, reasons = score_song(asdict(user), asdict(song))
        return f"Score {score:.4f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting numeric columns to int/float."""
    print(f"Loading songs from {csv_path}...")
    float_fields = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # csv gives every value as a string, so convert the numeric columns
            row["id"] = int(row["id"])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def _normalize_label(value) -> str:
    """Lowercase and trim a genre/mood label so "Pop " matches "pop"."""
    return str(value or "").strip().lower()

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song from 0 to 1 against user preferences and return (score, reasons)."""
    reasons = []
    total = 0.0
    weights_used = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT

    # Genre and mood: exact match (ignoring case and spaces) or nothing
    favorite_genre = _normalize_label(user_prefs.get("favorite_genre"))
    if favorite_genre and _normalize_label(song["genre"]) == favorite_genre:
        total += GENRE_WEIGHT
        reasons.append(f"Genre matches {favorite_genre} (+{GENRE_WEIGHT:.4f})")

    favorite_mood = _normalize_label(user_prefs.get("favorite_mood"))
    if favorite_mood and _normalize_label(song["mood"]) == favorite_mood:
        total += MOOD_WEIGHT
        reasons.append(f"Mood matches {favorite_mood} (+{MOOD_WEIGHT:.4f})")

    # Energy: closer to the target is better, not simply higher
    target_energy = float(user_prefs["target_energy"])
    energy_gap = abs(song["energy"] - target_energy)
    energy_points = ENERGY_WEIGHT * (1 - energy_gap)
    total += energy_points
    reasons.append(
        f"Energy {song['energy']:.2f} is {energy_gap:.2f} from target {target_energy:.2f} (+{energy_points:.4f})"
    )

    # Acousticness: optional; target is 1.0 for acoustic fans, 0.0 otherwise
    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        acoustic_target = 1.0 if likes_acoustic else 0.0
        acoustic_points = ACOUSTIC_WEIGHT * (1 - abs(song["acousticness"] - acoustic_target))
        total += acoustic_points
        weights_used += ACOUSTIC_WEIGHT
        preference = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(
            f"Acousticness {song['acousticness']:.2f} vs {preference} preference (+{acoustic_points:.4f})"
        )
    else:
        reasons.append(f"No acoustic preference, so score is divided by {weights_used:.2f}")

    return total / weights_used, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score (ties: lowest id first), and return the top k."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["id"]))
    return ranked[:max(k, 0)]
