# Formatação de citações

A função formatar_citacoes retorna uma lista de dicionários:

- documento: nome do arquivo de origem.
- pagina: índice da página convertido para numeração iniciada em 1.
- trecho: janela textual extraída do conteúdo recuperado.

## Deduplicação

O conjunto seen utiliza a chave (documento, pagina).

Ocorrências repetidas da mesma página são descartadas.

Páginas iguais pertencentes a documentos diferentes são preservadas.

## Limite

São retornadas até três citações distintas, respeitando
a ordem dos documentos recebidos pelo formatador.

As citações representam documentos recuperados pelo RAG,
não uma comprovação individual de cada afirmação gerada.
