from engine.card import CsataEgyseg
from utils.logger import naplo


def _object_name(obj):
    if obj is None:
        return "None"
    if hasattr(obj, "lap") and hasattr(obj.lap, "nev"):
        return obj.lap.nev
    return getattr(obj, "nev", type(obj).__name__)


def _object_type(obj):
    if obj is None:
        return "None"
    return type(obj).__name__


def _is_board_entity(obj):
    return isinstance(obj, CsataEgyseg) or (
        obj is not None
        and hasattr(obj, "kimerult")
        and hasattr(obj, "lap")
        and hasattr(obj.lap, "nev")
    )


def is_entity(obj):
    return _is_board_entity(obj)


def is_trap(obj):
    return obj is not None and not _is_board_entity(obj)


def is_zenit_entity(obj):
    return _is_board_entity(obj)


def is_attackable_zenit_target(obj):
    return _is_board_entity(obj)


def log_zone_write(owner, zone_name, slot_index, obj, reason):
    if obj is None:
        naplo.ir(
            f"[DEBUG:ZONE_WRITE] {getattr(owner, 'nev', 'ismeretlen')} | {zone_name}[{slot_index}] <- None | reason={reason}"
        )
        return

    if not _is_board_entity(obj):
        naplo.ir(
            f"[DEBUG:NON_ENTITY_ZONE_WRITE] {getattr(owner, 'nev', 'ismeretlen')} | {zone_name}[{slot_index}] | tipus={_object_type(obj)} | nev={_object_name(obj)} | reason={reason}"
        )
    else:
        naplo.ir(
            f"[DEBUG:ZONE_WRITE] {getattr(owner, 'nev', 'ismeretlen')} | {zone_name}[{slot_index}] | tipus={_object_type(obj)} | nev={_object_name(obj)} | reason={reason}"
        )


def set_zone_slot(owner, zone_name, slot_index, obj, reason):
    zone = getattr(owner, zone_name)
    zone[slot_index] = obj
    log_zone_write(owner, zone_name, slot_index, obj, reason)
    return obj
