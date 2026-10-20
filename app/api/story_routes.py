import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.story_schema import StoryRequest, StoryResponse
from app.services.story_generator import StoryGenerationError, StoryGenerator

logger = logging.getLogger(__name__)
router = APIRouter()


def get_story_generator(request: Request) -> StoryGenerator:
    return request.app.state.story_generator


@router.post("/generate_story", response_model=StoryResponse)
async def generate_story(
    req: StoryRequest,
    generator: StoryGenerator = Depends(get_story_generator),
) -> StoryResponse:
    try:
        story = await generator.generate(req)
    except StoryGenerationError as exc:
        logger.error("story generation failed: %s flags=%s", exc, exc.flags)
        raise HTTPException(status_code=502, detail="Story generation failed") from exc

    return StoryResponse(
        title=story.title,
        response=story.content,
        word_count=story.word_count,
        attempts=story.attempts,
        flags=story.flags,
    )
