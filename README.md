# Employee Aggregator — Take-Home

You're building a small slice of a real system: a frontend that talks to a **proxy**
(a BFF), which in turn talks to **three upstream HR Provider APIs**. Each Provider
exposes employee data, but every one of them does it differently — different
endpoints, different authentication, and different data shapes. Your job is to hide
all of that behind one clean, unified view.

```
  frontend (TanStack Start)  ──►  proxy / BFF (FastAPI)  ──►  Provider A  (Atlas HR)
                                                          ──►  Provider B  (Beacon People)
                                                          ──►  Provider C  (Cobalt Directory)
```

## What's provided vs. what you build

| Component | State | Who builds it |
|-----------|-------|---------------|
| `mock_apis/` — the 3 Provider APIs | **Done.** Do not modify; treat them as external services you don't control. | — |
| `proxy/` — FastAPI BFF | Bare starter skeleton | **You** |
| `frontend/` — TanStack Start app | Bare starter (default template) | **You** |

## Getting started

Prerequisites: [`uv`](https://docs.astral.sh/uv/) (Python) and [`bun`](https://bun.sh/) (frontend).

```bash
cp .env.example .env      # Provider credentials
make install              # install all dependencies
make dev                  # start everything (Ctrl-C stops it)
```

Once running:

| URL | What |
|-----|------|
| http://localhost:3000 | Frontend (yours to build) |
| http://localhost:8000/docs | Proxy (yours to build) |
| http://localhost:9001/docs | Provider A — Atlas HR |
| http://localhost:9002/docs | Provider B — Beacon People |
| http://localhost:9003/docs | Provider C — Cobalt Directory |

## The Providers

Each Provider runs as its own service with its own interactive docs at `/docs`. **Start
by reading those docs** — discovering each one's endpoints, how it wants to be
authenticated, and the exact shape of its data is part of the exercise.

Credentials live in `.env` (copied from `.env.example`):

| Provider | Base URL | Credential (env var) |
|----------|----------|----------------------|
| Atlas HR | `http://localhost:9001` | `ATLAS_API_KEY` |
| Beacon People | `http://localhost:9002` | `BEACON_API_KEY` |
| Cobalt Directory | `http://localhost:9003` | `COBALT_TOKEN` |

Each Provider authenticates differently — its `/docs` will show you how. You have the
credentials; you need to work out how each API expects to receive them.

## Notes

- The three Providers are intentionally inconsistent with each other. Expect different
  field names, nesting, units, date formats, status representations, and pagination
  styles.
- There's no required file layout or function names in `proxy/` and `frontend/` — make
  the structure your own.
- Focus on clarity and judgment over polish. We're more interested in *how* you model
  the problem than in how many features you finish.
