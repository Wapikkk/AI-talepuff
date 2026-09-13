from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.story_routes import router as story_router
from app.api.audio_routes import router as audio_router

app = FastAPI()

app.mount("/audio", StaticFiles(directory="audio_output"), name="audio")
app.include_router(story_router)
app.include_router(audio_router)

@app.get("/")
def read_root():
    return {"Status": "Server AI TalePuff On!"}