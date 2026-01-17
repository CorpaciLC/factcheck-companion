# Fact-Check Companion (Promptless Products)

## One narrow domain
A quiet companion for a single caregiver who regularly gets alarming videos from a loved one (e.g., evenings after work).

Instead of asking the user to craft prompts, the system turns a forwarded link into a short, calm reply the user can send back.

## What it does (and when)
- **Input**: a YouTube or TikTok link (no prompt required).
- **Output**: a brief message that summarizes the key claims and what reputable sources say.
- **When it acts**: only when it has enough signal to be useful; otherwise it stays cautious and labels low confidence.

## Signals (why it’s confident)
The pipeline uses a small set of signals that are explainable:
1. **Video content**: title/description + transcript when available.
2. **Creator pattern**: recent creator titles to detect repeated alarmist framing.
3. **Formal fact-checks**: Google Fact Check Tools API matches.
4. **Trusted coverage fallback**: targeted search across reputable domains.

## Restraint + timing
This project intentionally optimizes for long-term trust:
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
