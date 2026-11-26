import os
import re
import time
import pathlib
import textwrap
import warnings
from pathlib import Path
from typing import Literal, List, Dict, TypedDict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Oculta avisos internos de bibliotecas para manter o terminal limpo
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langgraph.graph import StateGraph, START, END

# --- 1. CONFIGURAÇÃO DE AMBIENTE E MODELO ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("Chave GOOGLE_API_KEY não encontrada no arquivo .env")

llm_triagem = ChatGoogleGenerativeAI(
    model="models/gemini-3.5-flash-lite", 
    api_key=GOOGLE_API_KEY
)

# --- 2. CAMADA DE TRIAGEM (PYDANTIC) ---
TRIAGEM_PROMPT = (
    "Você é um triador de Service Desk para políticas internas da empresa Carraro Desenvolvimento. "
    "Dada a mensagem do usuário, retorne SOMENTE um JSON com:\n"
    "{\n"
    '  "decisao": "AUTO_RESOLVER" | "PEDIR_INFO" | "ABRIR_CHAMADO",\n'
    '  "urgencia": "BAIXA" | "MEDIA" | "ALTA",\n'
    '  "campos_faltantes": ["..."]\n'
    "}\n"
    "Regras:\n"
    '- **AUTO_RESOLVER**: Perguntas claras sobre regras ou procedimentos descritos nas políticas (Ex: "Posso reembolsar a internet do meu home office?", "Como funciona a política de alimentação em viagens?").\n'
    '- **PEDIR_INFO**: Mensagens vagas ou que faltam informações para identificar o tema ou contexto (Ex: "Preciso de ajuda com uma política", "Tenho uma dúvida geral").\n'
    '- **ABRIR_CHAMADO**: Pedidos de exceção, liberação, aprovação ou acesso especial, ou quando o usuário explicitamente pede para abrir um chamado (Ex: "Quero exceção para trabalhar 5 dias remoto.", "Solicito liberação para anexos externos.", "Por favor, abra um chamado para o RH.").'
    "Analise a mensagem e decida a ação mais apropriada."
)

class TriagemOut(BaseModel):
    decisao: Literal["AUTO_RESOLVER", "PEDIR_INFO", "ABRIR_CHAMADO"]
    urgencia: Literal["BAIXA", "MEDIA", "ALTA"]
    campos_faltantes: List[str] = Field(default_factory=list)

triagem_chain = llm_triagem.with_structured_output(TriagemOut)

def triagem(mensagem: str) -> Dict: 
    saida: TriagemOut = triagem_chain.invoke([
        SystemMessage(content=TRIAGEM_PROMPT),
        HumanMessage(content=mensagem)
    ])
    return saida.model_dump()

# --- 3. PIPELINE DE DADOS E RAG (FAISS) ---
docs = []
pasta_dados = Path("dados/")
pasta_dados.mkdir(exist_ok=True)

for n in pasta_dados.glob("*.pdf"):
    try: 
        loader = PyMuPDFLoader(str(n))
        docs.extend(loader.load())
        print(f"Carregado arquivo {n.name} com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar arquivo {n.name}: {e}")

print(f"Total de páginas carregadas: {len(docs)}")
if not docs:
    raise RuntimeError("Nenhum PDF encontrado na pasta 'dados/'. Adicione os PDFs antes de rodar.")

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", 
    google_api_key=GOOGLE_API_KEY
)

vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold", 
    search_kwargs={"score_threshold": 0.3, "k": 4}
)

prompt_rag = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um Assistente de Políticas Internas (RH/IT) da empresa Carraro Desenvolvimento. "
     "Responda SOMENTE com base no contexto fornecido. "
     "Se não houver base suficiente, responda apenas 'Não sei'."),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])

