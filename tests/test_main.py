import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_reverse():
    r = client.post("/reverse", json={"text": "Hello"})
    assert r.status_code == 200
    assert r.json() == {"original": "Hello", "reversed": "olleH"}


def test_reverse_empty_string():
    assert client.post("/reverse", json={"text": ""}).json()["reversed"] == ""


def test_reverse_requires_text():
    assert client.post("/reverse", json={}).status_code == 422


def test_word_count():
    r = client.post("/word-count", json={"text": "to be or not to be"})
    assert r.json() == {"words": 6, "unique_words": 4, "characters": 18, "lines": 1, "reading_time_minutes": 1}


def test_word_count_is_case_insensitive_and_counts_lines():
    r = client.post("/word-count", json={"text": "Hello\nhello world"})
    body = r.json()
    assert body["words"] == 3 and body["unique_words"] == 2 and body["lines"] == 2


def test_word_count_empty():
    r = client.post("/word-count", json={"text": ""})
    assert r.json() == {"words": 0, "unique_words": 0, "characters": 0, "lines": 0, "reading_time_minutes": 0}


def test_palindrome_true_ignoring_punctuation():
    r = client.post("/palindrome", json={"text": "A man, a plan, a canal: Panama"})
    assert r.json()["is_palindrome"] is True


def test_palindrome_false():
    assert client.post("/palindrome", json={"text": "Mintlify"}).json()["is_palindrome"] is False


def test_palindrome_strict_mode():
    r = client.post("/palindrome", json={"text": "Racecar", "ignore_case_and_punctuation": False})
    assert r.json()["is_palindrome"] is False
    r = client.post("/palindrome", json={"text": "racecar", "ignore_case_and_punctuation": False})
    assert r.json()["is_palindrome"] is True


def test_spec_has_code_samples_in_four_languages():
    spec = app.openapi()
    for path in ("/reverse", "/word-count", "/palindrome", "/slugify", "/word-frequency"):
        langs = [s["lang"] for s in spec["paths"][path]["post"]["x-codeSamples"]]
        assert langs == ["bash", "python", "javascript", "go"]


def test_slugify():
    r = client.post("/slugify", json={"text": "Héllo, Mintlify Docs!"})
    assert r.json() == {"original": "Héllo, Mintlify Docs!", "slug": "hello-mintlify-docs"}


def test_slugify_separator_and_max_length():
    r = client.post("/slugify", json={"text": "The quick brown fox", "separator": "_", "max_length": 10})
    assert r.json()["slug"] == "the_quick"


def test_slugify_rejects_bad_separator():
    assert client.post("/slugify", json={"text": "x", "separator": "/"}).status_code == 422


def test_word_frequency():
    r = client.post("/word-frequency", json={"text": "To be or not to be", "top": 3})
    assert r.json() == {
        "total_words": 6,
        "words": [{"word": "to", "count": 2}, {"word": "be", "count": 2}, {"word": "or", "count": 1}],
    }


def test_word_frequency_min_length():
    r = client.post("/word-frequency", json={"text": "the cat and the hat", "min_length": 4})
    assert r.json() == {"total_words": 0, "words": []}


def test_reading_time_rounds_up():
    r = client.post("/word-count", json={"text": "word " * 401})
    assert r.json()["reading_time_minutes"] == 3


def test_committed_openapi_spec_is_up_to_date():
    """If this fails, run `make spec` and commit docs/openapi.json."""
    committed = json.loads((Path(__file__).parent.parent / "docs" / "openapi.json").read_text())
    assert committed == app.openapi()
