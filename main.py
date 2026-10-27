"""Text Utils API: reverse text, count words, check palindromes, make slugs.

Four endpoints, all `POST` with a JSON body containing `text`:
  /reverse     -> the text backwards
  /word-count  -> words, characters, lines, unique words
  /palindrome  -> is the text a palindrome?
  /slugify     -> a URL-friendly slug

The OpenAPI spec also includes `x-codeSamples` (cURL, Python, JavaScript, Go)
so Mintlify can show ready-to-run examples on every endpoint page.

Run it:  uvicorn main:app --reload
"""
import json
import re
import unicodedata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# The text logic (plain functions, no web code)
# --------------------------------------------------------------------------- #


def reverse_text(text: str) -> str:
    return text[::-1]


def count_words(text: str) -> dict:
    words = re.findall(r"[\w'-]+", text.lower())
    return {
        "words": len(words),
        "unique_words": len(set(words)),
        "characters": len(text),
        "lines": len(text.splitlines()) if text else 0,
    }


def is_palindrome(text: str, ignore_case_and_punctuation: bool = True) -> bool:
    if ignore_case_and_punctuation:
        # Keep only letters and digits, lower-cased: "A man, a plan..." -> "amanaplan..."
        text = "".join(ch.lower() for ch in text if ch.isalnum())
    return text == text[::-1]


# --------------------------------------------------------------------------- #
# Code samples for the docs (shown next to each endpoint)
# --------------------------------------------------------------------------- #


def slugify(text: str, separator: str = "-", max_length: int | None = None) -> str:
    """Turn text into a lowercase, URL-friendly slug: "Héllo, World!" -> "hello-world"."""
    # Strip accents (é -> e), then keep only letters, digits and spaces.
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-z0-9]+", ascii_text.lower())
    slug = separator.join(words)
    if max_length is not None and len(slug) > max_length:
        slug = slug[:max_length].rstrip(separator)
    return slug


def code_samples(path: str, body: dict) -> list[dict]:
    """Build the `x-codeSamples` list for one endpoint, in four languages."""
    payload = json.dumps(body)
    url = f"http://localhost:8000{path}"
    return [
        {
            "lang": "bash",
            "label": "cURL",
            "source": f"curl -X POST {url} \\\n  -H 'Content-Type: application/json' \\\n  -d '{payload}'",
        },
        {
            "lang": "python",
            "label": "Python",
            "source": f"import requests\n\nresponse = requests.post(\n    \"{url}\",\n    json={body!r},\n)\nprint(response.json())",
        },
        {
            "lang": "javascript",
            "label": "JavaScript",
            "source": (
                f"const response = await fetch(\"{url}\", {{\n"
                f"  method: \"POST\",\n"
                f"  headers: {{ \"Content-Type\": \"application/json\" }},\n"
                f"  body: JSON.stringify({payload}),\n"
                f"}});\n"
                f"console.log(await response.json());"
            ),
        },
        {
            "lang": "go",
            "label": "Go",
            "source": (
                "package main\n\n"
                "import (\n\t\"fmt\"\n\t\"io\"\n\t\"net/http\"\n\t\"strings\"\n)\n\n"
                "func main() {\n"
                f"\tbody := strings.NewReader(`{payload}`)\n"
                f"\tresp, err := http.Post(\"{url}\", \"application/json\", body)\n"
                "\tif err != nil {\n\t\tpanic(err)\n\t}\n"
                "\tdefer resp.Body.Close()\n"
                "\tout, _ := io.ReadAll(resp.Body)\n"
                "\tfmt.Println(string(out))\n"
                "}"
            ),
        },
    ]


# --------------------------------------------------------------------------- #
# Request / response models
# --------------------------------------------------------------------------- #


class TextRequest(BaseModel):
    text: str = Field(..., max_length=10_000, description="The text to work on (up to 10,000 characters).", examples=["Hello, Mintlify!"])


class ReverseResponse(BaseModel):
    original: str = Field(..., description="The text you sent.", examples=["Hello, Mintlify!"])
    reversed: str = Field(..., description="The text, backwards.", examples=["!yfitniM ,olleH"])


