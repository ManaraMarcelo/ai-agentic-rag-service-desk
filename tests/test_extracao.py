import unittest

from utils_loader import extrair_trecho


class TestExtracao(unittest.TestCase):

    def test_termo_encontrado(self):
        texto = "A politica permite reembolso de internet."
        trecho = extrair_trecho(texto, "reembolso")
        self.assertIn("reembolso", trecho)

    def test_limite_da_janela(self):
        texto = "a" * 300 + " internet " + "b" * 300
        trecho = extrair_trecho(texto, "internet", 100)
        self.assertLessEqual(len(trecho), 100)

    def test_sem_correspondencia(self):
        texto = "a" * 300
        self.assertEqual(
            extrair_trecho(texto, "internet", 100),
            "a" * 50,
        )

    def test_texto_vazio(self):
        self.assertEqual(
            extrair_trecho("", "internet"),
            "",
        )

    def test_ignora_maiusculas(self):
        texto = "Politica de INTERNET"
        self.assertIn(
            "INTERNET",
            extrair_trecho(texto, "internet"),
        )


if __name__ == "__main__":
    unittest.main()
