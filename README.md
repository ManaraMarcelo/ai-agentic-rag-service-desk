# 🤖 Assistente Inteligente de Service Desk (Agentic RAG)

Projeto final desenvolvido para a disciplina de Inteligência Artificial. O sistema atua como um agente de triagem e atendimento automático de Service Desk (RH e TI) para a empresa fictícia **Carraro Desenvolvimento**, utilizando **Retrieval-Augmented Generation (RAG)** e orquestração de múltiplos estados com **LangGraph**.

---

## 👥 Integrantes da Equipe
* **Marcelo Manara** – Arquitetura de IA, Engenharia de Prompt, Saída Estruturada (`Pydantic`) e Orquestração (`LangGraph`).
* **Marcelo Belotto** – Pipeline de Dados, Ingestão de PDFs (`PyMuPDF`), Chunking e Indexação Vetorial (`FAISS`).
* **Vinicius Emanuel** – Configuração de Ambiente, Extração/Formatação de Citações e Bateria de Testes.
* **Lucas Vieira** – Elaboração da Base de Conhecimento (PDFs de Políticas Internas), Documentação e Apresentação.

---

## 🎯 Objetivo e Funcionamento
Setores de suporte interno lidam diariamente com um alto volume de dúvidas sobre regras corporativas misturadas a solicitações operacionais. Este projeto resolve esse gargalo através de um fluxo inteligente dividido em etapas:

1. **Triagem Estruturada (`Pydantic` + `Gemini 2.5 Flash`):** Analisa a mensagem do colaborador e classifica a intenção em um formato JSON rigoroso contendo a decisão (`AUTO_RESOLVER`, `PEDIR_INFO` ou `ABRIR_CHAMADO`), o nível de urgência (`BAIXA`, `MEDIA`, `ALTA`) e possíveis campos faltantes.
2. **Busca Semântica e RAG (`FAISS` + `gemini-embedding-001`):** Caso a dúvida seja sobre políticas internas (`AUTO_RESOLVER`), o sistema consulta os documentos PDF na pasta `dados/`, recupera os trechos mais relevantes e gera uma resposta estritamente baseada no contexto, exibindo o **nome do arquivo PDF, a página e o trecho exato** utilizado.
3. **Orquestração e Fallback Inteligente (`LangGraph`):**
   * Se o RAG encontrar embasamento nos documentos, a resposta é entregue com as citações.
   * Se o documento não contiver a resposta (prevenção contra alucinações), o grafo avalia se há palavras-chave de exceção/liberação para converter automaticamente em abertura de chamado (`ABRIR_CHAMADO`), ou solicita mais detalhes ao usuário (`PEDIR_INFO`).

---

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.10+
* **LLM & Embeddings:** Google Gemini (`models/gemini-2.5-flash` e `models/gemini-embedding-001`) via `langchain-google-genai`
* **Orquestração de Agentes:** `LangGraph` e `LangChain`
* **Banco de Dados Vetorial:** `FAISS` (`faiss-cpu`)
* **Processamento de Documentos:** `PyMuPDF` (`fitz`) e `RecursiveCharacterTextSplitter`
* **Validação de Dados:** `Pydantic`

---

## 📂 Estrutura do Projeto

```text
├── dados/                      # Diretório contendo os PDFs de políticas internas da empresa
├── main.ipynb                  # Notebook interativo com todo o pipeline passo a passo
├── requirements.txt            # Lista de dependências do projeto
├── .env.example                # Exemplo de configuração de variáveis de ambiente
└── README.md                   # Documentação do projeto