class WordCountResponse(BaseModel):
    words: int = Field(..., description="Total number of words.", examples=[5])
    unique_words: int = Field(..., description="Number of different words (case-insensitive).", examples=[4])
    characters: int = Field(..., description="Total characters, including spaces and punctuation.", examples=[24])
    lines: int = Field(..., description="Number of lines.", examples=[1])


class PalindromeRequest(TextRequest):
    ignore_case_and_punctuation: bool = Field(
        True,
        description="When `true`, case, spaces and punctuation are ignored, so `A man, a plan, a canal: Panama` counts.",
        examples=[True],
    )


class PalindromeResponse(BaseModel):
    is_palindrome: bool = Field(..., description="Whether the text reads the same forwards and backwards.", examples=[True])
    text: str = Field(..., description="The text you sent.", examples=["Racecar"])


class SlugifyRequest(TextRequest):
    separator: str = Field("-", description="Character placed between words: `-` (default) or `_`.", pattern="^[-_]$", examples=["-"])
    max_length: int | None = Field(None, ge=1, le=200, description="Optional maximum slug length. Longer slugs are cut and any trailing separator is removed.", examples=[50])


class SlugifyResponse(BaseModel):
    original: str = Field(..., description="The text you sent.", examples=["Hello, Mintlify Docs!"])
    slug: str = Field(..., description="The URL-friendly slug.", examples=["hello-mintlify-docs"])


# --------------------------------------------------------------------------- #
# The app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Text Utils API",
    version="1.1.0",
    summary="Reverse text, count words, check palindromes and make slugs.",
    description="Four small text utilities, each one a single `POST` request with a JSON body.",
    servers=[{"url": "http://localhost:8000", "description": "Local development"}],
    openapi_tags=[{"name": "Text", "description": "Small text utilities."}],
)

# Allow browsers to call the API from anywhere. The docs' "Try it" playground
# sends requests straight from your browser to the API, so it needs CORS.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post(
    "/reverse",
    tags=["Text"],
    operation_id="reverseText",
    summary="Reverse text",
    response_model=ReverseResponse,
    openapi_extra={"x-codeSamples": code_samples("/reverse", {"text": "Hello, Mintlify!"})},
)
def reverse(body: TextRequest) -> ReverseResponse:
    """Return the text with its characters in reverse order."""
    return ReverseResponse(original=body.text, reversed=reverse_text(body.text))


@app.post(
    "/word-count",
    tags=["Text"],
    operation_id="countWords",
    summary="Count words",
    response_model=WordCountResponse,
    openapi_extra={"x-codeSamples": code_samples("/word-count", {"text": "to be or not to be"})},
)
def word_count(body: TextRequest) -> WordCountResponse:
    """Count words, unique words, characters and lines.

    Words are runs of letters, digits, apostrophes and hyphens. Comparison
    for `unique_words` ignores case.
    """
    return WordCountResponse(**count_words(body.text))


@app.post(
    "/palindrome",
    tags=["Text"],
    operation_id="checkPalindrome",
    summary="Check for a palindrome",
    response_model=PalindromeResponse,
    openapi_extra={"x-codeSamples": code_samples("/palindrome", {"text": "A man, a plan, a canal: Panama"})},
)
def palindrome(body: PalindromeRequest) -> PalindromeResponse:
    """Check whether the text reads the same forwards and backwards."""
    return PalindromeResponse(
        is_palindrome=is_palindrome(body.text, body.ignore_case_and_punctuation),
        text=body.text,
    )


@app.post(
    "/slugify",
    tags=["Text"],
    operation_id="slugifyText",
    summary="Make a URL slug",
    response_model=SlugifyResponse,
    openapi_extra={"x-codeSamples": code_samples("/slugify", {"text": "Hello, Mintlify Docs!"})},
)
def slugify_text(body: SlugifyRequest) -> SlugifyResponse:
    """Turn text into a lowercase, URL-friendly slug.

    Accents are removed (`é` becomes `e`), anything that is not a letter or
    digit is dropped, and words are joined with `separator`.
    """
    return SlugifyResponse(original=body.text, slug=slugify(body.text, body.separator, body.max_length))
