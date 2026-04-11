import unittest
from types import SimpleNamespace

from engine.keyword_engine import KeywordEngine
from engine.triggers import trigger_engine


class DummyUnit:
    def __init__(self, kepesseg, magnitudo=5):
        self.lap = SimpleNamespace(nev="Teszt", kepesseg=kepesseg, magnitudo=magnitudo)
        self.kimerult = False
        self.akt_tamadas = 3
        self.akt_hp = 3
        self.bane_target = False
        self.owner = SimpleNamespace(nev="TesztJatekos")


class TestKeywordRules(unittest.TestCase):
    def test_get_harmonize_bonus_depends_on_support_magnitude(self):
        attacker = DummyUnit("")

        support_small = DummyUnit("Harmonizálás", magnitudo=4)
        support_mid = DummyUnit("Harmonizálás", magnitudo=8)
        support_large = DummyUnit("Harmonizálás", magnitudo=9)

        self.assertEqual(KeywordEngine.get_harmonize_bonus(attacker, support_small), 2)
        self.assertEqual(KeywordEngine.get_harmonize_bonus(attacker, support_mid), 1)
        self.assertEqual(KeywordEngine.get_harmonize_bonus(attacker, support_large), 0)

    def test_filter_blockers_for_ethereal_attacker(self):
        attacker = DummyUnit("Légies")
        ethereal_blocker = DummyUnit("Légies")
        normal_blocker = DummyUnit("-")

        filtered = KeywordEngine.filter_blockers_for_attacker(
            attacker, [ethereal_blocker, normal_blocker]
        )

        self.assertEqual(filtered, [ethereal_blocker])

    def test_resolve_bane_destroys_marked_target(self):
        attacker = DummyUnit("Métely")
        defender = DummyUnit("-")
        defender.bane_target = True

        calls = {"count": 0}

        def destroy():
            calls["count"] += 1
            return True

        result = KeywordEngine.resolve_bane(attacker, defender, destroy)

        self.assertTrue(result)
        self.assertEqual(calls["count"], 1)

    def test_on_damage_dealt_emits_combat_damage_event(self):
        attacker = DummyUnit("-")
        defender = DummyUnit("-")
        seen = []

        def _handler(context):
            seen.append(context.event_name)

        trigger_engine.register("on_combat_damage_dealt", _handler)
        try:
            KeywordEngine.on_damage_dealt(attacker, defender)
        finally:
            trigger_engine._handlers["on_combat_damage_dealt"].remove(_handler)

        self.assertIn("on_combat_damage_dealt", seen)

    def test_taunt_blockers_are_mandatory(self):
        taunt_blocker = DummyUnit("Taunt")
        normal_blocker = DummyUnit("-")
        defender = SimpleNamespace(horizont=[taunt_blocker, normal_blocker, None, None, None, None])

        blockers = KeywordEngine.get_blockers(defender)

        self.assertEqual(blockers, [taunt_blocker])

    def test_exhausted_taunt_does_not_remain_forced_blocker(self):
        taunt_blocker = DummyUnit("Taunt")
        taunt_blocker.kimerult = True
        normal_blocker = DummyUnit("-")
        defender = SimpleNamespace(horizont=[taunt_blocker, normal_blocker, None, None, None, None])

        blockers = KeywordEngine.get_blockers(defender)

        self.assertEqual(blockers, [normal_blocker])


if __name__ == "__main__":
    unittest.main()
