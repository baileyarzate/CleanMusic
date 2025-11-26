# src/censor_manager.py

CUSS_MAPPING = {
    "bitch": "itch",
    "bitches": "itches",
    "shit": "ship",
    "fuck": "duck",
    "fucking": "ducking",
    "fucked": "ducked",
    "damn": "darn",
    "ass": "ash",
    "nigga": "neighbor",
    "nigger": "neighbor",
    "hoe": "row",
    "hoes": "rows",
    # Add more as needed
}

def detect_cuss_words(lyrics_data):
    """
    Scans lyrics for cuss words.
    Returns a list of dicts: {'word': str, 'start': float, 'end': float, 'replacement': str}
    """
    cuss_segments = []
    for item in lyrics_data:
        # Clean the word to match mapping keys (remove punctuation if any slipped through)
        word_clean = item['word'].lower().strip(".,!?")
        
        if word_clean in CUSS_MAPPING:
            cuss_segments.append({
                "word": word_clean,
                "start": item['start'],
                "end": item['end'],
                "replacement": CUSS_MAPPING[word_clean]
            })
    return cuss_segments
