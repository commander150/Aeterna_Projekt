from __future__ import annotations

from types import SimpleNamespace

from engine.actions import ActionLibrary
from engine.card import CsataEgyseg
from engine.targeting import TargetingEngine
from engine.triggers import trigger_engine
from utils.logger import naplo


def _handled(message=None, partial=False, **extra):
    if message:
        naplo.ir(message)
    result = {"resolved": True, "partial": partial}
    result.update(extra)
    return result


def _allied_units(player):
    return ActionLibrary._all_units(player)


def _enemy_horizon_units(player):
    return [
        (zone_name, index, unit)
        for zone_name, index, unit in ActionLibrary._all_units(player)
        if zone_name == "horizont"
    ]


def _negative_spell_markers(unit):
    markers = getattr(unit, "negative_spell_markers", None)
    if markers is None:
        markers = set()
        setattr(unit, "negative_spell_markers", markers)
    return markers


def _summon_token(owner, lane_index, name, atk, hp, race="Token", realm="Semleges", exhausted=True):
    token_card = SimpleNamespace(
        nev=name,
        kartyatipus="Entitás",
        birodalom=realm,
        klan="",
        faj=race,
        kaszt="",
        magnitudo=1,
        aura_koltseg=0,
        tamadas=atk,
        eletero=hp,
        kepesseg="",
        egyseg_e=True,
        jel_e=False,
        reakcio_e=False,
    )
    token_unit = CsataEgyseg(token_card)
    token_unit.owner = owner
    token_unit.kimerult = exhausted
    owner.horizont[lane_index] = token_unit
    trigger_engine.dispatch(
        "on_summon",
        source=token_unit,
        owner=owner,
        payload={"zone": "horizont", "token": True},
    )
    return token_unit


def handle_felderito_bagoly(card, jatekos, ellenfel, **_):
    if ellenfel is None or not ellenfel.pakli:
        return _handled(
            f"✨ Felderítő Bagoly: nem volt ellenfél pakli, ezért csak a felderítés maradt el.",
            partial=True,
        )

    top_card = ellenfel.pakli[-1]
    veszelyes = (
        top_card.aura_koltseg >= 3
        or top_card.magnitudo >= 4
        or top_card.tamadas >= 3
        or top_card.eletero >= 4
    )
    if veszelyes:
        ellenfel.pakli.insert(0, ellenfel.pakli.pop())
        return _handled(
            f"🔎 Felderítő Bagoly: {jatekos.nev} megnézte {ellenfel.nev} paklijának tetejét ({top_card.nev}), majd a pakli aljára küldte."
        )

    return _handled(
        f"🔎 Felderítő Bagoly: {jatekos.nev} megnézte {ellenfel.nev} paklijának tetejét ({top_card.nev}), és a helyén hagyta."
    )


