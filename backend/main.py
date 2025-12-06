"""
Backend API for TubeTranscript.

This module provides endpoints to fetch YouTube video transcripts and available languages.
It uses the youtube_transcript_api library to retrieve data.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = FastAPI(title="TubeTranscript API", version="1.2.0")

class VideoRequest(BaseModel):
    """Request model for video operations."""
    video_url_or_id: str
    lang: str = "fr"

class LanguageInfo(BaseModel):
    """Model representing a single language option."""
    language_code: str
    language_name: str
    is_generated: bool

class AvailableLanguagesResponse(BaseModel):
    """Response model for available languages."""
    video_id: str
    manual_transcripts: List[LanguageInfo]
    generated_transcripts: List[LanguageInfo]

class TranscriptSegment(BaseModel):
    """Model representing a single segment of the transcript."""
    start: float
    duration: float
    text: str

class TranscriptResponse(BaseModel):
    """Response model for the full transcript."""
    video_id: str
    text: str
    language: str
    is_generated: bool
    segments: List[TranscriptSegment]

def extract_video_id(url_or_id: str) -> str:
    """
    Extracts the YouTube video ID from a URL or returns the ID if provided directly.

    Args:
        url_or_id (str): The YouTube URL or video ID.

    Returns:
        str: The extracted video ID.
    """
    if "v=" in url_or_id:
        return url_or_id.split("v=")[1].split("&")[0]
    if "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[1].split("?")[0]
    return url_or_id

@app.post("/languages", response_model=AvailableLanguagesResponse)
async def get_available_languages(request: VideoRequest):
    """
    Retrieves the list of available languages (manual and generated) for a given video.

    Args:
        request (VideoRequest): The request object containing the video URL or ID.

    Returns:
        AvailableLanguagesResponse: An object containing lists of manual and generated languages.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    video_id = extract_video_id(request.video_url_or_id)
    try:
        ytt_api = YouTubeTranscriptApi()

        transcript_list = ytt_api.list(video_id)
        
        manual_transcripts = []
        generated_transcripts = []

        for t in transcript_list:
            info = LanguageInfo(
                language_code=t.language_code,
                language_name=t.language,
                is_generated=t.is_generated
            )
            if t.is_generated:
                generated_transcripts.append(info)
            else:
                manual_transcripts.append(info)

        return AvailableLanguagesResponse(
            video_id=video_id,
            manual_transcripts=manual_transcripts,
            generated_transcripts=generated_transcripts
        )
    except (TranscriptsDisabled, NoTranscriptFound):
        return AvailableLanguagesResponse(
            video_id=video_id,
            manual_transcripts=[],
            generated_transcripts=[]
        )
    except Exception as e:
        print(f"Error fetching languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcript", response_model=TranscriptResponse)
async def get_transcript(request: VideoRequest):
    """
    Retrieves the transcript for a specific video and language.

    Args:
        request (VideoRequest): The request object containing the video URL/ID and target language.

    Returns:
        TranscriptResponse: The transcript data including text and segments.

    Raises:
        HTTPException: If transcripts are disabled, not found, or another error occurs.
    """
    video_id = extract_video_id(request.video_url_or_id)
    ytt_api = YouTubeTranscriptApi()
    print(f"Processing video ID: {video_id} for language: {request.lang}")
    target_lang = request.lang

    try:
        # On utilise la méthode Factory
        transcript_list = ytt_api.list(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript([target_lang])
        except:
            transcript = transcript_list.find_transcript(['en'])
            transcript = transcript.translate(target_lang)

        transcript_data = transcript.fetch()
        
        segments = []
        for t in transcript_data:
            segments.append(TranscriptSegment(
                start=t.start,
                duration=t.duration,
                text=t.text
            ))

        full_text = " ".join([s.text for s in segments])
        
        return TranscriptResponse(
            video_id=video_id,
            text=full_text,
            language=transcript.language_code,
            is_generated=transcript.is_generated,
            segments=segments
        )

    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Sous-titres désactivés sur cette vidéo.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="Aucun sous-titre trouvé.")
    except Exception as e:
        print(f"CRITICAL ERROR: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=str(e))