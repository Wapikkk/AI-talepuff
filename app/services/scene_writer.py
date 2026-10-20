import json
import math
from dataclasses import dataclass

from app.clients.llm_client import GenerationParams, LLMClient, LLMError
from app.services import prompts

WORDS_PER_SCENE = 25
MAX_EXTENSIONS = 2
EXTRA_SCENES_ALLOWED = 2
MIN_SCENES = 3


@dataclass(frozen=True)
class StoryBrief:

    character_name: str
    theme: str
    mood: str
    length_minutes: int
    idea: str


@dataclass(frozen=True)
class WrittenStory:
    title: str
    scenes: list[str]
    output_tokens: int = 0
    generation_seconds: float = 0.0

    @property
    def content(self) -> str:
        return "\n\n".join(self.scenes)


def scene_count(target_words: int) -> int:
    return max(MIN_SCENES, round(target_words / WORDS_PER_SCENE))


def scenes_schema(count: int, with_title: bool) -> dict:
    properties: dict = {
        "scenes": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": count,
            "maxItems": count + EXTRA_SCENES_ALLOWED,
        }
    }
    required = ["scenes"]
    if with_title:
        properties["title"] = {"type": "string"}
        required.insert(0, "title")
    return {"type": "object", "properties": properties, "required": required}


def parse_scenes(text: str) -> tuple[str, list[str]]:
    """Mengembalikan (title, scenes). Bila JSON rusak -> ("", [])."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return "", []
    if not isinstance(data, dict):
        return "", []
    raw = data.get("scenes", [])
    scenes = [str(s).strip() for s in raw if str(s).strip()] if isinstance(raw, list) else []
    return str(data.get("title", "")).strip(), scenes


def _word_count(scenes: list[str]) -> int:
    return sum(len(s.split()) for s in scenes)


async def write_story_by_scenes(
    llm: LLMClient,
    brief: StoryBrief,
    target_words: int,
    params: GenerationParams = GenerationParams(),
    min_length_ratio: float = 0.85,
    extend: bool = True,
) -> WrittenStory:
    count = scene_count(target_words)
    messages = [
        {"role": "system", "content": prompts.STORY_RULES},
        {
            "role": "user",
            "content": prompts.build_story_prompt(
                brief.character_name, brief.theme, brief.mood, brief.idea, target_words, count
            ),
        },
    ]
    first = await llm.chat(messages, schema=scenes_schema(count, with_title=True), params=params)
    title, scenes = parse_scenes(first.text)
    tokens = first.output_tokens
    seconds = first.generation_seconds
    if not scenes:
        return WrittenStory("", [], tokens, seconds)

    for _ in range(MAX_EXTENSIONS if extend else 0):
        words = _word_count(scenes)
        if words >= min_length_ratio * target_words:
            break
        extra = max(1, math.ceil((target_words - words) / WORDS_PER_SCENE))
        try:
            more = await llm.chat(
                messages + [
                    {"role": "assistant", "content": first.text},
                    {"role": "user", "content": prompts.build_extension_prompt(extra)},
                ],
                schema=scenes_schema(extra, with_title=False),
                params=params,
            )
        except LLMError:
            break
        tokens += more.output_tokens
        seconds += more.generation_seconds
        _, new_scenes = parse_scenes(more.text)
        if not new_scenes:
            break
        scenes = scenes[:-1] + new_scenes + scenes[-1:]

    return WrittenStory(title, scenes, tokens, seconds)
