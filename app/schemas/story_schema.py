from pydantic import BaseModel

class StoryRequest(BaseModel):
    category: str
    sentiment: str