from pydantic import BaseModel
from typing import Optional
from enum import Enum




class Platform(str, Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"




class VideoInfo(BaseModel):
    platform: Platform
    url: str
    video_id: str
    title: str
    creator: str
    creator_id: Optional[str] = None
    description: str = ""
    transcript: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    hashtags: list[str] = []




class FactCheckResult(BaseModel):
    claim: str
    claimant: Optional[str] = None
    rating: str
    publisher: str
    url: str




class SearchResult(BaseModel):
    title: str
    snippet: str
    url: str




class ResearchResult(BaseModel):
    claim: str
    confidence: str  # "high", "medium", "low"
    explanation: str
    sources: list[str]
    platform: Platform
    channel_is_suspect: bool = False
    # Additional fields for logging (not sent to user)
    video_url: str = ""
    video_title: str = ""
    video_creator: str = ""
    claim_extracted: str = ""
    fact_checks_found: int = 0
    search_results_found: int = 0





