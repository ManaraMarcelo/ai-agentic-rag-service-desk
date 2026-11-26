# Extração de trechos

A função extrair_trecho:

1. Normaliza o conteúdo recuperado.
2. Extrai palavras da pergunta com expressão regular.
3. Considera termos com pelo menos quatro caracteres.
4. Procura a primeira ocorrência de um termo elegível.
5. Delimita uma janela de texto ao redor da ocorrência.

A janela padrão é de 240 caracteres.

Quando nenhum termo é encontrado, a posição inicial é zero.
Nesse caso, a implementação atual retorna até metade da janela.

A seleção é heurística e não garante correspondência exata
entre cada afirmação da resposta e o trecho apresentado.
