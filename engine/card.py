from engine.card_metadata import (
    has_effect_tag,
    has_keyword,
    has_target,
    has_trigger,
    normalize_metadata_value,
    normalized_metadata_list,
)


class Kartya:
    def __init__(self, sor_adat):
        row = sor_adat if isinstance(sor_adat, dict) else {}

        def _get(index, *keys, default=""):
            for key in keys:
                if key in row:
                    return row.get(key)
            if isinstance(sor_adat, (list, tuple)) and len(sor_adat) > index:
                return sor_adat[index]
            return default

        def _to_int(value):
            try:
                return int(float(value)) if value is not None else 0
            except Exception:
                return 0

        self.nev = normalize_metadata_value(_get(0, "kartya_nev", default="Nevtelen")) or "Nevtelen"
        self.kartyatipus = normalize_metadata_value(_get(1, "kartyatipus", "tipus", default=""))
        self.birodalom = normalize_metadata_value(_get(2, "birodalom", default=""))
        self.klan = normalize_metadata_value(_get(3, "klan", default=""))
        self.faj = normalize_metadata_value(_get(4, "faj", default=""))
        self.kaszt = normalize_metadata_value(_get(5, "kaszt", default=""))

        self.magnitudo = _to_int(_get(6, "magnitudo", default=0))
        self.aura_koltseg = _to_int(_get(7, "aura_koltseg", "aura", default=0))
        self.tamadas = _to_int(_get(8, "tamadas", "atk", default=0))
        self.eletero = _to_int(_get(9, "eletero", "hp", default=0))
        self.kepesseg = normalize_metadata_value(_get(10, "kepesseg", default=""))

        self.canonical_text = normalize_metadata_value(_get(11, "kepesseg_canonical", default="")) or self.kepesseg
        self.keywords = normalized_metadata_list(_get(11, "kulcsszavak_felismerve", default=""))
        self.triggers = normalized_metadata_list(_get(12, "trigger_felismerve", default=""), field_name="trigger")
        self.targets = normalized_metadata_list(_get(13, "celpont_felismerve", default=""))
        self.effect_tags = normalized_metadata_list(_get(14, "hatascimkek", default=""))
        self.interpretation_status = normalize_metadata_value(_get(15, "ertelmezesi_statusz", default=""))

        if self.keywords and self.canonical_text == self.kepesseg and "kepesseg_canonical" not in row:
            self.canonical_text = self.kepesseg

        self.keywords_normalized = list(self.keywords)
        self.triggers_normalized = list(self.triggers)
        self.targets_normalized = list(self.targets)
        self.effect_tags_normalized = list(self.effect_tags)
        self.structured_data_available = any(
            (
                bool(self.canonical_text and self.canonical_text != self.kepesseg),
                bool(self.keywords),
                bool(self.triggers),
                bool(self.targets),
                bool(self.effect_tags),
                bool(self.interpretation_status),
            )
        )

        self.egyseg_e = "entit" in self.kartyatipus.lower()
        self.jel_e = "jel" in self.kartyatipus.lower()
        self.reakcio_e = (
            "reakci" in self.kepesseg.lower()
            or "burst" in self.kepesseg.lower()
            or has_keyword(self, "burst")
        )

    def van_kulcsszo(self, kulcsszo):
        return has_keyword(self, kulcsszo) or kulcsszo.lower() in self.kepesseg.lower()

    def has_effect_tag(self, tag):
        return has_effect_tag(self, tag)

    def has_trigger(self, trigger):
        return has_trigger(self, trigger)

    def has_target(self, target):
        return has_target(self, target)


class CsataEgyseg:
    def __init__(self, kartya):
        self.lap = kartya
        self.akt_tamadas = kartya.tamadas
        self.akt_hp = kartya.eletero
        self.kimerult = True
        self.bane_target = False

        if hasattr(kartya, "van_kulcsszo"):
            gyors = kartya.van_kulcsszo("gyorsasag") or kartya.van_kulcsszo("celerity")
        else:
            kepesseg = getattr(kartya, "kepesseg", "") or ""
            gyors = "gyorsas" in kepesseg.lower() or "celerity" in kepesseg.lower()

        if gyors:
            self.kimerult = False

    def serul(self, mennyiseg):
        self.akt_hp -= mennyiseg
        return self.akt_hp <= 0
