from fastapi import APIRouter, HTTPException
from app.schemas.audio_scehma import AudioRequest
from app.services.tts_service import convert_text_to_audio
import os
import time

router = APIRouter()

@router.post("/generate_audio")
async def generate_audio(req: AudioRequest):
    try:
        file_name = f"story_{int(time.time())}_{req.voice_tone}.mp3"

        saved_file_path = await convert_text_to_audio(req.story_text, req.voice_tone, file_name)

        final_wav_name = os.path.basename(saved_file_path)

        audio_url = f"http://localhost:8000/audio/{final_wav_name}"

        return {
            "status": "success",
            "audio_url": audio_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))