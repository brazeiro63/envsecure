from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console


console = Console()


@click.command()
@click.argument("environment")
@click.option("--wizard", "wizard", is_flag=True, help="Assistente interativo")
@click.option("--from-template", is_flag=True, help="Gerar a partir de template .safe")
@click.option("--secrets-file", type=click.Path(dir_okay=False))
@click.option("--autofill-dev", is_flag=True, help="Preencher automaticamente valores de desenvolvimento para chaves required")
def configure_cmd(environment: str, wizard: bool, from_template: bool, secrets_file: Optional[str], autofill_dev: bool) -> None:
	"""Configura variáveis e segredos para um ambiente."""
	base_dir = Path(".envsecure")
	secrets_dir = base_dir / "secrets"
	secrets_dir.mkdir(parents=True, exist_ok=True)
	secrets_path = secrets_file and Path(secrets_file) or (secrets_dir / f"secrets.{environment}")

	if wizard:
		console.print("[cyan]Iniciando wizard de segredos. Pressione Enter para manter vazio.[/cyan]")
		entries: List[str] = []
		while True:
			name = click.prompt("Nome da variável (vazio para sair)", default="", show_default=False)
			if not name:
				break
			value = click.prompt(f"Valor para {name}", hide_input=True, default="", show_default=False)
			entries.append(f"{name}={value}")
		secrets_path.write_text("\n".join(entries) + ("\n" if entries else ""))
		console.print(f"[green]Arquivo de segredos salvo em {secrets_path}[/green]")
		return

	if from_template:
		template_path = base_dir / "templates" / "app.env.safe"
		if not template_path.exists():
			raise click.ClickException("Template .env.safe não encontrado. Rode 'envsecure init' primeiro.")
		# Copia placeholders para um arquivo de segredos para edição
		content = template_path.read_text()
		lines = []
		for line in content.splitlines():
			if line.strip().startswith("#") or not line.strip():
				continue
			name, _, _ = line.partition("=")
			lines.append(f"{name}=\n")
		secrets_path.write_text("\n".join(lines))
		console.print(f"[green]Gerado {secrets_path} a partir do template[/green]")
		if autofill_dev:
			from core.autofill import generate_dev_defaults
			catalog_path = base_dir / "catalog.json"
			values = generate_dev_defaults(template_path, catalog_path)
			existing = secrets_path.read_text().splitlines()
			merged: dict[str, str] = {}
			for line in existing:
				if not line.strip() or line.strip().startswith('#'):
					continue
				k, _, v = line.partition('=')
				merged[k.strip()] = v
			for k, v in values.items():
				if k not in merged or not merged[k]:
					merged[k] = v
			secrets_path.write_text("\n".join(f"{k}={v}" for k, v in merged.items()) + "\n")
			console.print(f"[green]Preenchidos valores de desenvolvimento em {secrets_path}[/green]")
		return

	if secrets_file:
		console.print(f"[green]Arquivo de segredos definido: {secrets_path}[/green]")
	else:
		console.print("[yellow]Nenhuma ação realizada. Use --wizard ou --from-template.[/yellow]")


