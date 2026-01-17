"""
WhatsApp Webhook Handler


Receives messages from Twilio, processes video URLs,
and returns fact-check explanations.
"""


from fastapi import APIRouter, Request, Response, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


from app.config import settings
from app.services.video import extract_url_from_message, detect_platform
from app.services import database
from app.models import Platform
from app.pipeline import research_video




router = APIRouter()




# Welcome message for first-time users or non-URL messages
def get_welcome_message() -> str:
    """Generate welcome message, including dashboard link if configured."""
    base_message = """Hi! I'm here to help you check if videos are trustworthy.


Just send me a YouTube or TikTok link, and I'll:
1. Check what the video claims
2. Look for fact-checks from trusted sources
3. Give you a clear, sourced explanation


Try sending a link now!"""


    if settings.DASHBOARD_URL:
        base_message += f"\n\n📊 See all checked videos: {settings.DASHBOARD_URL}"


    return base_message




NO_URL_MESSAGE = """I didn't see a video link in your message.


Send me a YouTube or TikTok URL and I'll research it for you."""




PROCESSING_MESSAGE = """Got it! I'm researching this video now.


I'll check:
- What the video claims
- The creator's content history
- Fact-check databases
- Trusted news sources


Give me a moment..."""




UNSUPPORTED_PLATFORM = """I can only check YouTube and TikTok videos right now.


Send me a link from one of those platforms and I'll help!"""




@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages from Twilio.
    """
    form = await request.form()
    incoming_msg = form.get("Body", "").strip()
    sender = form.get("From", "")


    # Extract URL from message
    url = extract_url_from_message(incoming_msg)


    resp = MessagingResponse()


    if not url:
        # No URL found - send help message
        if incoming_msg.lower() in ["hi", "hello", "hey", "start", "help"]:
            resp.message(get_welcome_message())
        else:
            resp.message(NO_URL_MESSAGE)
        return Response(content=str(resp), media_type="application/xml")


    # Check platform
    platform = detect_platform(url)
    if platform == Platform.UNKNOWN:
        resp.message(UNSUPPORTED_PLATFORM)
        return Response(content=str(resp), media_type="application/xml")


    # For fast response, we could:
    # 1. Reply immediately with "processing" message
    # 2. Process in background and send follow-up


    # For hackathon simplicity, we'll do synchronous processing
    # (In production, use background tasks + follow-up message)


    try:
        result = await research_video(url)


        # Log to public database (no PII - phone number not passed)
        await database.log_query_from_result(result)


        # Build response
        response_parts = [result.explanation]


        # Add confidence indicator
        if result.confidence == "high":
            response_parts.append("\n\n[Confidence: High - formal fact-check found]")
        elif result.confidence == "medium":
            response_parts.append("\n\n[Confidence: Medium - trusted news coverage found]")
        else:
            response_parts.append("\n\n[Confidence: Low - limited information available]")


        # Add warning if channel is suspect
        if result.channel_is_suspect:
            response_parts.append("\n[Note: This creator frequently posts alarmist content]")


        response_text = "".join(response_parts)


        # Twilio has a 1600 character limit per message
        if len(response_text) > 1500:
            response_text = response_text[:1497] + "..."


        resp.message(response_text)


    except Exception as e:
        error_msg = (
            "Sorry, I had trouble analyzing that video. "
            "Please try again, or try a different link."
        )
        if settings.DEBUG:
            error_msg += f"\n\nDebug: {str(e)}"
        resp.message(error_msg)


    return Response(content=str(resp), media_type="application/xml")




@router.get("/webhook")
async def webhook_verify(request: Request):
    """
    Verification endpoint for Twilio webhook setup.
    """
    return {"status": "ok", "message": "Webhook is active"}




# Optional: Background processing for long-running requests
async def process_and_reply(url: str, sender: str):
    """
    Process video in background and send follow-up message.
    Use this for production to avoid Twilio timeouts.
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return


    try:
        result = await research_video(url)


        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


        client.messages.create(
            body=result.explanation[:1500],
            from_=settings.TWILIO_PHONE_NUMBER,
            to=sender
        )
    except Exception:
        pass  # Log in production





