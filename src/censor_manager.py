import re
import unicodedata
from typing import Optional

# src/censor_manager.py

CUSS_MAPPING = {
    "bitch": "itch",
    "bitches": "itches",
    "shit": "ship",
    "shitty": "shippy",
    "bullshit": "bullship",
    "fuck": "duck",
    "fucks": "ducks",
    "fucking": "ducking",
    "fucked": "ducked",
    "motherfucker": "mother-ducker",
    "motherfuckers": "mother-duckers",
    "damn": "darn",
    "dammit": "darnit",
    "ass": "ash",
    "asses": "ashes",
    "asshole": "ash-hole",
    "assholes": "ash-holes",
    "dick": "stick",
    "dicks": "sticks",
    "dickhead": "stickhead",
    "pussy": "kitty",
    "pussies": "kitties",
    "cock": "rooster",
    "cocks": "roosters",
    "nigga": "neighbor",
    "nigger": "neighbor",
    "hoe": "row",
    "hoes": "rows",
    "slut": "sleet",
    "sluts": "sleets",
    "whore": "shore",
    "whores": "shores",
    "bastard": "rascal",
    "bastards": "rascals",
    "crap": "crud",
    "crappy": "cruddy",
    "douche": "doof",
    "douchebag": "doofbag",
    "dumbass": "dumb-ash",
    "jackass": "jack-ash",
    "retard": "goof",
    "retarded": "goofy",
    "hell": "heck",
    "goddamn": "goshdarn",
    "tit": "tip",
    "tits": "tips",
    "boobs": "bobs",
    "balls": "orbs",
}

_NON_ALPHA = re.compile(r"[^a-z0-9']+")
_REPEATED_CHAR = re.compile(r"(.)\1+")


def _normalize_word(word: str) -> str:
    """
    Lowercase + strip punctuation, keeping only letters/numbers/apostrophes.
    Whisper sometimes prefixes spaces/punctuation to words, so we aggressively
    normalize here.
    """
    if not word:
        return ""

    normalized = unicodedata.normalize("NFKC", str(word)).lower()
    normalized = _NON_ALPHA.sub("", normalized)
    return normalized.strip("'")


def _resolve_cuss_key(raw_word: str) -> Optional[str]:
    """
    Returns the dictionary key that should be used for the provided word.
    Handles slang spellings such as "fuckin" or "niggas" and stretched
    pronunciations like "shiiiit".
    """
    normalized = _normalize_word(raw_word)
    if not normalized:
        return None

    if normalized in CUSS_MAPPING:
        return normalized

    # Drop repeated characters (e.g., "shiiiit" -> "shit")
    squashed = _REPEATED_CHAR.sub(r"\1", normalized)
    if squashed and squashed in CUSS_MAPPING:
        return squashed

    # Handle trailing apostrophe slang: "fuckin" -> "fucking"
    if normalized.endswith("in"):
        candidate = f"{normalized}g"
        if candidate in CUSS_MAPPING:
            return candidate
    if normalized.endswith("n"):
        candidate = f"{normalized[:-1]}ng"
        if candidate in CUSS_MAPPING:
            return candidate

    # Handle plural/slang "niggas" -> "nigga"
    if normalized.endswith("s"):
        candidate = normalized[:-1]
        if candidate in CUSS_MAPPING:
            return candidate

    return None


def detect_cuss_words(lyrics_data):
    """
    Scans lyrics for cuss words.
    Returns a list of dicts: {'word': str, 'start': float, 'end': float, 'replacement': str}
    """
    cuss_segments = []
    for item in lyrics_data:
        cuss_key = _resolve_cuss_key(item.get("word", ""))
        if not cuss_key:
            continue

        cuss_segments.append({
            "word": item.get("word", ""),
            "start": item['start'],
            "end": item['end'],
            "replacement": CUSS_MAPPING[cuss_key]
        })
    return cuss_segments
