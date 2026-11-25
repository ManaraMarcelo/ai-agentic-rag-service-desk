# Normalização de texto

A função _clean_text utiliza:

```python
re.sub(r"\s+", " ", s or "").strip()
```

A expressão regular substitui sequências de espaços, tabulações
e quebras de linha por um único espaço.

O método strip remove espaços das extremidades.

Exemplo:

Entrada: "Politica\n de\t reembolso"

Saída: "Politica de reembolso"

Valores vazios ou None resultam em uma string vazia.
