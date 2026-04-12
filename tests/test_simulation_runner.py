import unittest

from simulation.runner import _valassz_birodalmat


class TestSimulationRunnerRealmNormalization(unittest.TestCase):
    def test_valassz_birodalmat_accepts_lowercase_realm(self):
        result = _valassz_birodalmat("terra", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Terra")

    def test_valassz_birodalmat_accepts_uppercase_realm(self):
        result = _valassz_birodalmat("VENTUS", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Ventus")

    def test_valassz_birodalmat_keeps_canonical_realm(self):
        result = _valassz_birodalmat("Terra", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Terra")

    def test_valassz_birodalmat_unknown_realm_raises_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            _valassz_birodalmat("ismeretlen", ["Aether", "Terra", "Ventus"], random_fallback=False)

        message = str(ctx.exception)
        self.assertIn("kert birodalom nem elerheto", message)
        self.assertIn("Aether, Terra, Ventus", message)


if __name__ == "__main__":
    unittest.main()
