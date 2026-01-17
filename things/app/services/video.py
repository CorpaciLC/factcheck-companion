import re
import yt_dlp
from typing import Optional
from app.models import Platform, VideoInfo




def detect_platform(url: str) -> Platform:
    """Detect if URL is YouTube, TikTok, or unknown."""
    youtube_patterns = [
        r'(youtube\.com/watch\?v=)',
        r'(youtu\.be/)',
        r'(youtube\.com/shorts/)',
    ]
    tiktok_patterns = [
        r'(tiktok\.com/@[\w.-]+/video/)',
        r'(tiktok\.com/t/)',
        r'(vm\.tiktok\.com/)',
    ]


    for pattern in youtube_patterns:
        if re.search(pattern, url):
            return Platform.YOUTUBE


    for pattern in tiktok_patterns:
        if re.search(pattern, url):
            return Platform.TIKTOK


    return Platform.UNKNOWN




def extract_url_from_message(message: str) -> Optional[str]:
    """Extract first URL from a message."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, message)
    return match.group(0) if match else None




async def get_video_info(url: str) -> VideoInfo:
    """Extract metadata from YouTube or TikTok video using yt-dlp."""
    platform = detect_platform(url)


    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)


    # Common fields
    video_id = info.get('id', '')
    title = info.get('title', '')
    description = info.get('description', '')[:1500] if info.get('description') else ''
    view_count = info.get('view_count')
    upload_date = info.get('upload_date')


    # Platform-specific fields
    if platform == Platform.YOUTUBE:
        creator = info.get('channel', info.get('uploader', 'Unknown'))
        creator_id = info.get('channel_id', info.get('uploader_id'))
        hashtags = info.get('tags', [])[:10]
        transcript = await _get_youtube_transcript(video_id)
    elif platform == Platform.TIKTOK:
        creator = info.get('creator', info.get('uploader', 'Unknown'))
        creator_id = info.get('creator_id', info.get('uploader_id'))
        # TikTok hashtags are often in description
        hashtags = re.findall(r'#(\w+)', description)[:10]
        transcript = None  # Would need Whisper for TikTok audio
    else:
        creator = info.get('uploader', 'Unknown')
        creator_id = info.get('uploader_id')
        hashtags = []
        transcript = None


    return VideoInfo(
        platform=platform,
        url=url,
        video_id=video_id,
        title=title,
        creator=creator,
        creator_id=creator_id,
        description=description,
        transcript=transcript,
        view_count=view_count,
        upload_date=upload_date,
        hashtags=hashtags,
    )




async def _get_youtube_transcript(video_id: str) -> Optional[str]:
    """Get transcript for YouTube video. Tries multiple languages."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi


        # Try to get transcript - will auto-select available language
        try:
            # First try to get any available transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)


            # Prefer manual transcripts, then auto-generated
            transcript = None
            for t in transcript_list:
                if not t.is_generated:
                    transcript = t.fetch()
                    break


            if not transcript:
                # Fall back to any available (including auto-generated)
                for t in transcript_list:
                    transcript = t.fetch()
                    break


            if transcript:
                full_transcript = " ".join([t['text'] for t in transcript])
                return full_transcript[:5000]


        except Exception:
            # Fallback: try default method
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([t['text'] for t in transcript_list])
            return full_transcript[:5000]


    except Exception as e:
        print(f"Transcript error: {e}")
        return None




async def get_creator_history(creator_id: str, platform: Platform) -> list[str]:
    """Get recent video titles from creator to detect doom patterns."""
    if not creator_id:
        return []


    try:
        if platform == Platform.YOUTUBE:
            channel_url = f"https://www.youtube.com/channel/{creator_id}/videos"
        elif platform == Platform.TIKTOK:
            # TikTok creator pages are harder to scrape reliably
            # For MVP, we'll skip this
            return []
        else:
            return []


        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'playlist_items': '1-10'
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)


        return [v.get('title', '') for v in info.get('entries', []) if v.get('title')]


    except Exception:
        return []




def analyze_creator_pattern(titles: list[str]) -> dict:
    """Analyze if creator has a pattern of doom/catastrophe content."""
    if not titles:
        return {"is_suspect": False, "reason": None}


    doom_keywords = [
        'end of', 'collapse', 'catastrophe', 'disaster', 'warning',
        'urgent', 'emergency', 'crisis', 'apocalypse', 'doom',
        'they don\'t want you to know', 'wake up', 'truth about',
        'exposed', 'shocking', 'you won\'t believe', 'must watch',
        'before it\'s too late', 'happening now', 'breaking'
    ]


    doom_count = 0
    for title in titles:
        title_lower = title.lower()
        if any(kw in title_lower for kw in doom_keywords):
            doom_count += 1


    # If more than 50% of recent videos are doom-y, flag the channel
    if len(titles) > 0 and (doom_count / len(titles)) > 0.5:
        return {
            "is_suspect": True,
            "reason": f"{doom_count} of {len(titles)} recent videos use alarmist language"
        }


    return {"is_suspect": False, "reason": None}





