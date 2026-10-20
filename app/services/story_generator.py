import logging
from dataclasses import dataclass, field, replace

from app.clients.llm_client import GenerationParams, LLMClient, LLMError
from app.schemas.story_schema import StoryRequest
from app.services import safety, story_validation
from app.services.scene_writer import StoryBrief, write_story_by_scenes

logger = logging.getLogger(__name__)

FALLBACK_NAME = "Pip"
DEFAULT_THEME = "Daily"
DEFAULT_MOOD = "Calm"
MIN_LENGTH_RATIO = 0.85


class StoryGenerationError(RuntimeError):
    def __init__(self, message: str, flags: list[str]) -> None:
        super().__init__(message)
        self.flags = flags


@dataclass(frozen=True)
class GeneratedStory:
    title: str
    content: str
    attempts: int
    word_count: int
    flags: list[str] = field(default_factory=list)
    output_tokens: int = 0
    generation_seconds: float = 0.0


def _label(value: str, default: str, field_name: str, flags: list[str]) -> str:
    cleaned = safety.clean_text(value)
    if not cleaned:
        return default
    if not safety.is_valid_label(cleaned):
        flags.append(f"{field_name}_replaced")
        return default
    return cleaned


def build_brief(request: StoryRequest) -> tuple[StoryBrief, list[str]]:
    flags: list[str] = []

    name = safety.clean_text(request.character_name)
    if not safety.is_valid_name(name):
        flags.append("name_replaced")
        name = FALLBACK_NAME

    theme = _label(request.theme, DEFAULT_THEME, "theme", flags)
    mood = _label(request.mood, DEFAULT_MOOD, "mood", flags)

    idea = safety.clean_text(request.description)
    if len(idea.split()) > safety.MAX_DESCRIPTION_WORDS:
        flags.append("idea_truncated")
        idea = safety.truncate_words(idea, safety.MAX_DESCRIPTION_WORDS)
    if idea and not safety.is_safe_idea(idea):
        flags.append("idea_dropped")
        idea = ""

    return StoryBrief(name, theme, mood, request.length_minutes, idea), flags


class StoryGenerator:
    def __init__(
        self,
        llm: LLMClient,
        words_per_minute: int = 120,
        max_attempts: int = 3,
        params: GenerationParams = GenerationParams(),
    ) -> None:
        self._llm = llm
        self._words_per_minute = words_per_minute
        self._max_attempts = max_attempts
        self._params = params

    async def generate(self, request: StoryRequest) -> GeneratedStory:
        brief, flags = build_brief(request)
        target_words = brief.length_minutes * self._words_per_minute
        tokens = 0
        seconds = 0.0

        for attempt in range(1, self._max_attempts + 1):
            try:
                written = await write_story_by_scenes(
                    self._llm, brief, target_words, self._params, MIN_LENGTH_RATIO
                )
            except LLMError as exc:
                flags.append("retry:llm_error")
                logger.warning("attempt %d/%d: LLM error: %s", attempt, self._max_attempts, exc)
                continue

            tokens += written.output_tokens
            seconds += written.generation_seconds

            title, title_fixes = story_validation.repair_glitches(story_validation.normalize_quotes(written.title))
            content, content_fixes = story_validation.repair_glitches(story_validation.normalize_quotes(written.content))
            title, title_names = story_validation.repair_truncated_name(title, brief.character_name)
            content, content_names = story_validation.repair_truncated_name(content, brief.character_name)
            fixes = title_fixes + content_fixes + title_names + content_names
            if fixes:
                flags.append(f"repaired:{fixes}")

            problems = story_validation.find_problems(title, content)
            if not problems:
                words = len(content.split())
                logger.info(
                    "story generated: attempts=%d words=%d tokens=%d flags=%s",
                    attempt, words, tokens, flags,
                )
                return GeneratedStory(title, content, attempt, words, flags, tokens, seconds)

            flags.extend(f"retry:{p}" for p in problems)
            logger.warning("attempt %d/%d rejected: %s", attempt, self._max_attempts, problems)
            if "banned" in problems:
                brief = replace(brief, idea="")

        raise StoryGenerationError(
            f"Gagal membuat cerita setelah {self._max_attempts} percobaan", flags + ["output_blocked"]
        )
