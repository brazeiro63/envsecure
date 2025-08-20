import os
from pathlib import Path
import click
from rich.console import Console


console = Console()


@click.command()
@click.argument("project_name")
@click.option("--envs", default="dev,prod", show_default=True, help="Lista de ambientes separados por vírgula")
def init_cmd(project_name: str, envs: str) -> None:
	"""Inicializa estrutura segura de gerenciamento de env/segredos em .envsecure/."""
	base_dir = Path(".envsecure")
	templates_dir = base_dir / "templates"
	secrets_dir = base_dir / "secrets"
	scripts_dir = base_dir / "deploy_scripts"

	for d in [base_dir, templates_dir, secrets_dir, scripts_dir]:
		d.mkdir(parents=True, exist_ok=True)

	# .gitignore seguro
	gitignore_path = base_dir / ".gitignore"
	if not gitignore_path.exists():
		gitignore_path.write_text("secrets.*\n*.env\n*.env.*\n.tmp/\n")

	# Template base
	(templates_dir / "app.env.safe").write_text(
		"# Template seguro sem valores sensíveis\n# EXAMPLE_VAR=your_value_here\n"
	)

	# Cria arquivos de secrets vazios por ambiente
	env_list = [e.strip() for e in envs.split(",") if e.strip()]
	for env in env_list:
		(secrets_dir / f"secrets.{env}").write_text(f"# valores sensíveis para {env}\n")

	console.print(f"[green]Projeto '{project_name}' inicializado em {base_dir}[/green]")


