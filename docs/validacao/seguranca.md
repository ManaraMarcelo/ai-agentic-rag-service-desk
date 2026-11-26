# Segurança das credenciais

A aplicação utiliza python-dotenv para carregar variáveis de ambiente.

- .env.example: modelo público de configuração.
- .env: arquivo local contendo a credencial real.
- .gitignore: impede o versionamento normal do arquivo .env.
- load_dotenv(): carrega as variáveis.
- os.getenv(): recupera GOOGLE_API_KEY.

A ausência da variável interrompe a inicialização com ValueError.

## Verificação

```powershell
git check-ignore .env
```

Não registrar chaves reais em commits, logs ou documentação.

Caso uma chave seja publicada, revogá-la e gerar outra.
