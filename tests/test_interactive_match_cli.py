import unittest
from types import SimpleNamespace

from simulation import interactive_match_cli


def make_card(name, realm="Ignis", card_type="Entitas", aura=1, magnitude=1):
    lower_type = card_type.lower()
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg="",
        birodalom=realm,
        klan="Teszt Klan",
        faj="Teszt Faj",
        kaszt="Teszt Kaszt",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=2 if "entitas" in lower_type else 0,
        eletero=3 if "entitas" in lower_type else 0,
        egyseg_e="entitas" in lower_type,
        jel_e="jel" in lower_type,
        sik_e="sik" in lower_type,
        spell_e="ige" in lower_type,
        reakcio_e=False,
    )


def make_card_pool():
    cards = []
    for index in range(10):
        cards.append(make_card(f"Ignis Lap {index}", realm="Ignis"))
        cards.append(make_card(f"Aqua Lap {index}", realm="Aqua"))
    return cards


class TestInteractiveMatchCli(unittest.TestCase):
    def test_build_match_config_normalizes_realms(self):
        config = interactive_match_cli.build_match_config(
            player1_realm="terra",
            player2_realm="VENTUS",
            random_seed=11,
            xlsx_path="cards.xlsx",
        )

        self.assertEqual(config["player1_realm"], "Terra")
        self.assertEqual(config["player2_realm"], "Ventus")
        self.assertEqual(config["random_seed"], 11)
        self.assertEqual(config["xlsx_path"], "cards.xlsx")

    def test_launch_interactive_match_cli_creates_match_lists_actions_and_executes_end_turn(self):
        printed_lines = []
        inputs = iter(["1", "q"])

        result = interactive_match_cli.launch_interactive_match_cli(
            match_config={
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 19,
            },
            input_func=lambda _: next(inputs),
            print_func=printed_lines.append,
        )

        joined = "\n".join(printed_lines)
        self.assertEqual(result["status"], "quit")
        self.assertIn("=== AKTUALIS ALLAPOT ===", joined)
        self.assertIn("Aktiv jatekos:", joined)
        self.assertIn("=== LEGAL AKCIOK ===", joined)
        self.assertIn("end_turn", joined)
        self.assertIn("=== ACTION EREDMENY ===", joined)
        self.assertIn("tipus=end_turn", joined)
        self.assertIn("turn_advanced", joined)

    def test_launch_interactive_match_cli_handles_invalid_realm_gracefully(self):
        printed_lines = []

        result = interactive_match_cli.launch_interactive_match_cli(
            match_config={
                "cards": make_card_pool(),
                "player1_realm": "NincsIlyen",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            },
            input_func=lambda _: "q",
            print_func=printed_lines.append,
        )

        joined = "\n".join(printed_lines)
        self.assertEqual(result["status"], "startup_error")
        self.assertIn("Nem sikerult meccset letrehozni.", joined)
        self.assertIn("Nem elerheto birodalom", joined)

    def test_main_uses_cli_args_without_start_prompt(self):
        captured = {}

        def fake_launch(**kwargs):
            captured.update(kwargs)
            return {"status": "quit"}

        original_launch = interactive_match_cli.launch_interactive_match_cli
        try:
            interactive_match_cli.launch_interactive_match_cli = fake_launch
            result = interactive_match_cli.main(
                argv=["--p1", "ignis", "--p2", "AQUA", "--seed", "7"],
                input_func=lambda _: "",
                print_func=lambda *_: None,
            )
        finally:
            interactive_match_cli.launch_interactive_match_cli = original_launch

        self.assertEqual(result["status"], "quit")
        self.assertEqual(captured["match_config"]["player1_realm"], "Ignis")
        self.assertEqual(captured["match_config"]["player2_realm"], "Aqua")
        self.assertEqual(captured["match_config"]["random_seed"], 7)
