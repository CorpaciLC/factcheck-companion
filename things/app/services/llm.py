import os
import openai
import app.config as config
from app.models import VideoInfo, FactCheckResult, SearchResult




SYSTEM_PROMPT = """You are a high-signal fact-checking assistant for a busy top performer.


Your task:
1. ANALYZE the video transcript for specific factual claims
2. IDENTIFY which claims are verifiable and which are speculation/opinion
3. CHECK each major claim against the fact-check results and news sources provided
4. EXPLAIN what's accurate, what's misleading, and what's false


For each major claim you find, assess:
- Is this claim verifiable or just opinion/speculation?
- Does evidence support or contradict it?
- Is it missing important context?
- Is it exaggerated or sensationalized?


Then write a message the user can copy-paste that:
- Starts with the bottom line (1 sentence)
- Lists the 2-3 key claims and whether evidence supports them
- Cites sources when available
- Is calm, respectful, and non-pushy
- Is brief (150-200 words max)


If the video contains multiple false claims, focus on the 2-3 most important ones.
If the channel has a pattern of doom content, mention it gently.
If you're uncertain, say so plainly and avoid strong conclusions.


Format: Simple language, no jargon. Write as a single message."""




# Model to deployment mapping (from 's internal setup)
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




def _openrouter_headers() -> dict:
    headers: dict[str, str] = {}
    if config.settings.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = config.settings.OPENROUTER_SITE_URL
    if config.settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = config.settings.OPENROUTER_APP_NAME
    return headers


def get_openrouter_client() -> openai.OpenAI:
    """Create an OpenRouter client (OpenAI-compatible)."""
    return openai.OpenAI(
        api_key=config.settings.OPENROUTER_API_KEY,
        base_url=config.settings.OPENROUTER_BASE_URL,
        default_headers=_openrouter_headers(),
    )


def get_openai_client() -> openai.OpenAI:
    """Create a direct OpenAI client."""
    return openai.OpenAI(api_key=config.settings.OPENAI_API_KEY)


def get_azure_client() -> openai.AzureOpenAI:
    """Create an Azure OpenAI client."""
    deployment = get_deployment_name(config.settings.LLM_MODEL)
    return openai.AzureOpenAI(
        api_key=config.settings.LLM_API_KEY,
        azure_endpoint=config.settings.LLM_ENDPOINT,
        azure_deployment=deployment,
        api_version=config.settings.LLM_API_VERSION,
        default_headers={
            # Some Azure APIM gateways require this header.
            "Ocp-Apim-Subscription-Key": config.settings.LLM_API_KEY,
            "user": os.getenv("USER", "factcheck-bot"),
        },
    )


def get_llm_client_and_model() -> tuple[object, str, str]:
    """Return (client, model, provider). Provider is 'openai' | 'openrouter' | 'azure'."""
    provider = (config.settings.LLM_PROVIDER or "auto").strip().lower()

    if provider == "openai":
        if not config.settings.OPENAI_API_KEY:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set")
        model = config.settings.OPENAI_MODEL or "gpt-4o-mini"
        return get_openai_client(), model, "openai"

    if provider == "openrouter":
        if not config.settings.OPENROUTER_API_KEY:
            raise RuntimeError("LLM_PROVIDER=openrouter but OPENROUTER_API_KEY is not set")
        model = config.settings.OPENROUTER_MODEL or "openai/gpt-4o-mini"
        return get_openrouter_client(), model, "openrouter"

    if provider == "azure":
        if not (config.settings.LLM_API_KEY and config.settings.LLM_ENDPOINT):
            raise RuntimeError("LLM_PROVIDER=azure but LLM_API_KEY/LLM_ENDPOINT are not set")
        return get_azure_client(), config.settings.LLM_MODEL, "azure"

    # auto
    if config.settings.OPENAI_API_KEY:
        model = config.settings.OPENAI_MODEL or "gpt-4o-mini"
        return get_openai_client(), model, "openai"
    if config.settings.LLM_API_KEY and config.settings.LLM_ENDPOINT:
        return get_azure_client(), config.settings.LLM_MODEL, "azure"
    if config.settings.OPENROUTER_API_KEY:
        model = config.settings.OPENROUTER_MODEL or "openai/gpt-4o-mini"
        return get_openrouter_client(), model, "openrouter"

    raise RuntimeError("No LLM configured (set OPENROUTER_API_KEY or LLM_API_KEY+LLM_ENDPOINT)")




async def generate_explanation(
    video_info: VideoInfo,
    creator_titles: list[str],
    creator_analysis: dict,
    fact_checks: list[FactCheckResult],
    search_results: list[SearchResult]
) -> str:
    """Generate grandmother-friendly explanation using 's LLM gateway."""

    # If no provider is configured, return a non-LLM fallback instead of failing the pipeline.
    if not (
        config.settings.OPENAI_API_KEY
        or config.settings.OPENROUTER_API_KEY
        or (config.settings.LLM_API_KEY and config.settings.LLM_ENDPOINT)
    ):
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


    # Use more transcript if available
    transcript_section = ""
    if video_info.transcript:
        transcript_section = f"""
VIDEO TRANSCRIPT (analyze this for factual claims):
\"\"\"
{video_info.transcript[:3000]}
\"\"\"
"""
    else:
        transcript_section = """
TRANSCRIPT: Not available - analyze based on title and description only.
"""


    user_prompt = f"""
VIDEO PLATFORM: {video_info.platform.value.upper()}
VIDEO TITLE: {video_info.title}
CREATOR: {video_info.creator}
VIDEO DESCRIPTION: {video_info.description[:800]}


{transcript_section}


{channel_text}


EXISTING FACT-CHECK RESULTS (from fact-check databases):
{fact_check_text}


TRUSTED NEWS COVERAGE:
{search_text}


---
INSTRUCTIONS:
1. First, identify the 2-3 main claims made in the video (from transcript/title/description)
2. Then, analyze each claim for accuracy
3. Finally, write a brief, gentle response for grandmother explaining what's true/false/misleading


Generate the response now:
"""


    try:
        if config.settings.DEBUG:
            print(f"[LLM] Provider setting: {config.settings.LLM_PROVIDER}")
            print(f"[LLM] Transcript available: {bool(video_info.transcript)}")
            if video_info.transcript:
                print(f"[LLM] Transcript length: {len(video_info.transcript)} chars")

        client, model, provider = get_llm_client_and_model()
        if config.settings.DEBUG:
            print(f"[LLM] Using provider: {provider}")
            print(f"[LLM] Using model: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )


        result = response.choices[0].message.content
        if config.settings.DEBUG:
            print(f"[LLM] Success! Response length: {len(result)} chars")


        return result


    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
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





