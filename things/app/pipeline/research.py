"""
Research Pipeline Orchestrator


This is the core logic that ties everything together:
1. Extract video info (YouTube or TikTok)
2. Analyze creator's content pattern
3. Check fact-check databases
4. Search trusted news sources (fallback)
5. Generate grandmother-friendly explanation
"""


from app.models import ResearchResult, Platform
from app.services import video, factcheck, search, llm




async def research_video(url: str) -> ResearchResult:
    """
    Run the full research pipeline on a video URL.


    Mutual Thriving Check embedded in the process:
    - Self (grandmother): Explanation reduces anxiety, doesn't dismiss
    - Others (family): Saves hours of manual research
    - Future: Builds media literacy gently over time
    """


    # Step 1: Extract video information
    video_info = await video.get_video_info(url)


    # Step 2: Get creator's recent content and analyze patterns
    creator_titles = await video.get_creator_history(
        video_info.creator_id,
        video_info.platform
    )
    creator_analysis = video.analyze_creator_pattern(creator_titles)


    # Step 3: Build the claim to search for
    # Combine title + key parts of description
    claim_text = _extract_claim(video_info)


    # Step 4: Check fact-check databases
    fact_checks = await factcheck.check_claim(claim_text)


    # Step 5: If no fact-checks, search trusted news sources
    search_results = []
    if not fact_checks:
        search_results = await search.search_trusted_sources(claim_text)


    # Determine confidence level
    if fact_checks:
        confidence = "high"
    elif search_results:
        confidence = "medium"
    else:
        confidence = "low"


    # Step 6: Generate explanation via LLM
    explanation = await llm.generate_explanation(
        video_info=video_info,
        creator_titles=creator_titles,
        creator_analysis=creator_analysis,
        fact_checks=fact_checks,
        search_results=search_results
    )


    # Collect all sources
    sources = []
    sources.extend([fc.url for fc in fact_checks if fc.url])
    sources.extend([sr.url for sr in search_results if sr.url])


    return ResearchResult(
        claim=video_info.title,
        confidence=confidence,
        explanation=explanation,
        sources=sources,
        platform=video_info.platform,
        channel_is_suspect=creator_analysis.get("is_suspect", False),
        # Additional fields for logging
        video_url=video_info.url,
        video_title=video_info.title,
        video_creator=video_info.creator,
        claim_extracted=claim_text,
        fact_checks_found=len(fact_checks),
        search_results_found=len(search_results),
    )




def _extract_claim(video_info) -> str:
    """
    Extract the core claim from video info.
    Prioritize: title > transcript first 200 words > description
    """
    parts = [video_info.title]


    if video_info.transcript:
        # First 200 words of transcript often contain the main claim
        words = video_info.transcript.split()[:200]
        parts.append(" ".join(words))
    elif video_info.description:
        # First 200 chars of description
        parts.append(video_info.description[:200])


    # Also include hashtags as they often signal the topic
    if video_info.hashtags:
        parts.append(" ".join(video_info.hashtags[:5]))


    return " ".join(parts)[:500]  # Limit total length





