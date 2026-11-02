"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs")

    # Default profile; keys match the UserProfile fields
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(
        f"\nUser profile: genre={user_prefs['favorite_genre']}, mood={user_prefs['favorite_mood']}, "
        f"target_energy={user_prefs['target_energy']:.2f}, likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print(f"\nTop {len(recommendations)} recommendations:\n")
    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"{rank}. {song['title']} - {song['artist']}")
        print(f"   Score: {score:.4f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()