# --- 4. FORMATADORES E CITAÇÕES ---
def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def extrair_trecho(texto: str, query: str, janela: int = 240) -> str:
    txt = _clean_text(texto)
    termos = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) >= 4]
    pos = -1
    for t in termos:
        pos = txt.lower().find(t)
        if pos != -1: break
    if pos == -1: pos = 0
    ini, fim = max(0, pos - janela//2), min(len(txt), pos + janela//2)
    return txt[ini:fim]

def formatar_citacoes(docs_rel: List, query: str) -> List[Dict]:
    cites, seen = [], set()
    for d in docs_rel:
        src = pathlib.Path(d.metadata.get("source", "")).name
        page = int(d.metadata.get("page", 0)) + 1
        key = (src, page)
        if key in seen:
            continue
        seen.add(key)
        cites.append({"documento": src, "pagina": page, "trecho": extrair_trecho(d.page_content, query)})
    return cites[:3]

def perguntar_politica_RAG(pergunta: str) -> Dict:
    docs_relacionados = retriever.invoke(pergunta)
    if not docs_relacionados:
        return {"answer": "Não sei.", "citacoes": [], "contexto_encontrado": False}

    contexto_formatado = "\n\n".join([d.page_content for d in docs_relacionados])
    chain_input = prompt_rag.format_messages(input=pergunta, context=contexto_formatado)
    answer = llm_triagem.invoke(chain_input)

    raw_content = answer.content
    if isinstance(raw_content, list):
        txt = "".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in raw_content]).strip()
    else:
        txt = (raw_content or "").strip()

    if txt.rstrip(".!?") == "Não sei":
        return {"answer": "Não sei.", "citacoes": [], "contexto_encontrado": False}

    return {
        "answer": txt,
        "citacoes": formatar_citacoes(docs_relacionados, pergunta),
        "contexto_encontrado": True
    }

# --- 5. ORQUESTRAÇÃO COM LANGGRAPH ---
class AgentState(TypedDict, total=False): 
    pergunta: str
    triagem: dict
    resposta: Optional[str]
    citacoes: List[dict]
    rag_sucesso: bool
    acao_final: str

def node_triagem(state: AgentState) -> AgentState: 
    print("  \033[2m↳ [Grafo] Executando triagem...\033[0m")
    return {"triagem": triagem(state["pergunta"])}

def node_auto_resolver(state: AgentState) -> AgentState:
    print("  \033[2m↳ [Grafo] Consultando base RAG (FAISS)...\033[0m")
    resposta_rag = perguntar_politica_RAG(state["pergunta"])
    update: AgentState = {
        "resposta": resposta_rag["answer"], 
        "citacoes": resposta_rag.get("citacoes", []),
        "rag_sucesso": resposta_rag["contexto_encontrado"], 
    }
    if resposta_rag["contexto_encontrado"]: 
        update["acao_final"] = "AUTO_RESOLVER"
    return update

def node_pedir_info(state: AgentState) -> AgentState:
    print("  \033[2m↳ [Grafo] Acionando pedir_info...\033[0m")
    faltantes = state["triagem"].get("campos_faltantes", [])
    detalhe = ", ".join(faltantes) if faltantes else "Tema e contexto específico"
    return {
        "resposta": f"Para avançar, preciso que detalhe: {detalhe}", 
        "citacoes": [], 
        "acao_final": "PEDIR_INFO"
    }

def node_abrir_chamado(state: AgentState) -> AgentState:
    print("  \033[2m↳ [Grafo] Acionando abrir_chamado...\033[0m")
    triag = state["triagem"]
    return {
        "resposta": f"Abrindo chamado com urgência {triag['urgencia']}. Descrição: {state['pergunta'][:140]}", 
        "citacoes": [], 
        "acao_final": "ABRIR_CHAMADO"
    }

KEYWORDS_ABRIR_TICKET = ["aprovação", "exceção", "liberação", "abrir ticket", "abrir chamado", "acesso especial"]

def decidir_pos_triagem(state: AgentState) -> str:
    decisao = state["triagem"]["decisao"]
    if decisao == "AUTO_RESOLVER": return "auto"
    if decisao == "PEDIR_INFO": return "info"
    if decisao == "ABRIR_CHAMADO": return "chamado"

def decidir_pos_auto_resolver(state: AgentState) -> str:
    if state.get("rag_sucesso"):
        return "ok"
    state_da_pergunta = (state["pergunta"] or "").lower()
    if any(k in state_da_pergunta for k in KEYWORDS_ABRIR_TICKET):
        print("  \033[33m↳ [Fallback] RAG sem base -> direcionando para abrir_chamado\033[0m")
        return "chamado"
    print("  \033[33m↳ [Fallback] RAG sem base -> direcionando para pedir_info\033[0m")
    return "info" 

workflow = StateGraph(AgentState)
workflow.add_node("triagem", node_triagem)
workflow.add_node("auto_resolver", node_auto_resolver)
workflow.add_node("pedir_info", node_pedir_info)
workflow.add_node("abrir_chamado", node_abrir_chamado)

