# Configuração do ambiente

O projeto utiliza Python 3.10 ou superior.

## Preparação no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencher GOOGLE_API_KEY no arquivo .env antes da execução.

## Execução

```powershell
python main.py
```

Executar a partir da raiz do projeto para localizar a pasta dados/.
