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


def _allied_horizon_units(player):
    return [
        (zone_name, index, unit)
        for zone_name, index, unit in ActionLibrary._all_units(player)
        if zone_name == "horizont"
    ]


def _card_name(obj):
    if hasattr(obj, "lap") and hasattr(obj.lap, "nev"):
        return normalize_lookup_text(obj.lap.nev)
    return normalize_lookup_text(getattr(obj, "nev", ""))


def _is_named(obj, name):
    return _card_name(obj) == normalize_lookup_text(name)


def _first_empty_horizon(player):
    for index, slot in enumerate(player.horizont):
        if slot is None:
            return index
    return None


def _first_empty_zenit(player):
    for index, slot in enumerate(player.zenit):
        if slot is None:
            return index
    return None


def _negative_spell_markers(unit):
    markers = getattr(unit, "negative_spell_markers", None)
    if markers is None:
        markers = set()
        setattr(unit, "negative_spell_markers", markers)
    return markers


def _is_machine_card(card):
    faj = normalize_lookup_text(getattr(card, "faj", ""))
    return "gepezet" in faj or "kiborg" in faj or "golem" in faj


def _grant_keyword(unit, keyword, temporary=False):
    attr = "temp_granted_keywords" if temporary else "granted_keywords"
    values = set(getattr(unit, attr, set()) or set())
    values.add(normalize_lookup_text(keyword))
    setattr(unit, attr, values)


def _remove_keyword_temporarily(unit, keyword):
    values = set(getattr(unit, "temp_removed_keywords", set()) or set())
    values.add(normalize_lookup_text(keyword))
    setattr(unit, "temp_removed_keywords", values)


def _grant_temp_attack(unit, amount):
    if amount <= 0:
        return
    unit.akt_tamadas += amount
    unit.temp_atk_bonus_until_turn_end = getattr(unit, "temp_atk_bonus_until_turn_end", 0) + amount


def _best_other_allied_unit(player, excluded_unit=None, horizon_only=False):
    units = _allied_horizon_units(player) if horizon_only else _allied_units(player)
    units = [item for item in units if item[2] is not excluded_unit]
    if not units:
        return None
    return max(units, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))


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


def can_activate_varatlan_erosites(card, tamado_egyseg=None, tamado=None, vedo=None, **_):
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


def can_activate_angyali_beavatkozas(card, owner=None, unit=None, attacker=None, **_):
    if owner is None or unit is None or attacker is None:
        return False
    return True


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


def can_activate_hamis_halal(card, owner=None, unit=None, reason="combat", **_):
    if owner is None or unit is None:
        return False
    return reason == "combat"


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


def resolve_spell_redirect_trap(spell_card, caster, target_owner, current_target=None):
    trap = _consume_named_trap(target_owner, "Hamis Bizonyitek")
    if trap is not None:
        result = handle_hamis_bizonyitek(trap, spell_card=spell_card, target_owner=target_owner, caster=caster)
        if not result.get("resolved"):
            target_owner.zenit.append(target_owner.temeto.pop())
            target_owner.hasznalt_jelek_ebben_a_korben = max(0, target_owner.hasznalt_jelek_ebben_a_korben - 1)
        else:
            return result

    trap = _consume_named_trap(target_owner, "Csaloka Hullam")
    if trap is None:
        return None

    result = handle_csaloka_hullam(trap, spell_card=spell_card, target_owner=target_owner, current_target=current_target, caster=caster)
    if not result.get("resolved") or result.get("partial"):
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
        pass
    elif _is_machine_card(source):
        owner.kovetkezo_gepezet_kedvezmeny = getattr(owner, "kovetkezo_gepezet_kedvezmeny", 0) + 1
        naplo.ir(f"A Hulladektelep: {owner.nev} kovetkezo Gepezet idezese 1 auraval olcsobb lesz.")

    if context.payload.get("zone") == "horizont" and _is_machine_card(source):
        trap = _consume_named_trap(owner, "Tulhevult Kazan")
        if trap is not None and context.target is not None:
            from engine.effects import EffectEngine

            celpontok = list(_enemy_horizon_units(context.target))
            if not celpontok:
                naplo.ir("Tulhevult Kazan: nem volt ellenseges Horizont Entitas a robbanashoz.")
                return
            naplo.ir(f"Tulhevult Kazan: {len(celpontok)} ellenseges Horizont Entitas 2 sebzest kap.")
            for _, _, unit in list(celpontok):
                aktualis = EffectEngine._select_enemy_target(context.target, "weakest", "horizont")
                if aktualis is None:
                    break
                EffectEngine._deal_damage_to_target(trap.nev, 2, aktualis, context.target, "Csapda", owner)


