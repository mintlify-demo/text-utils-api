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
    assert r.json() == {"words": 6, "unique_words": 4, "characters": 18, "lines": 1}


def test_word_count_is_case_insensitive_and_counts_lines():
    r = client.post("/word-count", json={"text": "Hello\nhello world"})
    body = r.json()
    assert body["words"] == 3 and body["unique_words"] == 2 and body["lines"] == 2


def test_word_count_empty():
    r = client.post("/word-count", json={"text": ""})
    assert r.json() == {"words": 0, "unique_words": 0, "characters": 0, "lines": 0}


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
    for path in ("/reverse", "/word-count", "/palindrome"):
        langs = [s["lang"] for s in spec["paths"][path]["post"]["x-codeSamples"]]
        assert langs == ["bash", "python", "javascript", "go"]


def test_committed_openapi_spec_is_up_to_date():
    """If this fails, run `make spec` and commit docs/openapi.json."""
    committed = json.loads((Path(__file__).parent.parent / "docs" / "openapi.json").read_text())
    assert committed == app.openapi()
