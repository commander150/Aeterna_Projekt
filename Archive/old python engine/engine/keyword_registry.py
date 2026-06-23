from dataclasses import dataclass

from utils.text import normalize_lookup_text


@dataclass(frozen=True)
class KeywordDefinition:
    key: str
    aliases: tuple[str, ...]
    category: str = "keyword"


KEYWORD_DEFINITIONS = {
    "aegis": KeywordDefinition("aegis", ("aegis", "oltalom")),
    "ethereal": KeywordDefinition("ethereal", ("ethereal", "legies", "légies")),
    "celerity": KeywordDefinition("celerity", ("celerity", "gyorsasag", "gyorsaság")),
    "sundering": KeywordDefinition("sundering", ("sundering", "hasitas", "hasítás")),
    "bane": KeywordDefinition("bane", ("bane", "metely", "métely")),
    "harmonize": KeywordDefinition("harmonize", ("harmonize", "harmonizalas", "harmonizálás")),
    "resonance": KeywordDefinition("resonance", ("resonance", "rezonancia")),
    "clarion": KeywordDefinition("clarion", ("clarion", "riado", "riadó")),
    "echo": KeywordDefinition("echo", ("echo", "visszhang")),
    "burst": KeywordDefinition("burst", ("burst", "reakcio", "reakció")),
    "taunt": KeywordDefinition("taunt", ("taunt", "provoke", "kenyszerites", "kenyszerites")),
}


class KeywordRegistry:
    @staticmethod
    def normalize_keyword_name(name):
        if not name:
            return ""
        normalized = normalize_lookup_text(name)
        for keyword_key, definition in KEYWORD_DEFINITIONS.items():
            if normalized == keyword_key:
                return keyword_key
            if normalized in {normalize_lookup_text(alias) for alias in definition.aliases}:
                return keyword_key
        return normalized

    @staticmethod
    def aliases_for(name):
        keyword_key = KeywordRegistry.normalize_keyword_name(name)
        definition = KEYWORD_DEFINITIONS.get(keyword_key)
        if definition is None:
            return (name,)
        return definition.aliases

    @staticmethod
    def has_keyword(source_text, name):
        haystack = normalize_lookup_text(source_text)
        aliases = KeywordRegistry.aliases_for(name)
        return any(normalize_lookup_text(alias) in haystack for alias in aliases)
