# EnvSecure Manager

Ferramenta CLI para gerenciamento seguro de variáveis de ambiente e segredos em projetos Python.

## Instalação (dev)

```bash
python -m venv .venv

# Ative o ambiente virtual conforme seu sistema operacional:
# Windows (PowerShell):
. .venv/Scripts/Activate.ps1
# Linux/macOS (bash/zsh):
source .venv/bin/activate

# Atualize o pip para melhor performance:
python -m pip install --upgrade pip

# Instale as dependências e trate possíveis erros:
python -m pip install -e . || { echo "Falha ao instalar dependências"; exit 1; }
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

Este projeto está licenciado sob a GNU General Public License v3.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

O EnvSecure Manager é software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation, seja a versão 3 da Licença, ou (a seu critério) qualquer versão posterior.

Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de COMERCIABILIDADE ou ADEQUAÇÃO A UM DETERMINADO FIM. Veja a GNU General Public License para mais detalhes.

Você deve ter recebido uma cópia da GNU General Public License junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.


