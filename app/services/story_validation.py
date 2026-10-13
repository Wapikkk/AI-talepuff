import re

from app.services import safety

MIN_WORDS = 40
_GLITCH_REPLACEMENT = re.compile("�")
_GLITCH_SPACED_LETTERS = re.compile(r"\b(?:[A-Za-z] ){3,}[A-Za-z]\b")
_GLITCH_STRAY_LABEL = re.compile(r"(?<![\w'])[A-Z][a-z]{0,3}:(?=\s)")

_WORD = re.compile(r"[A-Za-z']+")


def count_glitches(text: str) -> int:
    return sum(
        len(pattern.findall(text))
        for pattern in (_GLITCH_REPLACEMENT, _GLITCH_SPACED_LETTERS, _GLITCH_STRAY_LABEL)
    )


def repair_glitches(text: str) -> tuple[str, int]:
    fixed = 0

    def count(match: re.Match, replacement: str) -> str:
        nonlocal fixed
        fixed += 1
        return replacement

    text = _GLITCH_REPLACEMENT.sub(lambda m: count(m, "'"), text)
    text = _GLITCH_SPACED_LETTERS.sub(lambda m: count(m, m.group(0).replace(" ", "")), text)
    text = _GLITCH_STRAY_LABEL.sub(lambda m: count(m, ""), text)
    return re.sub(r"[ \t]{2,}", " ", text).strip(), fixed


def find_problems(title: str, content: str) -> list[str]:
    problems: list[str] = []
    if not title or not content:
        problems.append("empty")
        return problems
    if len(_WORD.findall(content)) < MIN_WORDS:
        problems.append("too_short")
    if "<think>" in content.lower() or "<think>" in title.lower():
        problems.append("think_leak")
    if safety.find_banned_terms(f"{title} {content}"):
        problems.append("banned")
    if count_glitches(f"{title} {content}"):
        problems.append("glitch")
    return problems
