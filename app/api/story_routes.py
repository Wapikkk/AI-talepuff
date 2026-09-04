from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import StoryRequest
from app.services.llm_service import generate_story_from_ollama
from app.services.tts_service import convert_text_to_audio
import time

router = APIRouter()

@router.post("/generate_story")
async def generate_story(req: StoryRequest):
    try:
        story_text = generate_story_from_ollama(req.category, req.sentiment)

        file_name = f"story_{int(time.time())}.mp3"

        await convert_text_to_audio(story_text, file_name)

        audio_url = f"http://localhost:8000/audio/{file_name}"

        return {
            "status": "success",
            "story": story_text, 
            "audio_url": audio_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))