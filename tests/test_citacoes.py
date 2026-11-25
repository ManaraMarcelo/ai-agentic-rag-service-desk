import unittest
from types import SimpleNamespace

from utils_loader import formatar_citacoes


def documento(nome, pagina):
    return SimpleNamespace(
        metadata={
            "source": f"dados/{nome}",
            "page": pagina,
        },
        page_content="Politica de reembolso de internet.",
    )


class TestCitacoes(unittest.TestCase):

    def test_nome_do_documento(self):
        resultado = formatar_citacoes(
            [documento("politica.pdf", 0)],
            "internet",
        )
        self.assertEqual(
            resultado[0]["documento"],
            "politica.pdf",
        )

    def test_numeracao_da_pagina(self):
        resultado = formatar_citacoes(
            [documento("politica.pdf", 0)],
            "internet",
        )
        self.assertEqual(resultado[0]["pagina"], 1)

    def test_deduplicacao(self):
        docs = [
            documento("politica.pdf", 0),
            documento("politica.pdf", 0),
        ]
        self.assertEqual(
            len(formatar_citacoes(docs, "internet")),
            1,
        )

    def test_documentos_distintos(self):
        docs = [
            documento("rh.pdf", 0),
            documento("ti.pdf", 0),
        ]
        self.assertEqual(
            len(formatar_citacoes(docs, "internet")),
            2,
        )

    def test_limite_tres_citacoes(self):
        docs = [
            documento("politica.pdf", i)
            for i in range(5)
        ]
        resultado = formatar_citacoes(docs, "internet")
        self.assertEqual(len(resultado), 3)
        self.assertEqual(
            [c["pagina"] for c in resultado],
            [1, 2, 3],
        )

    def test_sem_documentos(self):
        self.assertEqual(
            formatar_citacoes([], "internet"),
            [],
        )

    def test_conteudo_do_trecho(self):
        resultado = formatar_citacoes(
            [documento("politica.pdf", 0)],
            "internet",
        )
        self.assertIn("internet", resultado[0]["trecho"])


if __name__ == "__main__":
    unittest.main()
