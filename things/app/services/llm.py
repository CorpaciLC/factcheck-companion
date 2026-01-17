import os
import openai
from app.config import settings
from app.models import VideoInfo, FactCheckResult, SearchResult




SYSTEM_PROMPT = """You are helping a family member respond to their grandmother who has seen a concerning video (YouTube or TikTok).


The grandmother is easily influenced by catastrophic predictions and gets anxious. Your job is to help the grandson/granddaughter craft a response that:


1. ACKNOWLEDGES her concern (never dismiss or mock)
2. EXPLAINS what the video got wrong (if anything)
3. CITES credible sources
4. Is CALMING and respectful, not condescending
5. Is BRIEF - she won't read more than 150-200 words


MUTUAL THRIVING CHECK:
- Does this help grandmother feel less anxious? (not more)
- Does this save the family research time?
- Does this gently build her media literacy?


If the claim might actually be true or you're genuinely uncertain, SAY SO HONESTLY. Never fabricate certainty.


If the channel/creator has a pattern of doom content, mention it gently: "This channel tends to post a lot of alarming content..."


Format: Write as if the grandson will copy-paste this directly to grandmother. Use simple language. No jargon."""




# Model to deployment mapping 
MODEL_DEPLOYMENTS = {
    "main_region": {
        "o4-mini": "pdue-aoai-002-o4-mini",
        "o3-mini": "pdue-aoai-002-o3mini",
        "o3": "pdue-aoai-002-o3",
        "o1-mini": "pdue-aoai-002-o1mini",
        "o1": "pdue-aoai-002-o1",
        "gpt-4.1-mini": "pdue-aoai-002-gpt-4.1-mini",
        "gpt-4.1": "pdue-aoai-002-gpt-4.1",
        "gpt-4o-mini": "pdue-aoai-001-gpt4o-mini",
        "gpt-4o": "pdue-aoai-004-gpt4o",
    },
    "fallback_region": {
        "o4-mini": "dvue-aoai-001-o4-mini",
        "o3-mini": "dvue-aoai-001-o3mini",
        "o3": "dvue-aoai-001-o3",
        "o1-mini": "dvue-aoai-001-o1mini",
        "o1": "dvue-aoai-001-o1",
        "gpt-4.1-mini": "dvue-aoai-001-gpt-4.1-mini",
        "gpt-4.1": "dvue-aoai-001-gpt-4.1",
    }
}




def get_deployment_name(model: str) -> str:
    """Get deployment name for a model, trying main region first."""
    if model in MODEL_DEPLOYMENTS["main_region"]:
        return MODEL_DEPLOYMENTS["main_region"][model]
    if model in MODEL_DEPLOYMENTS["fallback_region"]:
        return MODEL_DEPLOYMENTS["fallback_region"][model]
    # Default fallback
    return f"pdue-aoai-002-{model}"




def get_client() -> openai.AzureOpenAI:
    """Create LLM gateway client."""
    deployment = get_deployment_name(settings.LLM_MODEL)


    return openai.AzureOpenAI(
        api_key=settings.OPENAI_API_KEY,
        azure_endpoint=settings.LLM_ENDPOINT,
        azure_deployment=deployment,
        api_version=settings.LLM_API_VERSION,
        default_headers={
            "Ocp-Apim-Subscription-Key": settings.LLM_API_KEY,
            "user": os.getenv("USER", "factcheck-bot")
        }
    )




async def generate_explanation(
    video_info: VideoInfo,
    creator_titles: list[str],
    creator_analysis: dict,
    fact_checks: list[FactCheckResult],
    search_results: list[SearchResult]
) -> str:
    """Generate grandmother-friendly explanation using LLM gateway."""


    if not settings.LLM_API_KEY:
        return _fallback_response(video_info, fact_checks, search_results)


    # Build context for LLM
    fact_check_text = ""
    if fact_checks:
        fact_check_text = "\n".join([
            f"- {fc.publisher}: rated '{fc.rating}' - {fc.url}"
            for fc in fact_checks
        ])
    else:
        fact_check_text = "No formal fact-checks found for this claim."


    search_text = ""
    if search_results:
        search_text = "\n".join([
            f"- {sr.title}: {sr.snippet[:100]}... ({sr.url})"
            for sr in search_results
        ])
    else:
        search_text = "No coverage found on trusted news sites."


    channel_text = ""
    if creator_analysis.get("is_suspect"):
        channel_text = f"CHANNEL PATTERN WARNING: {creator_analysis['reason']}"
    if creator_titles:
        channel_text += f"\nRecent videos from this creator: {creator_titles[:5]}"


    user_prompt = f"""
VIDEO PLATFORM: {video_info.platform.value.upper()}
VIDEO TITLE: {video_info.title}
CREATOR: {video_info.creator}
DESCRIPTION: {video_info.description[:500]}


{f"TRANSCRIPT EXCERPT: {video_info.transcript[:1000]}" if video_info.transcript else "TRANSCRIPT: Not available"}


{channel_text}


FACT-CHECK RESULTS:
{fact_check_text}


TRUSTED NEWS SEARCH:
{search_text}


---
Generate a response the family member can share directly with grandmother. Remember: brief, gentle, sourced.
"""


    try:
        client = get_client()


        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )


        return response.choices[0].message.content


    except Exception as e:
        if settings.DEBUG:
            print(f"LLM Error: {e}")
        return _fallback_response(video_info, fact_checks, search_results)




def _fallback_response(
    video_info: VideoInfo,
    fact_checks: list[FactCheckResult],
    search_results: list[SearchResult]
) -> str:
    """Generate a basic response without LLM."""
    parts = [f"I looked into the video: \"{video_info.title}\""]


    if fact_checks:
        fc = fact_checks[0]
        parts.append(f"\n\n{fc.publisher} has rated this claim as: {fc.rating}")
        parts.append(f"Source: {fc.url}")
    elif search_results:
        parts.append("\n\nI couldn't find a formal fact-check, but here's what trusted sources say:")
        for sr in search_results[:2]:
            parts.append(f"- {sr.title} ({sr.url})")
    else:
        parts.append("\n\nI couldn't find any coverage of this from trusted news sources.")
        parts.append("That doesn't mean it's false, but it means major outlets haven't reported on it.")
        parts.append("I'd wait for more information before worrying.")


    return "\n".join(parts)





