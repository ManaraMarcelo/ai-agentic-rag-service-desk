import unittest

from utils_loader import _clean_text


class TestNormalizacao(unittest.TestCase):

    def test_quebras_de_linha(self):
        self.assertEqual(
            _clean_text("Politica\n de\r\n reembolso"),
            "Politica de reembolso",
        )

    def test_tabulacoes(self):
        self.assertEqual(
            _clean_text("RH\t\tTI"),
            "RH TI",
        )

    def test_espacos_externos(self):
        self.assertEqual(
            _clean_text("  Service Desk  "),
            "Service Desk",
        )

    def test_texto_vazio(self):
        self.assertEqual(_clean_text(""), "")

    def test_valor_nulo(self):
        self.assertEqual(_clean_text(None), "")


if __name__ == "__main__":
    unittest.main()
