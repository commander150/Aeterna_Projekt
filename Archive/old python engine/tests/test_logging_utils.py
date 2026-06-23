import os
import unittest
from datetime import datetime

from engine.config import EngineConfig
from engine.logging_utils import build_log_header, build_log_path, ensure_log_directory


class TestLoggingUtils(unittest.TestCase):
    def test_log_directory_uses_year_and_month_structure(self):
        base_dir = os.path.join(os.getcwd(), "test_logs_workspace")
        now = datetime(2026, 4, 4, 13, 46, 19)
        log_dir = ensure_log_directory(base_dir, now)
        self.assertTrue(log_dir.endswith(os.path.join("LOG", "2026", "04")))
        self.assertTrue(os.path.isdir(log_dir))

    def test_log_path_uses_timestamped_aeterna_filename(self):
        base_dir = os.path.join(os.getcwd(), "test_logs_workspace")
        now = datetime(2026, 4, 4, 13, 46, 19)
        path = build_log_path(base_dir, now)
        self.assertTrue(path.endswith(os.path.join("LOG", "2026", "04", "AETERNA_LOG_2026-04-04_13-46-19.txt")))

    def test_header_contains_required_engine_information(self):
        engine_config = EngineConfig(
            run_mode="debug_custom_flags",
            expansion_modules={"advanced_keywords": True},
            expansion_flags={"keyword_stealth": True},
        )
        lines = build_log_header("startup-config", engine_config=engine_config, now=datetime(2026, 4, 4, 13, 46, 19))
        joined = "\n".join(lines)
        self.assertIn("Startup konfiguracio: startup-config", joined)
        self.assertIn("run_mode: debug_custom_flags", joined)
        self.assertIn("enabled modules: advanced_keywords", joined)
        self.assertIn("enabled flags: keyword_stealth", joined)


if __name__ == "__main__":
    unittest.main()
