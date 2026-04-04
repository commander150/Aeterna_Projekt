from dataclasses import dataclass, field


@dataclass
class TargetState:
    targetable: bool = True
    untargetable: bool = False
    spell_negate: bool = False
    trap_negate: bool = False
    burst_response: bool = True
    return_to_hand_allowed: bool = True
    exhaust_target_allowed: bool = True
    reasons: list[str] = field(default_factory=list)


class TargetingEngine:
    @staticmethod
    def target_state(target):
        existing = getattr(target, "target_state", None)
        if isinstance(existing, TargetState):
            return existing

        state = TargetState()
        setattr(target, "target_state", state)
        return state

    @staticmethod
    def validate(target, action):
        state = TargetingEngine.target_state(target)

        if not state.targetable or state.untargetable:
            state.reasons.append("untargetable")
            return False, state

        if action == "spell" and state.spell_negate:
            state.reasons.append("spell_negate")
            return False, state

        if action == "trap" and state.trap_negate:
            state.reasons.append("trap_negate")
            return False, state

        if action == "burst" and not state.burst_response:
            state.reasons.append("burst_response_blocked")
            return False, state

        if action == "return_to_hand" and not state.return_to_hand_allowed:
            state.reasons.append("return_to_hand_blocked")
            return False, state

        if action == "exhaust" and not state.exhaust_target_allowed:
            state.reasons.append("exhaust_blocked")
            return False, state

        return True, state
