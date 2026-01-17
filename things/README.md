# Fact-Check Companion (Promptless Products)

## One narrow domain
A high-signal fact-check companion for one top-tier performer who needs to stay sharp when information is messy (e.g., after work, between meetings, on travel days).

Instead of asking you to craft prompts, it turns a forwarded link into a short, decision-ready brief you can forward (or use to decide what to ignore).

## What it does (and when)
- **Input**: a YouTube or TikTok link (no prompt required).
- **Output**: a brief message summarizing the key claim(s), what reputable sources support/deny, and what to do with it.
- **When it acts**: it stays low-noise; when signals are weak it says so and avoids overconfident conclusions.

## Signals (why it’s confident)
The pipeline uses a small set of signals that are explainable:
1. **Video content**: title/description + transcript when available.
2. **Creator pattern**: recent creator titles to detect repeated alarmist framing.
3. **Formal fact-checks**: Google Fact Check Tools API matches.
4. **Trusted coverage fallback**: targeted search across reputable domains.

## Restraint + timing
This project intentionally optimizes for long-term trust (high signal-to-noise):
- **High confidence** (formal fact-check found): direct language and a clear recommendation.
- **Medium confidence** (trusted coverage found): cautious language and what’s known.
- **Low confidence** (little signal): explicitly says uncertainty and avoids strong claims.

## Transparency
Each run stores:
- extracted claim text
- confidence level
- whether the creator looks pattern-suspect
- sources used

The Streamlit dashboard shows recent checks and the exact explanation that was sent.

## Running locally
Backend:
```bash
cd "/c/Users/corpa/OneDrive/Documents/Knowledge Base/Explorations/Hackathons/things"
"C:/Users/corpa/OneDrive/Documents/Knowledge Base/Explorations/Hackathons/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload
```

Local pipeline test:
```bash
cd "/c/Users/corpa/OneDrive/Documents/Knowledge Base/Explorations/Hackathons/things"
"C:/Users/corpa/OneDrive/Documents/Knowledge Base/Explorations/Hackathons/.venv/Scripts/python.exe" test_local.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Env vars (LLM)
Use **one** provider:
- Direct OpenAI: `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`)
- OpenRouter: `OPENROUTER_API_KEY` (+ optional `OPENROUTER_MODEL`)
- Azure OpenAI: `LLM_PROVIDER=azure`, `LLM_API_KEY`, `LLM_ENDPOINT`

Default `LLM_PROVIDER=auto` prefers OpenAI if `OPENAI_API_KEY` is set.
