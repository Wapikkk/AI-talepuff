from fastapi import FastAPI
from app.api.story_routes import router as story_router

app = FastAPI()

app.include_router(story_router)

@app.get("/")
def read_root():
    return {"Status": "Server AI TalePuff On!"}