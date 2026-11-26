"""Carrega utilitarios sem inicializar Gemini ou FAISS."""

import ast
import pathlib
import re
from typing import List, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]

source = (ROOT / "main.py").read_text(encoding="utf-8-sig")
tree = ast.parse(source)

names = {
    "_clean_text",
    "extrair_trecho",
    "formatar_citacoes",
}

functions = [
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in names
]

if {node.name for node in functions} != names:
    raise RuntimeError("Funcoes utilitarias nao encontradas.")

module = ast.Module(body=functions, type_ignores=[])

namespace = {
    "re": re,
    "pathlib": pathlib,
    "List": List,
    "Dict": Dict,
}

exec(
    compile(module, str(ROOT / "main.py"), "exec"),
    namespace,
)

_clean_text = namespace["_clean_text"]
extrair_trecho = namespace["extrair_trecho"]
formatar_citacoes = namespace["formatar_citacoes"]
