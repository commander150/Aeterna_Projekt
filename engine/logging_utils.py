from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from engine.config import get_active_engine_config
from utils.logger import Naplozo, naplo


def ensure_log_directory(base_dir, now=None):
    now = now or datetime.now()
    log_dir = os.path.join(base_dir, "LOG", now.strftime("%Y"), now.strftime("%m"))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def build_log_path(base_dir, now=None):
    now = now or datetime.now()
    log_dir = ensure_log_directory(base_dir, now)
    filename = f"AETERNA_LOG_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    return os.path.join(log_dir, filename)


def _format_enabled_items(items):
    items = list(items)
    return ", ".join(items) if items else "none"


def build_log_header(startup_config_text, engine_config=None, now=None):
    now = now or datetime.now()
    engine_config = engine_config or get_active_engine_config()
    return [
        f"AETERNA LOG - {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Startup konfiguracio: {startup_config_text}",
        f"Aktiv engine konfiguracio: {engine_config.describe()}",
        f"run_mode: {engine_config.run_mode}",
        f"enabled modules: {_format_enabled_items(engine_config.active_modules())}",
        f"enabled flags: {_format_enabled_items(engine_config.active_flags())}",
        "",
    ]


def create_logger(config=None, base_dir=".", now=None, logger: Optional[Naplozo] = None):
    now = now or datetime.now()
    logger = logger or naplo
    log_base_dir = getattr(config, "log_base_dir", None) or base_dir
    engine_config = config.to_engine_config() if config and hasattr(config, "to_engine_config") else get_active_engine_config()
    startup_text = config.describe() if config and hasattr(config, "describe") else "none"
    log_path = build_log_path(log_base_dir, now)
    logger.start_log(log_path, header_lines=build_log_header(startup_text, engine_config=engine_config, now=now))
    return logger


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
