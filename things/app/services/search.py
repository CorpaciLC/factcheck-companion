import httpx
from app.config import settings
from app.models import SearchResult




TRUSTED_DOMAINS = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "snopes.com",
    "factcheck.org",
    "politifact.com",
    "npr.org",
    "theguardian.com",
]




async def search_trusted_sources(query: str) -> list[SearchResult]:
    """Search only trusted news sources using Serper."""
    if not settings.SERPER_API_KEY:
        return []


    # Build query limited to trusted domains
    site_query = " OR ".join([f"site:{d}" for d in TRUSTED_DOMAINS])
    full_query = f"{query} ({site_query})"


    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": settings.SERPER_API_KEY}


    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=headers,
                json={"q": full_query, "num": 5},
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []


    results = []
    for r in data.get("organic", [])[:5]:
        results.append(SearchResult(
            title=r.get("title", ""),
            snippet=r.get("snippet", ""),
            url=r.get("link", "")
        ))


    return results





