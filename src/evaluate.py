"""
Phase 4 evaluation runner for the Music Recommender Simulation.

Runs several user profiles through the recommender, then repeats one profile
with experimental weights. The experimental weights are passed in as an
argument, so the default scoring used by src/main.py is never changed.

Run with: python -m src.evaluate
"""

from src.main import print_recommendations
from src.recommender import DEFAULT_WEIGHTS, load_songs, recommend_songs

PROFILES = {
    "A: High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    },
    "B: Chill Lofi Study": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "C: Intense Rock Workout": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    # Conflicting on purpose: sad songs in the catalog are calm and acoustic,
    # rock songs are loud and electronic, and no song is both rock and sad.
    "D: Adversarial (sad, very high-energy, acoustic rock)": {
        "favorite_genre": "rock",
        "favorite_mood": "sad",
        "target_energy": 0.95,
        "likes_acoustic": True,
    },
}

# Genre halved, energy doubled. Sums to 1.075; score_song divides by the
# sum of the weights used, which normalizes them automatically.
EXPERIMENT_WEIGHTS = {"genre": 0.175, "mood": 0.30, "energy": 0.50, "acoustic": 0.10}
EXPERIMENT_PROFILE = "A: High-Energy Pop"


def run_profiles(songs: list) -> None:
    """Print the top 5 for every profile using the default weights."""
    for name, prefs in PROFILES.items():
        print("=" * 60)
        print(f"Profile {name}")
        print_recommendations(prefs, recommend_songs(prefs, songs, k=5))


def run_weight_experiment(songs: list) -> None:
    """Compare the default and experimental weights for one profile."""
    prefs = PROFILES[EXPERIMENT_PROFILE]
    baseline = recommend_songs(prefs, songs, k=len(songs))
    experiment = recommend_songs(prefs, songs, k=len(songs), weights=EXPERIMENT_WEIGHTS)
    baseline_rank = {song["id"]: rank for rank, (song, _, _) in enumerate(baseline, start=1)}

    print("=" * 60)
    print(f"Weight experiment on profile {EXPERIMENT_PROFILE}")
    print(f"Baseline weights:     {DEFAULT_WEIGHTS}")
    print(f"Experimental weights: {EXPERIMENT_WEIGHTS} (sum {sum(EXPERIMENT_WEIGHTS.values()):.3f}, normalized)")

    print("\nBaseline top 5:")
    for rank, (song, score, _) in enumerate(baseline[:5], start=1):
        print(f"  {rank}. {song['title']} - {song['artist']}  {score:.4f}")

    print("\nExperimental top 5 (change vs. baseline rank):")
    for rank, (song, score, _) in enumerate(experiment[:5], start=1):
        old_rank = baseline_rank[song["id"]]
        move = "same" if old_rank == rank else f"was #{old_rank}"
        print(f"  {rank}. {song['title']} - {song['artist']}  {score:.4f}  ({move})")

    print_recommendations(prefs, experiment[:5])

    print("Same weight change applied to every profile (top 5 titles):")
    for name, other_prefs in PROFILES.items():
        before = [song["title"] for song, _, _ in recommend_songs(other_prefs, songs, k=5)]
        after = [song["title"] for song, _, _ in recommend_songs(other_prefs, songs, k=5, weights=EXPERIMENT_WEIGHTS)]
        status = "unchanged" if before == after else "changed"
        print(f"\n  {name} ({status})")
        print(f"    baseline:     {', '.join(before)}")
        print(f"    experimental: {', '.join(after)}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs")
    run_profiles(songs)
    run_weight_experiment(songs)


if __name__ == "__main__":
    main()
