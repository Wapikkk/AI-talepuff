from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import StoryRequest
from app.services.llm_service import generate_story_from_ollama
router = APIRouter()

@router.post("/generate_story")
async def generate_story(req: StoryRequest):
    try:
        target_words = req.length_minutes * 120
        title, story_text = generate_story_from_ollama(
            character_name=req.character_name,
            theme=req.theme,
            mood=req.mood,
            length_minutes=req.length_minutes,
            language=req.language,
            description=req.description
        )

        return {
            "status": "success",
            "title": title,
            "response": story_text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))