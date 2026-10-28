# Text Utils API

Three small text utilities in [FastAPI](https://fastapi.tiangolo.com/). Part of the [Mintlify demo org](https://github.com/mintlify-demo). Docs: [https://mintlify-demo.mintlify.site/text-utils-api](https://mintlify-demo.mintlify.site/text-utils-api). The OpenAPI spec includes `x-codeSamples` in cURL, Python, JavaScript and Go.

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

## Docs

Published at [https://mintlify-demo.mintlify.site/text-utils-api](https://mintlify-demo.mintlify.site/text-utils-api) (sign-in required). The pages and the API spec live in the [`docs` repo, under `text-utils-api/`](https://github.com/mintlify-demo/docs/tree/main/text-utils-api), not here. This repo holds only code and tests. When a pull request here changes the API, Mintlify's *Update from code changes* automation opens a pull request in the `docs` repo with the matching docs update.

## Hosting

TODO(hosting): the API will be hosted with Mintlify's internal tooling (details TBD). Until then the OpenAPI `servers` list only `http://localhost:8000`. When the hosted URL exists, add it as the first entry of `servers=[...]` in `main.py`, update the `servers` list in the `docs` repo's spec too, and rebase the demo stack (see the demo kit README).

`docs` repo `text-utils-api/guides/partner-batch-processing.mdx` is gated to the `partner` and `enterprise` groups with `groups` frontmatter.

## Ticket → file map

Context for Mintlify's *Update docs from tickets* automation (seed tickets: `linear-tickets.json` in the demo kit).

| Ticket | What | Where |
| --- | --- | --- |
| DEMO-6 | Stop-word filtering for `/word-count` (`ignore_stop_words`) | `main.py` (`count_words`, `TextRequest`, `WordCountResponse`), `docs` repo `text-utils-api/guides/examples.mdx` |