def handle_legaramlat_magus(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("🌬️ Légáramlat-Mágus: nem volt ellenfél célpont.", partial=True)

    candidates = [
        data
        for data in _enemy_horizon_units(ellenfel)
        if data[2].lap.magnitudo <= 2
    ]
    if not candidates:
        return _handled(
            "🌬️ Légáramlat-Mágus: nem volt 2-es vagy kisebb Magnitúdójú ellenséges Horizont Entitás.",
            partial=True,
        )

    zone_name, index, target = max(candidates, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    valid, _ = TargetingEngine.validate(target, "return_to_hand")
    if not valid:
        return _handled(
            f"🌬️ Légáramlat-Mágus: {target.lap.nev} nem küldhető vissza kézbe.",
            partial=True,
        )

    ActionLibrary.return_target_to_hand(ellenfel, zone_name, index, f"{card.nev}")
    return _handled(f"🌬️ Légáramlat-Mágus: {target.lap.nev} visszakerült a tulajdonosa kezébe.")


def handle_a_vilagok_keresztezodese(card, jatekos, **_):
    setattr(jatekos, "vilagok_keresztezodese_aktiv", True)
    return _handled(
        f"🌌 A Világok Kereszteződése: {jatekos.nev} számára az állandó síkhatás aktív lett."
    )


def handle_csapdaallito(card, jatekos, **_):
    aktualis = getattr(jatekos, "kovetkezo_jel_kedvezmeny", 0) + 1
    setattr(jatekos, "kovetkezo_jel_kedvezmeny", aktualis)
    return _handled(
        f"🪤 Csapdaállító: {jatekos.nev} következő Jel kártyája ebben a mérkőzésben 1 aurával olcsóbb lesz."
    )


def handle_kove_valas(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("🪨 Kővé Válás: nem volt ellenfél célpont.", partial=True)

    candidates = _enemy_horizon_units(ellenfel)
    if not candidates:
        return _handled("🪨 Kővé Válás: nem volt ellenséges Horizont Entitás.", partial=True)

    _, _, target = max(candidates, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    target.stone_awaken_lock = max(1, getattr(target, "stone_awaken_lock", 0))
    target.position_lock_awakenings = max(1, getattr(target, "position_lock_awakenings", 0))
    _negative_spell_markers(target).update({"kove_valas", "position_lock"})
    return _handled(
        f"🪨 Kővé Válás: {target.lap.nev} a következő Ébredés fázisban kimerült marad, és addig nem válthat pozíciót."
    )


def handle_megtisztulas(card, jatekos, **_):
    units = _allied_units(jatekos)
    if not units:
        return _handled("✨ Megtisztulás: nem volt saját Entitás a hatáshoz.", partial=True)

    cleared = 0
    for _, _, unit in units:
        markers = _negative_spell_markers(unit)
        if getattr(unit, "stone_awaken_lock", 0) > 0:
            unit.stone_awaken_lock = 0
            cleared += 1
        if getattr(unit, "position_lock_awakenings", 0) > 0:
            unit.position_lock_awakenings = 0
            cleared += 1
        markers.difference_update({"kove_valas", "position_lock"})

        unit.bonus_max_hp = getattr(unit, "bonus_max_hp", 0) + 1
        unit.akt_hp += 1

    if cleared > 0:
        return _handled(
            f"✨ Megtisztulás: {cleared} negatív varázshatás lekerült, és minden saját Entitás +1 maximális HP-t kapott."
        )

    return _handled(
        "✨ Megtisztulás: eltávolítható negatív varázshatás nem volt, de minden saját Entitás +1 maximális HP-t kapott.",
        partial=True,
    )


def handle_csapda_a_fustben(card, vedo, summoned_unit=None, **_):
    if summoned_unit is None:
        return {"resolved": False}

    if summoned_unit.lap.magnitudo < 4:
        return {"resolved": False}

    summoned_unit.kimerult = True
    return _handled(
        f"🪤 Csapda a Füstben: {summoned_unit.lap.nev} azonnal kimerült állapotba került.",
        consume_trap=True,
    )


def can_activate_varatlan_erosites(card, tamado_egyseg, tamado, vedo, **_):
    if tamado_egyseg is None or tamado is None or vedo is None:
        return False

    try:
        lane_index = tamado.horizont.index(tamado_egyseg)
    except ValueError:
        return False

    blockers = [
        item for item in ActionLibrary._all_units(vedo)
        if item[0] == "horizont" and not item[2].kimerult and not getattr(item[2], "cannot_block_until_turn_end", False)
    ]
    if blockers:
        return False

    if vedo.horizont[lane_index] is not None:
        return False
    if isinstance(vedo.zenit[lane_index], CsataEgyseg):
        return False
    if not vedo.pecsetek:
        return False
    return True


def handle_varatlan_erosites(card, tamado_egyseg, tamado, vedo, **_):
    if not can_activate_varatlan_erosites(card, tamado_egyseg, tamado, vedo):
        return {"resolved": False}

    lane_index = tamado.horizont.index(tamado_egyseg)
    token = _summon_token(
        vedo,
        lane_index,
        "Erősítés Token",
        atk=1,
        hp=1,
        race="Gépezet",
        realm=vedo.birodalom,
        exhausted=True,
    )

    megsemmisult = token.serul(tamado_egyseg.akt_tamadas)
    if megsemmisult:
        vedo.temeto.append(token.lap)
        vedo.horizont[lane_index] = None
        return _handled(
            "🪤 Váratlan Erősítés: egy 1/1-es Gépezet token felfogta az ütést, majd elpusztult.",
            stop_attack=True,
        )

    return _handled(
        "🪤 Váratlan Erősítés: egy 1/1-es Gépezet token felfogta az ütést, és játékban maradt.",
        stop_attack=True,
    )


def on_awakening_phase(context):
    player = context.owner
    if player is None:
        return

    if getattr(player, "vilagok_keresztezodese_aktiv", False) and player.pakli:
        top_card = player.pakli[-1]
        if top_card.birodalom == "Aether":
            player.kez.append(player.pakli.pop())
            naplo.ir(
                f"🌌 A Világok Kereszteződése: {player.nev} felvette a pakli tetejéről az Aether lapot ({top_card.nev})."
            )
        else:
            if top_card.aura_koltseg >= 4 or top_card.magnitudo >= 4:
                player.pakli.insert(0, player.pakli.pop())
                naplo.ir(
                    f"🌌 A Világok Kereszteződése: {player.nev} megnézte a pakli tetejét ({top_card.nev}), majd a pakli aljára tette."
                )
            else:
                naplo.ir(
                    f"🌌 A Világok Kereszteződése: {player.nev} megnézte a pakli tetejét ({top_card.nev}), és a helyén hagyta."
                )

    for _, _, unit in _allied_units(player):
        if getattr(unit, "stone_awaken_lock", 0) > 0:
            unit.kimerult = True
            unit.stone_awaken_lock -= 1
            naplo.ir(f"🪨 Kővé Válás: {unit.lap.nev} kimerült marad ebben az Ébredés fázisban.")

        if getattr(unit, "position_lock_awakenings", 0) > 0:
            unit.position_lock_awakenings -= 1

