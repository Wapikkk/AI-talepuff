from pydantic import BaseModel

class StoryRequest(BaseModel):
    character_name: str
    theme: str
    mood: str
    length_minutes: int
    language: str
    description: str