from fastapi import APIRouter, HTTPException
from app.schemas.story_schema import StoryRequest
from app.services.llm_service import generate_story_from_ollama

router = APIRouter()

@router.post("/generate_story")
def generate_story(req: StoryRequest):
    try:
        story_text = generate_story_from_ollama(req.category, req.sentiment)
        return {"status": "success", "story": story_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))