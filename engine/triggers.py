from collections import defaultdict
from dataclasses import dataclass, field


EVENT_NAMES = (
    "on_play",
    "on_summon",
    "on_attack_declared",
    "on_spell_targeted",
    "on_damage_taken",
    "on_destroyed",
    "on_turn_start",
    "on_turn_end",
    "on_manifestation_phase",
    "on_awakening_phase",
    "on_position_changed",
)


@dataclass
class EventContext:
    event_name: str
    source: object | None = None
    owner: object | None = None
    target: object | None = None
    payload: dict = field(default_factory=dict)
    cancelled: bool = False


class TriggerEngine:
    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event_name, handler):
        self._handlers[event_name].append(handler)

    def dispatch(self, event_name, source=None, owner=None, target=None, payload=None):
        context = EventContext(
            event_name=event_name,
            source=source,
            owner=owner,
            target=target,
            payload=dict(payload or {}),
        )
        for handler in list(self._handlers.get(event_name, [])):
            handler(context)
        return context


trigger_engine = TriggerEngine()
