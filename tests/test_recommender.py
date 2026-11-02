import copy
from pathlib import Path

import pytest

from src.recommender import Song, UserProfile, Recommender, load_songs, score_song, recommend_songs

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- score_song / recommend_songs (functional API) ---

def make_song(id=1, genre="pop", mood="happy", energy=0.8, acousticness=0.2, artist="Test Artist"):
    return {
        "id": id,
        "title": f"Song {id}",
        "artist": artist,
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "tempo_bpm": 120.0,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": acousticness,
    }


POP_PREFS = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.8,
    "likes_acoustic": False,
}


def test_genre_match_adds_genre_weight():
    match, _ = score_song(POP_PREFS, make_song(genre="pop"))
    no_match, _ = score_song(POP_PREFS, make_song(genre="rock"))
    assert match - no_match == pytest.approx(0.35)


def test_genre_match_is_exact_not_partial():
    match, _ = score_song(POP_PREFS, make_song(genre="pop"))
    partial, _ = score_song(POP_PREFS, make_song(genre="indie pop"))
    assert match - partial == pytest.approx(0.35)


def test_mood_match_adds_mood_weight():
    match, _ = score_song(POP_PREFS, make_song(mood="happy"))
    no_match, _ = score_song(POP_PREFS, make_song(mood="sad"))
    assert match - no_match == pytest.approx(0.30)


def test_matching_ignores_case_and_whitespace():
    prefs = dict(POP_PREFS, favorite_genre="  POP ", favorite_mood="Happy")
    score, reasons = score_song(prefs, make_song(genre="Pop", mood=" HAPPY"))
    assert score == pytest.approx(1.0 - 0.10 * 0.2)
    assert any("Genre matches" in r for r in reasons)
    assert any("Mood matches" in r for r in reasons)


def test_energy_similarity_rewards_closeness_not_height():
    prefs = dict(POP_PREFS, favorite_genre="none", favorite_mood="none", target_energy=0.40)
    # Same acousticness, so only energy differs: 0.25 * (1 - gap)
    near, _ = score_song(prefs, make_song(energy=0.45))
    far, _ = score_song(prefs, make_song(energy=0.90))
    assert near - far == pytest.approx(0.25 * (0.95 - 0.50))
    assert near > far


def test_acousticness_follows_preference():
    acoustic_song = make_song(acousticness=0.9)
    electronic_song = make_song(acousticness=0.1)
    likes = dict(POP_PREFS, likes_acoustic=True)
    dislikes = dict(POP_PREFS, likes_acoustic=False)
    assert score_song(likes, acoustic_song)[0] > score_song(likes, electronic_song)[0]
    assert score_song(dislikes, electronic_song)[0] > score_song(dislikes, acoustic_song)[0]


def test_missing_acoustic_preference_renormalizes():
    prefs = {"favorite_genre": "pop", "favorite_mood": "sad", "target_energy": 0.8}
    score, reasons = score_song(prefs, make_song(genre="pop", mood="happy", energy=0.6))
    # (0.35 genre + 0 mood + 0.25 * 0.8 energy) / 0.90
    assert score == pytest.approx((0.35 + 0.25 * 0.8) / 0.90)
    assert not any(r.startswith("Acousticness") for r in reasons)


def test_perfect_match_without_acoustic_preference_scores_one():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    score, _ = score_song(prefs, make_song(energy=0.8))
    assert score == pytest.approx(1.0)


def test_scores_stay_between_zero_and_one_for_real_dataset():
    songs = load_songs(str(DATA_PATH))
    profiles = [
        POP_PREFS,
        {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.4, "likes_acoustic": True},
        {"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.0},
        {"favorite_genre": "jazz", "favorite_mood": "relaxed", "target_energy": 1.0, "likes_acoustic": False},
    ]
    for prefs in profiles:
        for song in songs:
            score, _ = score_song(prefs, song)
            assert 0.0 <= score <= 1.0


def test_reasons_only_claim_components_that_matched():
    score, reasons = score_song(POP_PREFS, make_song(genre="rock", mood="happy", energy=0.7, acousticness=0.3))
    assert not any("Genre matches" in r for r in reasons)
    assert "Mood matches happy (+0.3000)" in reasons
    assert "Energy 0.70 is 0.10 from target 0.80 (+0.2250)" in reasons
    assert "Acousticness 0.30 vs non-acoustic preference (+0.0700)" in reasons
    assert score == pytest.approx(0.30 + 0.225 + 0.07)


def test_recommend_songs_sorted_descending_with_explanations():
    songs = [
        make_song(id=1, genre="rock", mood="sad", energy=0.2),
        make_song(id=2, genre="pop", mood="happy", energy=0.8),
        make_song(id=3, genre="pop", mood="sad", energy=0.8),
    ]
    results = recommend_songs(POP_PREFS, songs, k=3)
    assert [song["id"] for song, _, _ in results] == [2, 3, 1]
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(explanation, str) and explanation for _, _, explanation in results)


def test_equal_scores_break_ties_by_lowest_id():
    songs = [make_song(id=9), make_song(id=3), make_song(id=5)]
    results = recommend_songs(POP_PREFS, songs, k=3)
    assert [song["id"] for song, _, _ in results] == [3, 5, 9]


def test_top_k_selection_and_edge_cases():
    songs = [make_song(id=i, energy=i / 10) for i in range(1, 6)]
    assert len(recommend_songs(POP_PREFS, songs, k=2)) == 2
    assert len(recommend_songs(POP_PREFS, songs, k=10)) == 5
    assert recommend_songs(POP_PREFS, songs, k=0) == []
    assert recommend_songs(POP_PREFS, songs, k=-1) == []


def test_empty_song_list_returns_empty():
    assert recommend_songs(POP_PREFS, [], k=5) == []
    assert Recommender([]).recommend(UserProfile("pop", "happy", 0.8, False), k=5) == []


def test_recommend_songs_does_not_modify_input():
    songs = [make_song(id=1), make_song(id=2, genre="rock")]
    before = copy.deepcopy(songs)
    recommend_songs(POP_PREFS, songs, k=2)
    assert songs == before


def test_load_songs_reads_all_rows_with_numeric_types():
    songs = load_songs(str(DATA_PATH))
    assert len(songs) == 20
    assert isinstance(songs[0]["id"], int)
    for field in ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]:
        assert isinstance(songs[0][field], float)
