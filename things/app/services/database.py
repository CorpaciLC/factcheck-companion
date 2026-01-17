"""
Supabase Database Service


Handles logging of fact-check queries to Supabase.
Privacy by design: Phone numbers are NEVER passed to this module.
"""


from typing import Optional
from supabase import create_client, Client
from app.config import settings
from app.models import ResearchResult, VideoInfo




def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if configured."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)




async def log_query(
    video_info: VideoInfo,
    result: ResearchResult,
    claim_extracted: str,
    fact_checks_count: int,
    search_results_count: int
) -> bool:
    """
    Log a fact-check query to Supabase.


    PRIVACY NOTE: This function intentionally does NOT accept any user
    identifiers (phone number, IP, etc.). Anonymization is achieved by
    simply never passing PII to this function.


    Args:
        video_info: Extracted video metadata
        result: The research result
        claim_extracted: The claim text we searched for
        fact_checks_count: Number of formal fact-checks found
        search_results_count: Number of news search results found


    Returns:
        True if logged successfully, False otherwise
    """
    client = get_supabase_client()
    if not client:
        return False


    try:
        data = {
            "platform": video_info.platform.value,
            "video_url": video_info.url,
            "video_title": video_info.title,
            "video_creator": video_info.creator,
            "claim_extracted": claim_extracted[:1000] if claim_extracted else "",
            "confidence": result.confidence,
            "explanation": result.explanation[:5000] if result.explanation else "",
            "sources": result.sources[:10],  # Limit to 10 sources
            "channel_is_suspect": result.channel_is_suspect,
            "fact_checks_found": fact_checks_count,
            "search_results_found": search_results_count,
        }


        client.table("queries").insert(data).execute()
        return True


    except Exception as e:
        # Log error but don't crash the main flow
        if settings.DEBUG:
            print(f"Failed to log query to Supabase: {e}")
        return False




async def log_query_from_result(result: ResearchResult) -> bool:
    """
    Simplified logging function that takes a ResearchResult directly.


    The ResearchResult now contains all metadata needed for logging.
    No PII is ever part of ResearchResult by design.


    Args:
        result: The complete research result with metadata


    Returns:
        True if logged successfully, False otherwise
    """
    client = get_supabase_client()
    if not client:
        return False


    try:
        data = {
            "platform": result.platform.value,
            "video_url": result.video_url,
            "video_title": result.video_title,
            "video_creator": result.video_creator,
            "claim_extracted": result.claim_extracted[:1000] if result.claim_extracted else "",
            "confidence": result.confidence,
            "explanation": result.explanation[:5000] if result.explanation else "",
            "sources": result.sources[:10],
            "channel_is_suspect": result.channel_is_suspect,
            "fact_checks_found": result.fact_checks_found,
            "search_results_found": result.search_results_found,
        }


        client.table("queries").insert(data).execute()
        return True


    except Exception as e:
        if settings.DEBUG:
            print(f"Failed to log query to Supabase: {e}")
        return False




async def get_recent_queries(limit: int = 100) -> list[dict]:
    """
    Fetch recent queries for the dashboard.


    Args:
        limit: Maximum number of queries to return


    Returns:
        List of query records, newest first
    """
    client = get_supabase_client()
    if not client:
        return []


    try:
        response = client.table("queries") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
    except Exception:
        return []




async def get_query_stats() -> dict:
    """
    Get aggregate statistics for the dashboard.


    Returns:
        Dict with total_queries, platform_breakdown, confidence_breakdown
    """
    client = get_supabase_client()
    if not client:
        return {}


    try:
        # Get all queries for stats (could optimize with SQL functions later)
        response = client.table("queries").select("platform, confidence").execute()
        queries = response.data


        total = len(queries)
        platforms = {}
        confidences = {}


        for q in queries:
            p = q.get("platform", "unknown")
            c = q.get("confidence", "unknown")
            platforms[p] = platforms.get(p, 0) + 1
            confidences[c] = confidences.get(c, 0) + 1


        return {
            "total_queries": total,
            "platform_breakdown": platforms,
            "confidence_breakdown": confidences,
        }
    except Exception:
        return {}





