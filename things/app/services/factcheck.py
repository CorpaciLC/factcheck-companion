import httpx
from app.config import settings
from app.models import FactCheckResult




async def check_claim(claim: str) -> list[FactCheckResult]:
    """Query Google Fact Check Tools API."""
    if not settings.GOOGLE_API_KEY:
        return []


    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "key": settings.GOOGLE_API_KEY,
        "query": claim[:200],  # API has query length limits
        "languageCode": "en"
    }


    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []


    results = []
    for claim_data in data.get("claims", []):
        for review in claim_data.get("claimReview", []):
            results.append(FactCheckResult(
                claim=claim_data.get("text", ""),
                claimant=claim_data.get("claimant"),
                rating=review.get("textualRating", "Unknown"),
                publisher=review.get("publisher", {}).get("name", "Unknown"),
                url=review.get("url", "")
            ))


    return results[:5]  # Limit to top 5 results





