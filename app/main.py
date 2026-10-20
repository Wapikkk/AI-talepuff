import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.audio_routes import router as audio_router
from app.api.story_routes import router as story_router
from app.clients.factory import build_http_client, build_llm_client
from app.core.config import Settings
from app.core.warmup import warm_up_quietly
from app.services.story_generator import StoryGenerator


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()
    async with build_http_client(settings) as http:
        llm = build_llm_client(settings, http)
        app.state.story_generator = StoryGenerator(
            llm,
            words_per_minute=settings.words_per_minute,
            max_attempts=settings.max_attempts,
        )
        warmup = asyncio.create_task(warm_up_quietly(llm))
        try:
            yield
        finally:
            warmup.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await warmup


app = FastAPI(lifespan=lifespan)

app.mount("/audio", StaticFiles(directory="audio_output"), name="audio")
app.include_router(story_router)
app.include_router(audio_router)


@app.get("/")
def read_root():
    return {"Status": "Server AI TalePuff On!"}
