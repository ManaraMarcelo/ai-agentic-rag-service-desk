# Execução e apresentação dos resultados

## Testes unitários

```powershell
python -m unittest discover -s tests -v
```

Os testes isolam as funções utilitárias e não utilizam
credenciais, embeddings ou chamadas ao Gemini.

## Testes funcionais

```powershell
python main.py
```

A saída apresenta:

- Pergunta.
- Decisão da triagem.
- Urgência.
- Ação final.
- Resposta.
- Documento, página e trecho das citações.

## Intervalo entre consultas

A implementação utiliza time.sleep(5) após cada pergunta.

Esse intervalo reduz a frequência das chamadas, mas não
garante conformidade com todas as cotas da API.

Uma melhoria futura seria implementar tratamento de HTTP 429,
tentativas limitadas e exponential backoff.

Os testes funcionais dependem de uma chave válida e acesso à API.
