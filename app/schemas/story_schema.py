from pydantic import BaseModel, ConfigDict, Field


class StoryRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    character_name: str = Field(min_length=1, max_length=100)
    theme: str = Field(default="", max_length=100)
    mood: str = Field(default="", max_length=200)
    length_minutes: int = Field(ge=1, le=10)
    language: str = Field(default="", max_length=50)
    description: str = Field(default="", max_length=1000)


class StoryResponse(BaseModel):
    status: str = "success"
    title: str
    response: str
    word_count: int
    attempts: int
    flags: list[str]
