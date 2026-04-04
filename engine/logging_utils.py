from utils.logger import naplo


def log_flag_skip(effect_name, flag_name, category="FLAG_OFF"):
    naplo.ir(f"[SKIP:{category}] {effect_name} | mechanika kikapcsolva: {flag_name}")


def log_rule_skip(effect_name, reason):
    naplo.ir(f"[SKIP:RULE] {effect_name} | {reason}")


def log_target_skip(effect_name, reason):
    naplo.ir(f"[SKIP:TARGET] {effect_name} | {reason}")


def log_limit_skip(effect_name, reason):
    naplo.ir(f"[SKIP:LIMIT] {effect_name} | {reason}")


def log_unresolved(effect_name, reason="Card effect parser missing"):
    naplo.ir(f"[UNRESOLVED] {effect_name} | {reason}")
