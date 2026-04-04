from __future__ import annotations

from types import SimpleNamespace

from engine.actions import ActionLibrary
from engine.board_utils import _is_board_entity, is_trap, is_zenit_entity, set_zone_slot
from engine.card import CsataEgyseg
from engine.targeting import TargetingEngine
from engine.triggers import trigger_engine
from utils.logger import naplo
from utils.text import normalize_lookup_text


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


def _is_machine_card(card):
    faj = normalize_lookup_text(getattr(card, "faj", ""))
    return "gepezet" in faj or "kiborg" in faj or "golem" in faj


def _consume_named_trap(player, trap_name):
    for index, trap in enumerate(player.zenit):
        if not is_trap(trap):
            continue
        if normalize_lookup_text(getattr(trap, "nev", "")) == normalize_lookup_text(trap_name):
            player.temeto.append(trap)
            set_zone_slot(player, "zenit", index, None, f"consume_trap:{trap_name}")
            player.hasznalt_jelek_ebben_a_korben += 1
            return trap
    return None


def _summon_token(owner, lane_index, name, atk, hp, race="Token", realm="Semleges", exhausted=True):
    token_card = SimpleNamespace(
        nev=name,
        kartyatipus="Entitas",
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
    set_zone_slot(owner, "horizont", lane_index, token_unit, f"token_summon:{name}")
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
            "Felderito Bagoly: nem volt ellenfel pakli, ezert csak a felderites maradt el.",
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
            f"Felderito Bagoly: {jatekos.nev} megnezte {ellenfel.nev} paklianak tetejet ({top_card.nev}), majd a pakli aljara kuldte."
        )

    return _handled(
        f"Felderito Bagoly: {jatekos.nev} megnezte {ellenfel.nev} paklianak tetejet ({top_card.nev}), es a helyen hagyta."
    )


