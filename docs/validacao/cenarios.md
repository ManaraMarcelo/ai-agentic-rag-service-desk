# Cenários de testes funcionais

A bateria existente em main.py contém sete perguntas.

| Caso | Pergunta | Comportamento a verificar |
|---|---|---|
| 01 | Posso reembolsar a internet? | Consulta às políticas |
| 02 | Quero mais 5 dias de trabalho remoto. Como faço? | Tratamento de exceção |
| 03 | Posso reembolsar cursos ou treinamentos da Alura? | Consulta sobre treinamento |
| 04 | É possível reembolsar certificações do Google Cloud? | Consulta sobre certificação |
| 05 | Posso obter o Google Gemini de graça? | Consulta sobre ferramentas |
| 06 | Preciso de ajuda com uma política. | Solicitação de informações |
| 07 | Quantas capivaras tem no Rio Pinheiros? | Tratamento de pergunta fora de escopo |

## Critérios de avaliação

- Decisão de triagem coerente.
- Resposta baseada nos documentos disponíveis.
- Citações sem duplicidade.
- Limite de três citações.
- Ausência de resposta inventada fora do contexto.

Os critérios acima são expectativas de validação,
não resultados de execução.
