import unittest
from types import SimpleNamespace

from backend.facade import create_match, drop_match, get_legal_actions, get_match_result, get_snapshot
from backend.legal_actions import get_legal_actions_for_player
from backend.snapshot import export_match_snapshot
from engine.game_state import MatchState


def make_card(name, realm="Ignis", card_type="Entitas", aura=1, magnitude=1):
    lower_type = card_type.lower()
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        birodalom=realm,
        klan="Teszt Klan",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=2 if "entitas" in lower_type else 0,
        eletero=3 if "entitas" in lower_type else 0,
        egyseg_e="entitas" in lower_type,
        jel_e="jel" in lower_type,
        spell_e="ige" in lower_type,
        reakcio_e=False,
    )


def make_card_pool():
    cards = []
    for index in range(10):
        cards.append(make_card(f"Ignis Lap {index}", realm="Ignis"))
        cards.append(make_card(f"Aqua Lap {index}", realm="Aqua"))
    return cards


class TestBackendStateContext(unittest.TestCase):
    def test_snapshot_exports_active_player_phase_and_finished_state_from_match_state(self):
        p1 = SimpleNamespace(nev="P1", birodalom="Ignis", pakli=[], kez=[], temeto=[], pecsetek=[], osforras=[], horizont=[None] * 6, zenit=[None] * 6, overflow_vereseg=False)
        p2 = SimpleNamespace(nev="P2", birodalom="Aqua", pakli=[], kez=[], temeto=[], pecsetek=[], osforras=[], horizont=[None] * 6, zenit=[None] * 6, overflow_vereseg=False)
        game = SimpleNamespace(
            kor=4,
            p1=p1,
            p2=p2,
            log_metrics={},
            state=MatchState(p1, p2, kor=4, active_player=p2, phase="combat", match_finished=True, winner=p2, victory_reason="overflow"),
        )

        snapshot = export_match_snapshot(game)

        self.assertEqual(snapshot["turn"], 4)
        self.assertEqual(snapshot["active_player"], "P2")
        self.assertEqual(snapshot["phase"], "combat")
        self.assertTrue(snapshot["match_finished"])
        self.assertEqual(snapshot["winner"], "P2")
        self.assertEqual(snapshot["victory_reason"], "overflow")

    def test_facade_result_includes_phase_and_active_player(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
                "random_seed": 13,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        snapshot = get_snapshot(match_id)
        result = get_match_result(match_id)

        self.assertEqual(snapshot["active_player"], "Jatekos_1")
        self.assertEqual(snapshot["phase"], "play")
        self.assertFalse(snapshot["match_finished"])
        self.assertEqual(result["active_player"], "Jatekos_1")
        self.assertEqual(result["phase"], "play")

    def test_legal_actions_return_empty_for_non_active_player_or_non_play_phase(self):
        active = SimpleNamespace(
            nev="Aktiv",
            birodalom="Ignis",
            kez=[],
            horizont=[None] * 6,
            zenit=[None] * 6,
            osforras=[],
            elerheto_aura=lambda: 0,
            effektiv_aura_koltseg=lambda lap: getattr(lap, "aura_koltseg", 0),
        )
        inactive = SimpleNamespace(
            nev="Varakozo",
            birodalom="Aqua",
            kez=[],
            horizont=[None] * 6,
            zenit=[None] * 6,
            osforras=[],
            elerheto_aura=lambda: 0,
            effektiv_aura_koltseg=lambda lap: getattr(lap, "aura_koltseg", 0),
        )
        game = SimpleNamespace(state=MatchState(active, inactive, active_player=active, phase="combat", match_finished=False))

        self.assertEqual(get_legal_actions_for_player(game, active), [])
        game.state.phase = "play"
        self.assertEqual(get_legal_actions_for_player(game, inactive), [])

    def test_facade_legal_actions_respects_state_context(self):
        match_id = create_match(
            {
                "cards": make_card_pool(),
                "player1_realm": "Ignis",
                "player2_realm": "Aqua",
                "random_realm_fallback": False,
            }
        )
        self.addCleanup(lambda: drop_match(match_id))

        self.assertIsInstance(get_legal_actions(match_id, "p1"), list)
        self.assertEqual(get_legal_actions(match_id, "p2"), [])