def handle_lathatatlan_fal(card, tamado_egyseg=None, tamado=None, vedo=None, **_):
    if tamado_egyseg is None or tamado is None or vedo is None:
        return {"resolved": False}

    try:
        tamado_index = tamado.horizont.index(tamado_egyseg)
    except ValueError:
        return {"resolved": False}

    ActionLibrary.return_target_to_hand(tamado, "horizont", tamado_index, card.nev)
    return _handled(
        f"Lathatatlan Fal: {tamado_egyseg.lap.nev} tamadasa ervenytelenitve, a tamado visszakerult kezbe.",
        consume_trap=True,
        stop_attack=True,
    )


def handle_a_melyseg_szeme(card, vedo, tamado, summoned_unit=None, **_):
    if summoned_unit is None or tamado is None or vedo is None:
        return {"resolved": False}
    if summoned_unit.lap.magnitudo < 4:
        return {"resolved": False}
    if summoned_unit not in tamado.horizont:
        return {"resolved": False}

    lane_index = tamado.horizont.index(summoned_unit)
    zenit_jeloltek = [
        (index, unit)
        for index, unit in enumerate(tamado.zenit)
        if _is_board_entity(unit)
    ]
    if not zenit_jeloltek:
        return _handled(
            f"A Melyseg Szeme: {summoned_unit.lap.nev} megjelent, de nem volt zenitbeli Entitas a cserere.",
            consume_trap=True,
            partial=True,
        )

    cel_index, zenit_unit = min(zenit_jeloltek, key=lambda adat: (adat[1].akt_tamadas, adat[1].akt_hp))
    set_zone_slot(tamado, "horizont", lane_index, zenit_unit, "a_melyseg_szeme_swap_to_horizont")
    set_zone_slot(tamado, "zenit", cel_index, summoned_unit, "a_melyseg_szeme_swap_to_zenit")
    trigger_engine.dispatch("on_position_changed", source=summoned_unit.lap, owner=tamado, payload={"from": "horizont", "to": "zenit"})
    trigger_engine.dispatch("on_position_changed", source=zenit_unit.lap, owner=tamado, payload={"from": "zenit", "to": "horizont"})
    return _handled(
        f"A Melyseg Szeme: {summoned_unit.lap.nev} helyet cserelt {zenit_unit.lap.nev} lappal.",
        consume_trap=True,
    )


def handle_csaloka_hullam(card, spell_card=None, target_owner=None, current_target=None, **_):
    if spell_card is None or target_owner is None or current_target is None:
        return {"resolved": False}

    alternativa = next(
        (
            adat for adat in ActionLibrary._all_units(target_owner)
            if adat[2] is not current_target[2]
        ),
        None,
    )
    if alternativa is None:
        return _handled(
            f"Csaloka Hullam: nem volt masik ervenyes sajat celpont a {spell_card.nev} atiranyitasahoz.",
            partial=True,
        )

    return _handled(
        f"Csaloka Hullam: a {spell_card.nev} celpontja atiranyitva {alternativa[2].lap.nev} lapra.",
        consume_trap=True,
        redirected_target=alternativa,
        redirect_owner=target_owner,
    )


