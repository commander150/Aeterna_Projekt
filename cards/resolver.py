from engine.effects_expansions import handle_expansion_gate


def resolve_card_handler(card, category="on_play"):
    if handle_expansion_gate(getattr(card, "nev", "Ismeretlen lap"), getattr(card, "kepesseg", "")):
        return {"status": "skipped", "category": category}
    return {"status": "core"}