workflow.add_edge(START, "triagem")
workflow.add_conditional_edges("triagem", decidir_pos_triagem, {
    "auto": "auto_resolver",
    "info": "pedir_info",
    "chamado": "abrir_chamado"
})
workflow.add_conditional_edges("auto_resolver", decidir_pos_auto_resolver, {
    "info": "pedir_info",
    "chamado": "abrir_chamado",
    "ok": END
})
workflow.add_edge("pedir_info", END)
workflow.add_edge("abrir_chamado", END)

grafo = workflow.compile()

# --- 6. BATERIA DE TESTES ---
def _formatar_bloco(texto: str, largura: int = 76, indent: str = "    ") -> str:
    paragrafos = [p.strip() for p in (texto or "").splitlines() if p.strip()]
    linhas = [textwrap.fill(p, width=largura, initial_indent=indent, subsequent_indent=indent) for p in paragrafos]
    return "\n".join(linhas) if linhas else f"{indent}(sem resposta)"

if __name__ == "__main__":
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    COR_ACAO = {
        "AUTO_RESOLVER": GREEN,
        "PEDIR_INFO": YELLOW,
        "ABRIR_CHAMADO": RED,
    }

    testes = [
        "Posso reembolsar a internet?",
        "Quero mais 5 dias de trabalho remoto. Como faço?",
        "Posso reembolsar cursos ou treinamentos da Alura?",
        "É possível reembolsar certificações do Google Cloud?",
        "Posso obter o Google Gemini de graça?",
        "Preciso de ajuda com uma política.",
        "Quantas capivaras tem no Rio Pinheiros?"
    ]

    print(f"\n{BOLD}{CYAN}════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}               🤖 ASSISTENTE DE SERVICE DESK IA (AGENTIC RAG)               {RESET}")
    print(f"{BOLD}{CYAN}════════════════════════════════════════════════════════════════════════════{RESET}\n")

    def _exibir_resultado(pergunta: str) -> None:
        resposta_final = grafo.invoke({"pergunta": pergunta})
        triag = resposta_final.get("triagem", {})
        decisao = triag.get("decisao", "-")
        urgencia = triag.get("urgencia", "-")
        acao = resposta_final.get("acao_final", "-")
        cor = COR_ACAO.get(acao, RESET)

        print(f"  {BOLD}Roteamento:{RESET} Triagem={decisao}  |  Urgência={urgencia}  |  Ação Final={cor}{BOLD}{acao}{RESET}")
        print(f"  {BOLD}Resposta:{RESET}")
        print(_formatar_bloco(resposta_final.get("resposta", "")))

        if resposta_final.get("citacoes"):
            print(f"  {BOLD}Fontes encontradas:{RESET}")
            for citacao in resposta_final["citacoes"]:
                print(f"    • {CYAN}{citacao['documento']}{RESET} {DIM}(Pág. {citacao['pagina']}){RESET}")
                print(_formatar_bloco(f"\"{citacao['trecho']}...\"", largura=72, indent="      "))

    total = len(testes)
    for idx, msg_test in enumerate(testes, 1):
        print(f"{BOLD}{CYAN}━━━ TESTE {idx}/{total} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"  {BOLD}Pergunta:{RESET} {msg_test}")
        _exibir_resultado(msg_test)
        print()
        if idx < total:
            time.sleep(5)

    # Modo interativo ao final da bateria de testes
    while True:
        try:
            continuar = input(f"{BOLD}{CYAN}Deseja fazer uma pergunta personalizada? (y/n): {RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if continuar == "n":
            print(f"{DIM}Execução encerrada.{RESET}\n")
            break
        if continuar != "y":
            print(f"{YELLOW}Responda apenas 'y' para sim ou 'n' para não.{RESET}")
            continue

        try:
            pergunta_usuario = input(f"\n{BOLD}Digite sua pergunta:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not pergunta_usuario:
            print(f"{YELLOW}Pergunta vazia. Tente novamente.{RESET}\n")
            continue

        print(f"{BOLD}{CYAN}━━━ PERGUNTA PERSONALIZADA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"  {BOLD}Pergunta:{RESET} {pergunta_usuario}")
        _exibir_resultado(pergunta_usuario)
        print()