def handle_tuzeso(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Tuzeso: nem volt ellenfel.", partial=True)
    from engine.effects import EffectEngine

    jeloltek = list(_enemy_horizon_units(ellenfel))
    if not jeloltek:
        return _handled("Tuzeso: nem volt ellenseges Horizont Entitas.", partial=True)

    for _, _, _ in jeloltek:
        aktualis = EffectEngine._select_enemy_target(ellenfel, "weakest", "horizont")
        if aktualis is None:
            break
        EffectEngine._deal_damage_to_target(card.nev, 2, aktualis, ellenfel, "Kepesseg", jatekos)
    return _handled(f"Tuzeso: {len(jeloltek)} ellenseges Horizont Entitas 2 sebzest kapott.")


def handle_goznyomasos_kiloves(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Goznyomasos Kiloves: nem volt ellenfel.", partial=True)
    from engine.effects import EffectEngine

    cel = EffectEngine._select_enemy_target(ellenfel, "strongest", "horizont")
    if cel is None:
        return _handled("Goznyomasos Kiloves: nem volt ellenseges Horizont celpont.", partial=True)

    _, index, unit = cel
    overflow = max(0, 4 - unit.akt_hp)
    elpusztult = EffectEngine._deal_damage_to_target(card.nev, 4, cel, ellenfel, "Kepesseg", jatekos)
    if not elpusztult or overflow <= 0:
        return _handled(f"Goznyomasos Kiloves: {unit.lap.nev} 4 sebzest kapott.")

    hatso = ellenfel.zenit[index]
    if _is_board_entity(hatso):
        EffectEngine._deal_damage_to_target(card.nev, overflow, ("zenit", index, hatso), ellenfel, "Kepesseg", jatekos)
        return _handled(f"Goznyomasos Kiloves: {unit.lap.nev} elpusztult, a maradek {overflow} sebzes a mogotte allo Zenit Entitast erte.")

    if overflow > 0:
        EffectEngine._deal_direct_seal_damage(card.nev, overflow, jatekos, ellenfel, "Kepesseg")
        return _handled(f"Goznyomasos Kiloves: {unit.lap.nev} elpusztult, a maradek {overflow} sebzes Pecsetet tort.")

    return _handled(f"Goznyomasos Kiloves: {unit.lap.nev} elpusztult.")


def handle_visszahivas_az_uressegbol(card, jatekos, **_):
    if jatekos is None:
        return {"resolved": False}
    from engine.card import CsataEgyseg

    jeloltek = [lap for lap in jatekos.temeto if "entitas" in normalize_lookup_text(getattr(lap, "kartyatipus", ""))]
    if not jeloltek:
        return _handled("Visszahivas az Uressegbol: nem volt Entitas az Uressegben.", partial=True)

    ures = _first_empty_horizon(jatekos)
    if ures is None:
        return _handled("Visszahivas az Uressegbol: nincs szabad Horizont hely.", partial=True)

    cel_lap = max(jeloltek, key=lambda lap: (lap.magnitudo, lap.tamadas, lap.eletero))
    jatekos.temeto.remove(cel_lap)
    egyseg = CsataEgyseg(cel_lap)
    egyseg.owner = jatekos
    egyseg.kimerult = False
    set_zone_slot(jatekos, "horizont", ures, egyseg, "visszahivas_az_uressegbol")
    trigger_engine.dispatch("on_summon", source=egyseg, owner=jatekos, payload={"zone": "horizont", "revived": True})
    return _handled(f"Visszahivas az Uressegbol: {cel_lap.nev} visszatert a Horizontra aktiv allapotban.")


def handle_gyar_felugyelo(card, jatekos, **_):
    ures = _first_empty_horizon(jatekos)
    if ures is None:
        return _handled("Gyar-Felugyelo: nincs ures Horizont hely a tokennek.", partial=True)
    _summon_token(jatekos, ures, "Gepezet Token", atk=1, hp=1, race="Gepezet", realm=jatekos.birodalom, exhausted=True)
    return _handled("Gyar-Felugyelo: egy 1/1-es Gepezet token a Horizontra kerult.")


def handle_a_tomegtermeles_gyara(card, jatekos, **_):
    setattr(jatekos, "tomegtermeles_gyara_aktiv", True)
    return _handled(f"A Tomegtermeles Gyara: {jatekos.nev} elso gepezet/golem/kiborg idezese koronkent +1 ideiglenes aurat ad.")


def handle_egi_emeles(card, jatekos, **_):
    egyseg = next(iter(_allied_units(jatekos)), None)
    if egyseg is None:
        return _handled("Egi Emeles: nem volt sajat Entitas a visszavetelhez.", partial=True)
    zone_name, index, unit = egyseg
    ActionLibrary.return_target_to_hand(jatekos, zone_name, index, card.nev)
    jatekos.kovetkezo_entitas_kedvezmeny = max(getattr(jatekos, "kovetkezo_entitas_kedvezmeny", 0), 2)
    return _handled(f"Egi Emeles: {unit.lap.nev} visszakerult kezbe, a kovetkezo megidezett Entitas 2 auraval olcsobb.")


def handle_tengeri_delibab(card, jatekos, **_):
    ures = _first_empty_horizon(jatekos)
    if ures is None:
        return _handled("Tengeri Delibab: nincs ures Horizont hely a masolatnak.", partial=True)
    eredeti = next(iter(_allied_units(jatekos)), None)
    if eredeti is None:
        return _handled("Tengeri Delibab: nincs masolhato sajat Entitas.", partial=True)

    _, _, unit = eredeti
    masolat = _summon_token(
        jatekos,
        ures,
        f"{unit.lap.nev} Delibab",
        atk=unit.akt_tamadas,
        hp=1,
        race=getattr(unit.lap, "faj", "Illuzio"),
        realm=jatekos.birodalom,
        exhausted=True,
    )
    masolat.temp_mirage = True
    return _handled(f"Tengeri Delibab: ideiglenes 1 HP-s masolat jott letre {unit.lap.nev} alapjan.")


def handle_kod_alak(card, jatekos, **_):
    return _handled("Kod-Alak: spell-target reakcio aktiv, celzasra kezbe ter vissza es semlegesit.")


def handle_lopakodo_felcser_dron(card, jatekos, **_):
    return _handled("Lopakodo Felcser-Dron: spell/rituale target immunity aktiv.")


def handle_sivatagi_kem(card, jatekos, **_):
    return _handled("Sivatagi Kem: pecset-sebzes utan az ellenfel keze naplozodik.")


def handle_viharos_menekules(card, jatekos, ellenfel, **_):
    sajatok = list(_allied_units(jatekos))[:2]
    if not sajatok:
        return _handled("Viharos Menekules: nem volt visszaveheto sajat Entitas.", partial=True)

    visszavett = 0
    for zone_name, index, _ in sajatok:
        if ActionLibrary.return_target_to_hand(jatekos, zone_name, index, card.nev):
            visszavett += 1

    elpusztitott = 0
    if ellenfel is not None:
        for index, trap in enumerate(list(ellenfel.zenit)):
            if elpusztitott >= visszavett:
                break
            if not is_trap(trap):
                continue
            ellenfel.temeto.append(trap)
            set_zone_slot(ellenfel, "zenit", index, None, "viharos_menekules_destroy_trap")
            elpusztitott += 1

    return _handled(f"Viharos Menekules: {visszavett} sajat Entitas kerult kezbe vissza, es {elpusztitott} ellenseges Jel pusztult el.")


def handle_univerzalis_csere(card, jatekos, **_):
    eldobhato = list(jatekos.kez[:2])
    if not eldobhato:
        return _handled("Univerzalis Csere: nem volt eldobhato lap a kezben.", partial=True)

    for lap in eldobhato:
        jatekos.kez.remove(lap)
        jatekos.temeto.append(lap)
        naplo.ir(f"Univerzalis Csere: eldobva {lap.nev}.")

    huzando = len(eldobhato) * 2
    for _ in range(huzando):
        jatekos.huzas(extra=True)
    return _handled(f"Univerzalis Csere: {len(eldobhato)} lap eldobva, {huzando} lap huzva.")


def handle_goblin_taktika(card, jatekos, **_):
    summoned = 0
    for _ in range(2):
        ures = _first_empty_horizon(jatekos)
        if ures is None:
            break
        _summon_token(jatekos, ures, "Goblin Token", atk=1, hp=1, race="Goblin / Harcos", realm=jatekos.birodalom, exhausted=True)
        summoned += 1
    if summoned <= 0:
        return _handled("Goblin Taktika: nem volt ures Horizont hely a tokeneknek.", partial=True)
    return _handled(f"Goblin Taktika: {summoned} darab 1/1-es Goblin/Harcos token erkezett a Horizontra.", partial=summoned < 2)


def handle_sikatori_zsebtolvaj(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Sikatori Zsebtolvaj: nem volt ellenfel a kezinfohoz.", partial=True)
    ActionLibrary.inspect_opponent_hand(ellenfel, "Sikatori Zsebtolvaj")
    return _handled(f"Sikatori Zsebtolvaj: {ellenfel.nev} keze naplozva lett.")


def handle_tukrozodo_remeny(card, jatekos, **_):
    jatekos.tukrozodo_remeny_aktiv = True
    return _handled(f"Tukrozodo Remeny: {jatekos.nev} sajat Horizont seruleseit mostantol tukrozott erosodes kiseri.")


def handle_a_feny_utja(card, jatekos, **_):
    cel = min(_allied_units(jatekos), key=lambda data: (data[2].akt_hp, data[2].akt_tamadas), default=None)
    if cel is None:
        return _handled("A Feny Utja: nem volt sajat Entitas a vedelemhez.", partial=True)
    _, _, unit = cel
    unit.survival_shield_until_turn_end = True
    return _handled(f"A Feny Utja: {unit.lap.nev} a kor vegeig 1 HP-n tulelheti a kovetkezo vegzetes sebzest.")


def handle_a_feny_neve(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("A Feny Neve: nem volt ellenfel.", partial=True)
    from engine.effects import EffectEngine

    celpontok = list(_enemy_horizon_units(ellenfel))
    if not celpontok:
        return _handled("A Feny Neve: nem volt ellenseges Horizont Entitas.", partial=True)

    for _, _, unit in celpontok:
        _remove_keyword_temporarily(unit, "aegis")
        _remove_keyword_temporarily(unit, "ethereal")

    for _, index, unit in list(celpontok):
        aktualis = ellenfel.horizont[index]
        if aktualis is None:
            continue
        EffectEngine._deal_damage_to_target(card.nev, 1, ("horizont", index, aktualis), ellenfel, "Kepesseg", jatekos)

    return _handled(f"A Feny Neve: {len(celpontok)} ellenseges Horizont Entitas elvesztette ideiglenesen az Aegis/Ethereal kulcsszavait es 1 sebzest kapott.")


def handle_keresztes_hadjarat(card, jatekos, **_):
    units = list(_allied_units(jatekos))
    if not units:
        return _handled("Keresztes Hadjarat: nem volt sajat Entitas.", partial=True)
    for _, _, unit in units:
        _grant_keyword(unit, "celerity", temporary=True)
        _grant_temp_attack(unit, 1)
        unit.kimerult = False
    return _handled(f"Keresztes Hadjarat: {len(units)} sajat Entitas +1 ATK-t es ideiglenes Celerityt kapott.")


def handle_gyorsitott_menet(card, jatekos, **_):
    mozgatott = 0
    for from_index, unit in list(enumerate(jatekos.zenit)):
        if not _is_board_entity(unit):
            continue
        cel_index = from_index if jatekos.horizont[from_index] is None else _first_empty_horizon(jatekos)
        if cel_index is None:
            continue
        if ActionLibrary.move_entity_between_zones(jatekos, "zenit", from_index, "horizont", cel_index, card.nev, exhausted=False):
            moved = jatekos.horizont[cel_index]
            _grant_keyword(moved, "celerity", temporary=True)
            moved.kimerult = False
            mozgatott += 1
    if mozgatott <= 0:
        return _handled("Gyorsitott Menet: nem volt Horizontra mozgathato sajat Zenit Entitas.", partial=True)
    return _handled(f"Gyorsitott Menet: {mozgatott} sajat Entitas lepett a Zenitbol a Horizontra, ideiglenes Celerityvel.")


def handle_vamszedo_pont(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Vamszedo Pont: nem volt ellenfel a huzasfigyeleshez.", partial=True)
    ellenfel.vamszedo_pont_figyelo = jatekos
    return _handled(f"Vamszedo Pont: {jatekos.nev} mostantol masolhatja {ellenfel.nev} extra huzasait.")


def handle_martirok_vedelme(card, jatekos, **_):
    jatekos.martirok_vedelme_aktiv = True
    return _handled(f"Martirok Vedelme: {jatekos.nev} sajat Horizont halalai mostantol vedelmi visszaterest kaphatnak.")


def handle_megtorlo_feny(card, jatekos, **_):
    jatekos.megtorlo_feny_aktiv = True
    return _handled(f"Megtorlo Feny: {jatekos.nev} sajat serulesei mostantol visszacsapnak a tamadora.")


def handle_tornado_csapda(card, tamado_egyseg=None, tamado=None, vedo=None, **_):
    if tamado_egyseg is None or tamado is None:
        return {"resolved": False}
    try:
        index = tamado.horizont.index(tamado_egyseg)
    except ValueError:
        return {"resolved": False}
    ActionLibrary.return_target_to_hand(tamado, "horizont", index, card.nev)
    return _handled(
        f"Tornado Csapda: {tamado_egyseg.lap.nev} visszakerult kezbe, a tamadas megszakadt.",
        consume_trap=True,
        stop_attack=True,
    )


def handle_kitero_manover(card, jatekos, ellenfel, **_):
    cel = min(_allied_units(jatekos), key=lambda data: (data[2].akt_hp, data[2].akt_tamadas), default=None)
    if cel is None:
        return _handled("Kitero Manover: nem volt sajat Entitas a megmenteshez.", partial=True)
    zone_name, index, unit = cel
    if not ActionLibrary.return_target_to_hand(jatekos, zone_name, index, card.nev):
        return _handled("Kitero Manover: a celpont nem volt kezbe visszaveheto.", partial=True)

    tamadok = [data for data in _enemy_horizon_units(ellenfel) if not data[2].kimerult] if ellenfel is not None else []
    if tamadok:
        _, _, attacker = max(tamadok, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
        attacker.kimerult = True
        naplo.ir(f"Kitero Manover: {attacker.lap.nev} kimerult maradt a kitert tamadas utan.")
    return _handled(f"Kitero Manover: {unit.lap.nev} visszakerult kezbe es meguszta a pusztulast.", partial=not bool(tamadok))


def handle_megvesztegetes(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Megvesztegetes: nem volt ellenfel.", partial=True)
    jeloltek = [
        data for data in ActionLibrary._all_units(ellenfel)
        if getattr(data[2].lap, "magnitudo", 0) <= 3
    ]
    if not jeloltek:
        return _handled("Megvesztegetes: nem volt max 3 Magnitudos ellenseges Entitas.", partial=True)
    _, _, unit = max(jeloltek, key=lambda data: (data[2].akt_tamadas, data[2].akt_hp))
    ActionLibrary.prohibit_attack_or_block(unit, card.nev)
    return _handled(f"Megvesztegetes: {unit.lap.nev} ebben a korben nem tamadhat es nem blokkolhat.")


def handle_szegecsvihar(card, jatekos, ellenfel, **_):
    if ellenfel is None:
        return _handled("Szegecsvihar: nem volt ellenfel.", partial=True)
    from engine.effects import EffectEngine

    celpontok = list(_enemy_horizon_units(ellenfel))[:2]
    if not celpontok:
        return _handled("Szegecsvihar: nem volt ellenseges Entitas.", partial=True)
    kulonbozo = 0
    for zone_name, index, unit in celpontok:
        aktualis = getattr(ellenfel, zone_name)[index]
        if aktualis is None:
            continue
        EffectEngine._deal_damage_to_target(card.nev, 2, (zone_name, index, aktualis), ellenfel, "Kepesseg", jatekos)
        kulonbozo += 1
    return _handled(f"Szegecsvihar: {kulonbozo} kulonbozo ellenseges Entitas kapott 2-2 sebzest.", partial=kulonbozo < 2)


def handle_a_termeszet_szava(card, jatekos, **_):
    talalat = ActionLibrary.search_deck_by_predicate(
        jatekos,
        lambda lap: "bestia" in normalize_lookup_text(getattr(lap, "faj", "")) and "entitas" in normalize_lookup_text(getattr(lap, "kartyatipus", "")),
        to_hand=True,
        reason=card.nev,
    )
    if not talalat:
        return _handled("A Termeszet Szava: nem volt keresheto Bestia Entitas a pakliban.", partial=True)
    return _handled("A Termeszet Szava: egy Bestia Entitas a paklibol kezbe kerult.")


def handle_ujjaszuletes_fenye(card, jatekos, **_):
    from engine.effects import EffectEngine
    from engine.card import CsataEgyseg

    aldozat = next(iter(_allied_horizon_units(jatekos)), None)
    if aldozat is None:
        return _handled("Ujjaszuletes Fenye: nem volt felaldozhato sajat Horizont Entitas.", partial=True)
    zone_name, index, unit = aldozat
    aldozat_nev = unit.lap.nev
    EffectEngine.destroy_unit(jatekos, zone_name, index, None, card.nev)

    jeloltek = [
        lap for lap in jatekos.temeto
        if "entitas" in normalize_lookup_text(getattr(lap, "kartyatipus", ""))
        and getattr(lap, "nev", "") != aldozat_nev
    ]
    if not jeloltek:
        return _handled("Ujjaszuletes Fenye: nem volt masik visszahozhato Entitas az Uressegben.", partial=True)

    vissza = max(jeloltek, key=lambda lap: (lap.magnitudo, lap.tamadas, lap.eletero))
    jatekos.temeto.remove(vissza)
    uj = CsataEgyseg(vissza)
    uj.owner = jatekos
    uj.kimerult = True
    set_zone_slot(jatekos, "horizont", index, uj, "ujjaszuletes_fenye")
    trigger_engine.dispatch("on_summon", source=uj, owner=jatekos, payload={"zone": "horizont", "revived": True})
    return _handled(f"Ujjaszuletes Fenye: {aldozat_nev} aldozata utan {vissza.nev} visszatert ugyanarra a helyre, kimerulve.")


def handle_sivatagi_kem_pecset_sebzes(attacker, defender):
    if attacker is None or defender is None or not _is_named(attacker, "Sivatagi Kem"):
        return False
    ActionLibrary.inspect_opponent_hand(defender, "Sivatagi Kem")
    return True


def on_summon_priority(context):
    unit = context.source
    owner = context.owner
    if unit is None or owner is None:
        return

    if _is_named(unit, "Lopakodo Felcser-Dron"):
        state = TargetingEngine.target_state(unit)
        state.spell_negate = True
        naplo.ir(f"Lopakodo Felcser-Dron: {unit.lap.nev} nem celozhato ellenseges Igevel vagy Ritualeval.")

    if getattr(owner, "tomegtermeles_gyara_aktiv", False) and not getattr(owner, "tomegtermeles_gyara_triggerelt_ebben_a_korben", False):
        if _is_machine_card(unit.lap):
            owner.tomegtermeles_gyara_triggerelt_ebben_a_korben = True
            owner.ad_ideiglenes_aurat(1, "A Tomegtermeles Gyara")
            naplo.ir(f"A Tomegtermeles Gyara: {owner.nev} elso megfelelo idezese utan 1 ideiglenes aura jott letre.")


def on_spell_targeted_priority(context):
    target = context.target
    owner = context.payload.get("target_owner")
    if target is None or owner is None:
        return

    if _is_named(target, "Kod-Alak"):
        zone_name = context.payload.get("zone")
        index = context.payload.get("index")
        if zone_name is None or index is None:
            return
        if ActionLibrary.return_target_to_hand(owner, zone_name, index, "Kod-Alak"):
            context.cancelled = True
            naplo.ir(f"Kod-Alak: {target.lap.nev} visszatert kezbe, a rajta levo varazslat semlegesitve.")


def on_damage_taken_priority(context):
    target = context.target
    if target is None or not _is_board_entity(target):
        return

    cel_owner = context.payload.get("target_owner") or getattr(target, "owner", None)
    damage = int(context.payload.get("damage", 0) or 0)
    zona = context.payload.get("zone")
    source_unit = context.source if _is_board_entity(context.source) else context.payload.get("source_unit")
    source_owner = context.owner or getattr(source_unit, "owner", None)
    source_zone = context.payload.get("source_zone")
    source_index = context.payload.get("source_index")

    if cel_owner is not None and getattr(cel_owner, "tukrozodo_remeny_aktiv", False) and zona == "horizont" and damage > 0:
        masik = _best_other_allied_unit(cel_owner, excluded_unit=target)
        if masik is not None:
            _, _, celpont = masik
            celpont.bonus_max_hp = getattr(celpont, "bonus_max_hp", 0) + damage
            celpont.akt_hp += damage
            naplo.ir(f"Tukrozodo Remeny: {target.lap.nev} serulese utan {celpont.lap.nev} +{damage} maximalis HP-t kapott.")
        else:
            naplo.ir("Tukrozodo Remeny: nem volt masik sajat Entitas a tukrozott erosodeshez.")

    if (
        cel_owner is not None
        and getattr(cel_owner, "megtorlo_feny_aktiv", False)
        and damage > 0
        and _is_board_entity(source_unit)
        and source_owner is not None
        and source_zone in {"horizont", "zenit"}
        and source_index is not None
    ):
        from engine.effects import EffectEngine

        vissza = (damage + 1) // 2
        aktualis_source = getattr(source_owner, source_zone)[source_index]
        if aktualis_source is not None:
            EffectEngine._deal_damage_to_target("Megtorlo Feny", vissza, (source_zone, source_index, aktualis_source), source_owner, "Kepesseg", cel_owner)
            naplo.ir(f"Megtorlo Feny: {source_unit.lap.nev} visszakapott {vissza} sebzest.")


def on_turn_end_priority(context):
    owner = context.owner
    if owner is None:
        return

    for zone_name in ("horizont", "zenit"):
        zone = getattr(owner, zone_name)
        for index in range(len(zone) - 1, -1, -1):
            unit = zone[index]
            if _is_board_entity(unit) and getattr(unit, "temp_mirage", False):
                from engine.effects import EffectEngine

                EffectEngine.destroy_unit(owner, zone_name, index, context.target, "Tengeri Delibab")

    if getattr(owner, "kovetkezo_entitas_kedvezmeny", 0) > 0:
        owner.kovetkezo_entitas_kedvezmeny = 0

    for _, _, unit in _allied_units(owner):
        bonus = getattr(unit, "temp_atk_bonus_until_turn_end", 0)
        if bonus > 0:
            unit.akt_tamadas = max(0, unit.akt_tamadas - bonus)
            unit.temp_atk_bonus_until_turn_end = 0
        unit.survival_shield_until_turn_end = False
        unit.temp_granted_keywords = set()
        unit.temp_removed_keywords = set()

