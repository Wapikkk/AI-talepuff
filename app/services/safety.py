import re

MAX_NAME_CHARS = 30
MAX_DESCRIPTION_WORDS = 30

_BANNED_ENGLISH = [
    r"kill(s|ed|ing|er)?", r"murder(s|ed|ing|er)?", r"blood(y)?", r"dead", r"death",
    r"die(s|d)?", r"dying", r"suicide", r"corpse(s)?", r"gun(s)?", r"knife|knives",
    r"stab(s|bed|bing)?", r"shoot(s|ing)?", r"shot", r"weapon(s)?", r"bomb(s)?",
    r"torture(d)?", r"rape(d)?", r"sex(y|ual)?", r"naked", r"nude", r"drug(s)?",
    r"alcohol", r"beer", r"wine", r"cigarette(s)?", r"hell", r"demon(s)?", r"devil",
    r"horror", r"fuck(ing|ed)?", r"shit(ty)?", r"bitch", r"bastard", r"damn",
]
_BANNED_INDONESIAN = [
    r"bunuh", r"membunuh", r"pembunuhan", r"darah", r"mayat", r"senjata", r"pistol",
    r"pisau", r"bom", r"narkoba", r"telanjang", r"seks", r"setan", r"bangsat",
    r"bajingan", r"kontol", r"memek", r"ngentot",
]
_BANNED_RE = re.compile(
    r"\b(" + "|".join(_BANNED_ENGLISH + _BANNED_INDONESIAN) + r")\b", re.IGNORECASE
)

_INJECTION_RE = re.compile(
    r"(ignore|disregard|forget)\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)?\s*"
    r"(instruction|rule|prompt)s?"
    r"|system\s+prompt"
    r"|abaikan\s+(semua\s+)?(aturan|instruksi|perintah)"
    r"|do\s+not\s+use\s+json"
    r"|reply\s+in\s+",
    re.IGNORECASE,
)

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_NAME_ALLOWED = re.compile(r"^[A-Za-z][A-Za-z' \-]*$")
_PII_RE = re.compile(r"\b\d{6,}\b")


def find_banned_terms(text: str) -> list[str]:
    """Daftar kata terlarang yang ditemukan di `text` (huruf kecil, tanpa duplikat)."""
    return sorted({m.group(0).lower() for m in _BANNED_RE.finditer(text)})


def looks_like_injection(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))


def contains_pii(text: str) -> bool:
    """Deteksi kasar: deretan angka panjang (nomor telepon, dsb.)."""
    return bool(_PII_RE.search(text))


def clean_text(text: str) -> str:
    """Buang karakter kontrol dan rapikan spasi."""
    return " ".join(_CONTROL_CHARS.sub(" ", text).split())


def truncate_words(text: str, max_words: int) -> str:
    return " ".join(text.split()[:max_words])


def is_valid_name(name: str) -> bool:
    """Nama karakter: huruf, spasi, apostrof, tanda hubung; panjang terbatas."""
    return (
        0 < len(name) <= MAX_NAME_CHARS
        and bool(_NAME_ALLOWED.match(name))
        and not find_banned_terms(name)
    )


def is_safe_idea(text: str) -> bool:
    """Apakah deskripsi bebas aman dimasukkan ke prompt apa adanya."""
    return not (find_banned_terms(text) or looks_like_injection(text) or contains_pii(text))