def handle_legaramlat_magus(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Legaramlat-Magus: nem volt ellenfel celpont.", partial=True)

    candidates = [
        data
        for data in _enemy_horizon_units(ellenfel)
        if data[2].lap.magnitudo <= 2
    ]
    if not candidates:
        return _handled(
            "Legaramlat-Magus: nem volt 2-es vagy kisebb Magnitudoju ellenseges Horizont Entitas.",
            partial=True,
        )

    zone_name, index, target = max(candidates, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    valid, _ = TargetingEngine.validate(target, "return_to_hand")
    if not valid:
        return _handled(
            f"Legaramlat-Magus: {target.lap.nev} nem kuldheto vissza kezbe.",
            partial=True,
        )

    ActionLibrary.return_target_to_hand(ellenfel, zone_name, index, f"{card.nev}")
    return _handled(f"Legaramlat-Magus: {target.lap.nev} visszakerult a tulajdonosa kezebe.")


def handle_a_vilagok_keresztezodese(card, jatekos, **_):
    setattr(jatekos, "vilagok_keresztezodese_aktiv", True)
    return _handled(
        f"A Vilagok Keresztezodese: {jatekos.nev} szamara az allando sikhatas aktiv lett."
    )


def handle_csapdaallito(card, jatekos, **_):
    aktualis = getattr(jatekos, "kovetkezo_jel_kedvezmeny", 0) + 1
    setattr(jatekos, "kovetkezo_jel_kedvezmeny", aktualis)
    return _handled(
        f"Csapdaallito: {jatekos.nev} kovetkezo Jel kartyaja 1 auraval olcsobb lesz."
    )


def handle_kove_valas(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Kove Valas: nem volt ellenfel celpont.", partial=True)

    candidates = _enemy_horizon_units(ellenfel)
    if not candidates:
        return _handled("Kove Valas: nem volt ellenseges Horizont Entitas.", partial=True)

    _, _, target = max(candidates, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    target.stone_awaken_lock = max(1, getattr(target, "stone_awaken_lock", 0))
    target.position_lock_awakenings = max(1, getattr(target, "position_lock_awakenings", 0))
    _negative_spell_markers(target).update({"kove_valas", "position_lock"})
    return _handled(
        f"Kove Valas: {target.lap.nev} a kovetkezo Ebredés fazisban kimerult marad, es addig nem valthat poziciot."
    )


def handle_megtisztulas(card, jatekos, **_):
    units = _allied_units(jatekos)
    if not units:
        return _handled("Megtisztulas: nem volt sajat Entitas a hatashoz.", partial=True)

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
            f"Megtisztulas: {cleared} negativ varazshatas lekerult, es minden sajat Entitas +1 maximalis HP-t kapott."
        )

    return _handled(
        "Megtisztulas: eltavolithato negativ varazshatas nem volt, de minden sajat Entitas +1 maximalis HP-t kapott.",
        partial=True,
    )


def handle_csapda_a_fustben(card, vedo, summoned_unit=None, **_):
    if summoned_unit is None:
        return {"resolved": False}

    if summoned_unit.lap.magnitudo < 4:
        return {"resolved": False}

    summoned_unit.kimerult = True
    return _handled(
        f"Csapda a Fustben: {summoned_unit.lap.nev} azonnal kimerult allapotba kerult.",
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
    if is_zenit_entity(vedo.zenit[lane_index]):
        return False
    if not vedo.pecsetek:
        return False
    return True


def handle_varatlan_erosites(card, tamado_egyseg=None, tamado=None, vedo=None, **_):
    if not can_activate_varatlan_erosites(card, tamado_egyseg, tamado, vedo):
        return {"resolved": False}

    lane_index = tamado.horizont.index(tamado_egyseg)
    token = _summon_token(
        vedo,
        lane_index,
        "Erosites Token",
        atk=1,
        hp=1,
        race="Gepezet",
        realm=vedo.birodalom,
        exhausted=True,
    )

    megsemmisult = token.serul(tamado_egyseg.akt_tamadas)
    if megsemmisult:
        vedo.temeto.append(token.lap)
        set_zone_slot(vedo, "horizont", lane_index, None, "varatlan_erosites_token_destroyed")
        return _handled(
            "Varatlan Erosites: egy 1/1-es Gepezet token felfogta az utest, majd elpusztult.",
            stop_attack=True,
        )

    return _handled(
        "Varatlan Erosites: egy 1/1-es Gepezet token felfogta az utest, es jatekban maradt.",
        stop_attack=True,
    )


def handle_a_hulladektelep(card, jatekos, **_):
    setattr(jatekos, "hulladektelep_aktiv", True)
    return _handled(f"A Hulladektelep: {jatekos.nev} szamara aktiv lett a gepezet-ujrahasznosito sikhatas.")


def handle_alvilagi_kapcsolatok(card, jatekos, **_):
    traps = [lap for lap in jatekos.pakli if getattr(lap, "jel_e", False)]
    if not traps:
        return _handled("Alvilagi Kapcsolatok: nem volt keresheto Jel a pakliban.", partial=True)

    target = min(traps, key=lambda lap: (lap.magnitudo, lap.aura_koltseg, lap.nev))
    empty_index = next((i for i, slot in enumerate(jatekos.zenit) if slot is None), None)
    if empty_index is None:
        return _handled("Alvilagi Kapcsolatok: nem volt ures Zenit hely a csapdanak.", partial=True)

    jatekos.pakli.remove(target)
    set_zone_slot(jatekos, "zenit", empty_index, target, "alvilagi_kapcsolatok")
    return _handled(f"Alvilagi Kapcsolatok: {target.nev} ingyen, leforditva a Zenitbe kerult.")


def handle_az_orok_elet_temploma(card, jatekos, **_):
    setattr(jatekos, "orok_elet_temploma_aktiv", True)
    return _handled(f"Az Orok Elet Temploma: {jatekos.nev} szamara aktiv lett az allando eleteronovelo sikhatas.")


def handle_informacio_vasarlas(card, jatekos, **_):
    if not jatekos.pakli:
        return _handled("Informacio-Vasarlas: a pakli ures volt.", partial=True)

    top_cards = []
    for _ in range(min(3, len(jatekos.pakli))):
        top_cards.append(jatekos.pakli.pop())

    chosen = max(top_cards, key=lambda lap: (lap.aura_koltseg, lap.magnitudo, lap.tamadas + lap.eletero))
    jatekos.kez.append(chosen)
    top_cards.remove(chosen)

    for card_to_bottom in top_cards:
        jatekos.pakli.insert(0, card_to_bottom)

    return _handled(
        f"Informacio-Vasarlas: {chosen.nev} kezbe kerult, a maradek {len(top_cards)} lap a pakli aljara ment."
    )


def handle_rendszerfrissites(card, jatekos, **_):
    units = _allied_units(jatekos)
    if not units:
        return _handled("Rendszerfrissites: nem volt sajat Entitas a celponthoz.", partial=True)

    _, _, unit = max(units, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    unit.protect_keywords_until_turn_end = True
    unit.protect_atk_from_enemy_until_turn_end = True
    return _handled(
        f"Rendszerfrissites: {unit.lap.nev} a kor vegeig nem veszitheti el a kulcsszavait, es ATK-ja nem csokkentheto ellenseges hatasokkal."
    )


def handle_a_gyenge_elhullik(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("A Gyenge Elhullik: nem volt ellenfel.", partial=True)

    candidates = [data for data in _enemy_horizon_units(ellenfel) if data[2].akt_hp <= 2]
    if not candidates:
        return _handled("A Gyenge Elhullik: nem volt 2 vagy kevesebb jelenlegi HP-ju ellenseges Horizont Entitas.", partial=True)

    from engine.effects import EffectEngine

    for zone_name, index, unit in sorted(candidates, key=lambda data: data[1], reverse=True):
        EffectEngine.destroy_unit(ellenfel, zone_name, index, jatekos, "a gyenge elhullik")
    return _handled(f"A Gyenge Elhullik: {len(candidates)} ellenseges Horizont Entitas elpusztult.")


def handle_hamis_arany(card, varazslat, jatekos, ellenfel, **_):
    if varazslat is None or getattr(varazslat, "egyseg_e", False) or getattr(varazslat, "jel_e", False):
        return {"resolved": False}

    aktiv = 0
    for source in ellenfel.osforras:
        if isinstance(source, dict) and not source.get("hasznalt", False):
            source["hasznalt"] = True
            aktiv += 1
    ellenfel.rezonancia_aura = 0

    return _handled(
        f"Hamis Arany: {ellenfel.nev} varazslata letrejott, de {aktiv} megmaradt aktiv auraja elveszett ebben a korben.",
        consume_trap=True,
    )


def can_activate_hamis_arany(card, varazslat=None, **_):
    if varazslat is None:
        return False
    return not getattr(varazslat, "egyseg_e", False) and not getattr(varazslat, "jel_e", False)


def handle_hamis_igeret(card, vedo, summoned_unit=None, **_):
    if summoned_unit is None or summoned_unit.lap.magnitudo < 4:
        return {"resolved": False}

    vedo.kovetkezo_kor_ideiglenes_aura = getattr(vedo, "kovetkezo_kor_ideiglenes_aura", 0) + 2
    return _handled(
        f"Hamis Igeret: {vedo.nev} a kovetkezo sajat korere 2 ideiglenes Aether Aurat kapott elokeszitve.",
        consume_trap=True,
    )


def can_activate_hamis_igeret(card, summoned_unit=None, **_):
    return summoned_unit is not None and summoned_unit.lap.magnitudo >= 4


def handle_kereskedelmi_embargo(card, vedo, summoned_unit=None, tamado=None, **_):
    if summoned_unit is None or tamado is None:
        return {"resolved": False}
    if getattr(tamado, "megidezett_entitasok_ebben_a_korben", 0) < 2:
        return {"resolved": False}

    return _handled(
        f"Kereskedelmi Embargo: {summoned_unit.lap.nev} a sikeres idezes utan azonnal az uressegbe kerult.",
        consume_trap=True,
        destroy_summoned=True,
    )


def can_activate_kereskedelmi_embargo(card, vedo=None, summoned_unit=None, tamado=None, **_):
    return vedo is not None and summoned_unit is not None and tamado is not None and getattr(tamado, "megidezett_entitasok_ebben_a_korben", 0) >= 2


def can_activate_angyali_beavatkozas(card, owner, unit, attacker=None, **_):
    return owner is not None and unit is not None and attacker is not None


def handle_angyali_beavatkozas(card, owner, unit, attacker=None, **_):
    if not can_activate_angyali_beavatkozas(card, owner, unit, attacker=attacker):
        return {"resolved": False}

    unit.akt_hp = 1
    attacker.kimerult = True
    attacker.extra_exhausted_turns = getattr(attacker, "extra_exhausted_turns", 0) + 1
    return _handled(
        f"Angyali Beavatkozas: {unit.lap.nev} megmenekult 1 HP-n, {attacker.lap.nev} pedig a kovetkezo korere is kimerult marad.",
        consume_trap=True,
        prevented_death=True,
    )


def can_activate_hamis_bizonyitek(card, spell_card=None, target_owner=None, caster=None, **_):
    if spell_card is None or target_owner is None or caster is None:
        return False
    if normalize_lookup_text(getattr(spell_card, "kartyatipus", "")) != "rituale":
        return False
    return any(_is_board_entity(unit) for unit in caster.horizont + caster.zenit)


def handle_hamis_bizonyitek(card, spell_card=None, target_owner=None, caster=None, **_):
    if not can_activate_hamis_bizonyitek(card, spell_card=spell_card, target_owner=target_owner, caster=caster):
        return {"resolved": False}

    redirect_targets = ActionLibrary._all_units(caster)
    if not redirect_targets:
        return _handled("Hamis Bizonyitek: nem volt atiranyithato sajat Entitas.", partial=True)

    zone_name, index, unit = min(redirect_targets, key=lambda data: (data[2].akt_hp, data[2].akt_tamadas))
    return _handled(
        f"Hamis Bizonyitek: a {spell_card.nev} celpontja atiranyitva {unit.lap.nev} lapra.",
        consume_trap=True,
        redirected_target=(zone_name, index, unit),
    )


def can_activate_hamis_halal(card, owner, unit, reason="combat", **_):
    return owner is not None and unit is not None and reason == "combat"


def handle_hamis_halal(card, owner, unit, zone_name=None, index=None, **_):
    if zone_name is None or index is None or not can_activate_hamis_halal(card, owner, unit):
        return {"resolved": False}

    set_zone_slot(owner, zone_name, index, None, "hamis_halal_return_to_hand")
    owner.kez.append(unit.lap)
    return _handled(
        f"Hamis Halal: {unit.lap.nev} megmenekult, es azonnal visszakerult a kezbe.",
        consume_trap=True,
        prevented_death=True,
        returned_to_hand=True,
    )


def resolve_spell_redirect_trap(spell_card, caster, target_owner):
    trap = _consume_named_trap(target_owner, "Hamis Bizonyitek")
    if trap is None:
        return None

    result = handle_hamis_bizonyitek(trap, spell_card=spell_card, target_owner=target_owner, caster=caster)
    if not result.get("resolved"):
        target_owner.zenit.append(target_owner.temeto.pop())
        target_owner.hasznalt_jelek_ebben_a_korben = max(0, target_owner.hasznalt_jelek_ebben_a_korben - 1)
        return None
    return result


def resolve_combat_lethal_trap(owner, unit, attacker, zone_name, index):
    for trap_name, handler in (
        ("Angyali Beavatkozas", handle_angyali_beavatkozas),
        ("Hamis Halal", handle_hamis_halal),
    ):
        trap = _consume_named_trap(owner, trap_name)
        if trap is None:
            continue
        result = handler(trap, owner=owner, unit=unit, attacker=attacker, zone_name=zone_name, index=index, reason="combat")
        if result.get("resolved"):
            return result
        owner.zenit.append(owner.temeto.pop())
        owner.hasznalt_jelek_ebben_a_korben = max(0, owner.hasznalt_jelek_ebben_a_korben - 1)
    return None


def on_awakening_phase(context):
    player = context.owner
    if player is None:
        return

    if getattr(player, "vilagok_keresztezodese_aktiv", False) and player.pakli:
        top_card = player.pakli[-1]
        if top_card.birodalom == "Aether":
            player.kez.append(player.pakli.pop())
            naplo.ir(
                f"A Vilagok Keresztezodese: {player.nev} felvette a pakli tetejerol az Aether lapot ({top_card.nev})."
            )
        else:
            if top_card.aura_koltseg >= 4 or top_card.magnitudo >= 4:
                player.pakli.insert(0, player.pakli.pop())
                naplo.ir(
                    f"A Vilagok Keresztezodese: {player.nev} megnezte a pakli tetejet ({top_card.nev}), majd a pakli aljara tette."
                )
            else:
                naplo.ir(
                    f"A Vilagok Keresztezodese: {player.nev} megnezte a pakli tetejet ({top_card.nev}), es a helyen hagyta."
                )

    if getattr(player, "orok_elet_temploma_aktiv", False):
        units = _allied_units(player)
        if units:
            for _, _, unit in units:
                unit.bonus_max_hp = getattr(unit, "bonus_max_hp", 0) + 1
                unit.akt_hp += 1
            naplo.ir(f"Az Orok Elet Temploma: {len(units)} sajat Entitas +1 maximalis HP-t kapott.")

    pending_temp_aura = getattr(player, "kovetkezo_kor_ideiglenes_aura", 0)
    if pending_temp_aura > 0:
        player.kovetkezo_kor_ideiglenes_aura = 0
        player.ad_ideiglenes_aurat(pending_temp_aura, "Hamis Igeret")

    for _, _, unit in _allied_units(player):
        if getattr(unit, "stone_awaken_lock", 0) > 0:
            unit.kimerult = True
            unit.stone_awaken_lock -= 1
            naplo.ir(f"Kove Valas: {unit.lap.nev} kimerult marad ebben az Ebredés fazisban.")

        if getattr(unit, "position_lock_awakenings", 0) > 0:
            unit.position_lock_awakenings -= 1


def on_destroyed(context):
    owner = context.owner
    source = context.source
    if owner is None or source is None:
        return
    if not getattr(owner, "hulladektelep_aktiv", False):
        return
    if _is_machine_card(source):
        owner.kovetkezo_gepezet_kedvezmeny = getattr(owner, "kovetkezo_gepezet_kedvezmeny", 0) + 1
        naplo.ir(f"A Hulladektelep: {owner.nev} kovetkezo Gepezet idezese 1 auraval olcsobb lesz.")

