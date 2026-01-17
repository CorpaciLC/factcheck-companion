#!/usr/bin/env python3
"""
Local test script - test the pipeline without WhatsApp.


Usage:
    python test_local.py "https://youtube.com/watch?v=..."
    python test_local.py "https://tiktok.com/@user/video/..."
"""


import asyncio
import sys
from dotenv import load_dotenv


load_dotenv()


from app.pipeline import research_video
from app.services.video import detect_platform




async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_local.py <youtube_or_tiktok_url>")
        print("\nExample:")
        print("  python test_local.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)


    url = sys.argv[1]
    platform = detect_platform(url)


    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"Platform detected: {platform.value}")
    print(f"{'='*60}\n")


    print("Running research pipeline...")
    print("(This may take 10-30 seconds)\n")


    try:
        result = await research_video(url)


        print(f"{'='*60}")
        print("RESULT")
        print(f"{'='*60}")
        print(f"\nClaim: {result.claim}")
        print(f"Confidence: {result.confidence}")
        print(f"Channel suspect: {result.channel_is_suspect}")
        print(f"\nSources: {result.sources}")
        print(f"\n{'-'*60}")
        print("EXPLANATION (what the user would send):")
        print(f"{'-'*60}")
        print(f"\n{result.explanation}")
        print(f"\n{'='*60}\n")


    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()




if __name__ == "__main__":
    asyncio.run(main())





