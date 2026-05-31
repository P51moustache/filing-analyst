# Filing Analyst

[![CI](https://github.com/p51moustache/filing-analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/p51moustache/filing-analyst/actions/workflows/ci.yml)

An AI tool that reads an SEC **10-K** filing and produces a structured swing-trading workup: ~45 financial metrics, sector-specific metrics, red flags, catalysts, and a deterministic **0-100 trade score** with a rating. FastAPI + the Anthropic Claude API on the backend, React + TypeScript on the front.

It is built around an analyst framework: revenue bridges, FCF/NI quality, cash-conversion cycle, leverage, SBC dilution, and sector-specific keys for SaaS, semis, defense, banks, REITs, and more.

## How it works

```
Upload 10-K (PDF / HTML / TXT)
        |  PyPDF2 · BeautifulSoup · regex section extraction
        v
Parse into Item 1 / 1A / 7 / 7A / 8 / 9A sections
        v
Claude structured extraction  -->  validated ExtractedAnalysis object
        |  (no metric is invented by the app)
        v
Deterministic trade score (Python)  -->  40% catalysts · 35% quality/cash · 25% risk
        v
Excel report (openpyxl)  +  JSON for the UI
```

Analysis jobs are tracked in a SQLite store (`app/services/job_store.py`), so status
and results survive a server restart and the upload/report directories don't grow without
bound — jobs older than `RETENTION_HOURS` are pruned with their files on startup.

## The LLM engineering

The analyzer (`backend/app/services/ai_analyzer.py`):

- **Structured outputs, not regex.** The model is forced to return a schema-valid object via `client.messages.parse(output_format=ExtractedAnalysis)`. The Pydantic schema *is* the contract; there is no fragile "find the JSON in the prose" scraping, and a refusal or schema miss is handled explicitly.
- **Current, configurable model.** Defaults to the flagship (`claude-opus-4-8`) and is overridable per deploy via `ANTHROPIC_MODEL` to trade quality for cost (e.g. `claude-sonnet-4-6`, `claude-haiku-4-5`).
- **Prompt caching.** The large static analyst framework is sent once as a cached system prefix; only the filing text varies between requests, so repeat analyses pay ~0.1x for the framework prefix.
- **Resilience.** The Anthropic SDK is configured to retry 429 / 5xx with exponential backoff; API and connection errors are caught and surfaced as clean failures, with the `request_id` logged.
- **Token budgeting, not magic slices.** Filings are measured with the Token Counting API and trimmed to a configurable budget *transparently* (the amount dropped is logged) instead of being silently cut at an arbitrary character count.
- **Observability.** Input / output / cache tokens and an estimated dollar cost are logged per request.
- **Deterministic scoring is separated from extraction.** The model extracts facts; the 0-100 score is computed in plain, testable Python (`calculate_trade_score`), so the rating is reproducible and auditable.

## Trade score

| Bucket | Weight | Examples |
|---|---|---|
| Catalysts & trends | 40 | organic growth, margin expansion, buyback capacity, identified catalysts, RPO vs revenue |
| Quality & cash | 35 | FCF/NI conversion, cash-conversion cycle, SBC + dilution, Net Debt/EBITDA, interest coverage |
| Risk | 25 | red flags, material weakness, customer concentration, near-term debt maturities |

`>= 75` (with strong catalysts) -> Strong Buy · `>= 60` -> Buy · `>= 45` -> Hold · else Avoid.

## Tech stack

**Backend:** Python · FastAPI · Anthropic SDK (structured outputs, prompt caching, token counting) · Pydantic v2 · pandas / openpyxl · PyPDF2 · BeautifulSoup4 · SQLite job store
**Frontend:** React · TypeScript · axios
**Mobile:** React Native · Expo (SDK 56) · TypeScript

## Run it

You need a 10-K file and an Anthropic API key.

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your-key-here" > .env
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm start          # opens http://localhost:3000
```

Then download a 10-K from [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch) (the HTML or PDF of the filing) and upload it. Fetching from EDGAR is manual; the app analyzes whatever file you give it.

**Mobile (Expo)**

There's also a React Native client in [`mobile/`](mobile) that runs on your phone via [Expo Go](https://expo.dev/go) — same analysis, native UI. Run the backend with `--host 0.0.0.0`, then `cd mobile && npm install && npx expo start` and scan the QR code. On the same Wi-Fi it auto-detects the backend; see [mobile/README.md](mobile/README.md) for cellular/tunnel setup.

## Configuration

Backend environment variables (`backend/.env`):

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | _(required)_ | Your Anthropic key |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | Analysis model (structured outputs require a current model) |
| `ANTHROPIC_MAX_RETRIES` | `4` | SDK retry ceiling for 429 / 5xx |
| `MAX_INPUT_TOKENS` | `200000` | Filing token budget before transparent trimming |
| `MAX_FILE_SIZE` | `20971520` | Max upload size in bytes (20 MB) |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins |
| `DB_PATH` | `./analyses.db` | SQLite file backing the job store |
| `RETENTION_HOURS` | `168` | Age after which analyses and their files are pruned |

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Tests cover the scoring math, the extraction-to-pipeline mapping with the Claude call mocked, and the SQLite job store (durability + pruning) — so no API key or network is needed. The React app has a Jest/RTL test for the upload → poll → results flow. Everything runs in CI (`.github/workflows/ci.yml`): backend lint + tests, frontend typecheck + tests + build.

## API

- `POST /api/upload` — upload a 10-K
- `POST /api/analyze` — start analysis (optional custom focus prompt)
- `GET /api/status/{id}` — poll status / fetch the result
- `GET /api/report/{id}` — download the Excel report

## Notes

This is a personal project for analyzing public filings. It is not investment advice, and the trade score is a heuristic, not a recommendation. Running an analysis calls the Claude API and costs money proportional to the model and filing size.

---
Built by [Zach Lonsdale](https://www.linkedin.com/in/zach-lonsdale).
