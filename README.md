# EnvSecure Manager

Ferramenta CLI para gerenciamento seguro de variáveis de ambiente e segredos em projetos Python.

## Instalação (dev)

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -e .
```

## Uso rápido

```bash
envsecure --help
envsecure init minha-app --envs dev,prod
envsecure scan --path . --output catalog.json
envsecure catalog list
envsecure configure dev --wizard
envsecure validate --env dev --audit --report security-audit.txt
```

## Estrutura

- `cli/`: comandos CLI
- `core/`: regras de negócio (scan, catalog, templates, secrets, validator, deploy)
- `models/`: modelos de dados
- `utils/`: utilitários (crypto, ssh, filesystem)
- `templates/`: templates de projeto/deploy/config
- `tests/`: testes unitários

## Segurança
- Separação de templates `.safe` e arquivos `secrets.*` (no `.gitignore`)
- Validações de presença/força e placeholders
- Deploy local/SSH com backup e permissões restritivas

## Requisitos
- Python 3.8+

## Licença
MIT


