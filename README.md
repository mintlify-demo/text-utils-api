# Text Utils API

Three small text utilities in [FastAPI](https://fastapi.tiangolo.com/). Part of the [Mintlify demo org](https://github.com/mintlify-demo): `docs/` holds this API's Mintlify docs. The OpenAPI spec includes `x-codeSamples` in cURL, Python, JavaScript and Go.

| Endpoint | What it does |
| --- | --- |
| `POST /reverse` | Reverse the text |
| `POST /word-count` | Count words, unique words, characters and lines |
| `POST /palindrome` | Check whether the text is a palindrome |

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000  (Swagger UI at /docs)
```

```bash
curl -X POST localhost:8000/reverse -H 'Content-Type: application/json' -d '{"text": "Hello"}'
```

## Test it

```bash
python -m pytest -q
```

## Regenerate the OpenAPI spec

`docs/openapi.json` is committed so Mintlify can build the API reference without running the app. After changing `main.py` (including the code samples):

```bash
python scripts/export_openapi.py    # or: make spec
```

A test fails if the committed spec is out of date.

## Docs

`docs/` is a complete Mintlify project. The central [`docs`](https://github.com/mintlify-demo/docs) repo publishes it at `/text-utils-api`. Preview just this folder with `cd docs && mint dev`.

## Hosting

TODO(hosting): the API will be hosted with Mintlify's internal tooling (details TBD). Until then the OpenAPI `servers` list only `http://localhost:8000`. When the hosted URL exists, add it as the first entry of `servers=[...]` in `main.py`, run `make spec`, and rebase the demo stack (see the demo kit README).

`docs/guides/partner-batch-processing.mdx` is gated to the `partner` and `enterprise` groups with `groups` frontmatter.

## Ticket → file map

Context for Mintlify's *Update docs from tickets* automation (seed tickets: `linear-tickets.json` in the demo kit).

| Ticket | What | Where |
| --- | --- | --- |
| DEMO-6 | Stop-word filtering for `/word-count` (`ignore_stop_words`) | `main.py` (`count_words`, `TextRequest`, `WordCountResponse`), `docs/guides/examples.mdx` |
