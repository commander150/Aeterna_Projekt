import unicodedata


MOJIBAKE_REPLACEMENTS = {
    "Ăˇ": "á",
    "Ă©": "é",
    "Ă­": "í",
    "Ăł": "ó",
    "Ă¶": "ö",
    "Ĺ‘": "ő",
    "Ăş": "ú",
    "ĂĽ": "ű",
    "Ă": "Á",
    "Ă‰": "É",
    "ĂŤ": "Í",
    "Ă“": "Ó",
    "Ă–": "Ö",
    "Ĺ": "Ő",
    "Ăš": "Ú",
    "Ăś": "Ü",
    "Ă": "Ü",
    "Ă": "",
    "Ĺ": "",
    "ď¸Ź": "",
    "âš ": "⚠",
    "âś¨": "✨",
    "â ": "☠",
    "â—": "❗",
    "đź’Ą": "💥",
    "đź’”": "💔",
    "đź›ˇ": "🛡",
    "đź§Š": "🧊",
    "đź”Ą": "🔥",
    "đź”®": "🔮",
    "đźŽŻ": "🎯",
    "đźŽ¶": "🎶",
    "đź‘»": "👻",
    "đź“ś": "📝",
    "đź•¸": "🗸",
    "â„ą": "ℹ",
    "â…": "✅",
}


def repair_mojibake(text):
    if text is None:
        return ""

    fixed = str(text)
    for broken, good in MOJIBAKE_REPLACEMENTS.items():
        fixed = fixed.replace(broken, good)
    return fixed


def normalize_lookup_text(text):
    if not text:
        return ""

    fixed = repair_mojibake(text)
    normalized = unicodedata.normalize("NFKD", fixed)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.lower()
