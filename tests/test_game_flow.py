import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from engine.game import AeternaSzimulacio


def make_card(name, card_type="Entitas", magnitude=1, aura=1):
    return SimpleNamespace(
        nev=name,
        kartyatipus=card_type,
        kepesseg="",
        birodalom="Aether",
        klan="",
        faj="",
        kaszt="",
        magnitudo=magnitude,
        aura_koltseg=aura,
        tamadas=1,
        eletero=1,
        egyseg_e="Entitas" in card_type,
        jel_e="Jel" in card_type,
        reakcio_e=False,
    )


class TestGameFlow(unittest.TestCase):
    def test_kijatszas_fazis_skips_spell_effect_when_spell_trap_cancels(self):
        sim = object.__new__(AeternaSzimulacio)
        spell = make_card("Villam", card_type="Ige", magnitude=1, aura=1)
        caster = SimpleNamespace(
            nev="Caster",
            kez=[spell],
            osforras=[{"lap": make_card("Forras"), "hasznalt": False}],
            temeto=[],
            elerheto_aura=lambda: 1,
            effektiv_aura_koltseg=lambda lap: 1,
            fizet=lambda lap: True,
        )
        defender = SimpleNamespace(nev="Defender")
        sim.p1 = caster
        sim.p2 = defender
        sim._alkalmaz_kartya_hatast = Mock(return_value=None)
        sim._resolve_spell_cast_traps = Mock(return_value={"consume_trap": True, "cancelled_spell": True})

        result = AeternaSzimulacio.kijatszas_fazis(sim, caster)

        self.assertIsNone(result)
        sim._resolve_spell_cast_traps.assert_called_once_with(spell, caster, defender)
        sim._alkalmaz_kartya_hatast.assert_not_called()
        self.assertIn(spell, caster.temeto)
        self.assertNotIn(spell, caster.kez)


if __name__ == "__main__":
    unittest.main()
