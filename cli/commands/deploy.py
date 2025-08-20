from pathlib import Path
import shutil
from typing import Optional, Dict
import click
from rich.console import Console


console = Console()


def _backup_file(target: Path) -> None:
	if target.exists():
		backup = target.with_suffix(target.suffix + ".bak")
		shutil.copy2(target, backup)


@click.command()
@click.argument("environment")
@click.option("--local", is_flag=True, help="Deploy local em arquivo .env")
@click.option("--ssh", "ssh_target", help="user@host:/path")
@click.option("--key", "key_file", help="Arquivo de chave SSH")
@click.option("--validate-first", is_flag=True, default=False)
def deploy_cmd(environment: str, local: bool, ssh_target: Optional[str], key_file: Optional[str], validate_first: bool) -> None:
	"""Realiza deploy seguro dos segredos e arquivos de env."""
	base_dir = Path(".envsecure")
	secrets_path = base_dir / "secrets" / f"secrets.{environment}"
	template_path = base_dir / "templates" / "app.env.safe"
	output_env = base_dir / f".env.{environment}"

	if validate_first:
		from cli.commands.validate import _validate_files
		_validate_files(template_path, secrets_path)

	if not secrets_path.exists():
		raise click.ClickException(f"Segredos não encontrados: {secrets_path}")
	if not template_path.exists():
		raise click.ClickException(f"Template não encontrado: {template_path}")

	# Substituição simples: mantém chaves do template e substitui por valores de secrets
	variables: Dict[str, str] = {}
	for line in secrets_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, value = line.partition("=")
		variables[name.strip()] = value.strip()

	content = []
	for line in template_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, sep, _ = line.partition("=")
		value = variables.get(name.strip(), "")
		content.append(f"{name}{sep}{value}")

	_backup_file(output_env)
	output_env.write_text("\n".join(content) + "\n")
	console.print(f"[green]Gerado {output_env}[/green]")

	if local:
		console.print("[green]Deploy local concluído.[/green]")
		return

	if ssh_target:
		# Deploy via SSH (placeholder minimal); implementação completa em utils/ssh futuramente
		console.print(f"[yellow]Enviar {output_env} para {ssh_target} usando {key_file or 'agent'} (não implementado).[/yellow]")
		return

	console.print("[yellow]Nenhum alvo especificado. Use --local ou --ssh.[/yellow]")


