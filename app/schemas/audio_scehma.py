from pydantic import BaseModel

class AudioRequest(BaseModel):
    story_text: str
    voice_tone: str