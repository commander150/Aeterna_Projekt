from __future__ import annotations

from typing import Dict, List


DECK_PRESETS: Dict[str, Dict[str, object]] = {
    "ignis_tempo_test": {
        "label": "Ignis tempo tesztpakli",
        "description": "Gyors nyomas, tempo es eros korai board jelenlet figyelesere.",
        "realm": "Ignis",
        "cards": [
            "Hamvaskezű Újonc",
            "Lángoló Öklű Bajnok",
            "Parázsfarkas",
            "Ignis Csonttörő",
            "Vörösréz Pajzsos",
            "Hamvaskezű Seregvezér",
            "Tűzvihar Bajnoka",
            "Élő Meteor",
            "A Főnix Könnye",
            "Tünde Pyromanta",
        ]
        * 4,
    },
    "aqua_control_test": {
        "label": "Aqua kontroll tesztpakli",
        "description": "Lassabb kontroll, vedekezes es lezaro pecsetnyomas megfigyelesere.",
        "realm": "Aqua",
        "cards": [
            "Kagylópáncélos Őrszem",
            "Kagylópajzsos Védelmező",
            "Gyöngyvigyázó Papnő",
            "Árapály-Mágus",
            "Mélységi Gólem",
            "Abisszális Ős-Teknős",
            "Az Őstenger Akarata",
            "Páncélos Rák",
            "Fagyos Lándzsa",
            "Hullám-Parancsnok",
        ]
        * 4,
    },
    "ventus_tempo_test": {
        "label": "Ventus tempo tesztpakli",
        "description": "Celerity, visszavetel es gyors board-tempo mintak ellenorzesere.",
        "realm": "Ventus",
        "cards": [
            "Szelek Szárnyán Járó",
            "Ciklonlovas Cserkész",
            "Villámlépésű Kardforgató",
            "Szelekszárnyú Íjász",
            "Mennydörgés Sólyom",
            "Orkán Bajnok",
            "Hurrikán-Táncos",
            "Szélszelídítő Felfedező",
            "Villámvágta Huszár",
            "Levegő-Elementál",
        ]
        * 4,
    },
    "aether_control_test": {
        "label": "Aether kontroll tesztpakli",
        "description": "Aether gepezetes, lassabb kontroll es csapda-jellegu mintak figyelesere.",
        "realm": "Aether",
        "cards": [
            "Gépiesített Baka",
            "Adaptív Felderítő Drón",
            "Bronzfal Gólem",
            "Aether-Generátor",
            "Óramű-Kiborg Zsoldos",
            "Titánpáncélos Gólem",
            "Újrahasznosító Egység",
            "Fogaskerék-Szerelő",
            "Automata Őrszem",
            "Mechanikus Skorpió",
        ]
        * 4,
    },
}

_PRESET_LOOKUP = {name.lower(): name for name in DECK_PRESETS}


def normalize_deck_preset_name(value):
    if value in (None, "", "none", "random"):
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None
    return _PRESET_LOOKUP.get(cleaned.lower(), cleaned)


def list_deck_presets() -> Dict[str, Dict[str, object]]:
    return {
        name: {
            "label": preset["label"],
            "description": preset["description"],
            "realm": preset["realm"],
            "size": len(preset["cards"]),
        }
        for name, preset in DECK_PRESETS.items()
    }


def get_deck_preset(name: str) -> Dict[str, object]:
    canonical_name = normalize_deck_preset_name(name)
    if canonical_name not in DECK_PRESETS:
        available = ", ".join(sorted(DECK_PRESETS))
        raise ValueError(f"Ismeretlen deck preset: {name}. Elerheto presetek: {available}")
    preset = DECK_PRESETS[canonical_name]
    return {
        "name": canonical_name,
        "label": preset["label"],
        "description": preset["description"],
        "realm": preset["realm"],
        "cards": list(preset["cards"]),
    }


def resolve_deck_preset_cards(name: str, full_card_pool) -> Dict[str, object]:
    preset = get_deck_preset(name)
    cards_by_name = {
        getattr(card, "nev", None): card
        for card in full_card_pool
        if getattr(card, "nev", None)
    }

    resolved_cards: List[object] = []
    missing_cards: List[str] = []
    for card_name in preset["cards"]:
        card = cards_by_name.get(card_name)
        if card is None:
            missing_cards.append(card_name)
            continue
        resolved_cards.append(card)

    if missing_cards:
        missing_display = ", ".join(sorted(set(missing_cards)))
        raise ValueError(
            f"A '{preset['name']}' preset nem epitheto fel, hianyzik ez a lap a cards.xlsx-bol: {missing_display}"
        )

    return {
        "name": preset["name"],
        "label": preset["label"],
        "description": preset["description"],
        "realm": preset["realm"],
        "cards": resolved_cards,
    }
