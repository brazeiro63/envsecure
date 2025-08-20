from pathlib import Path
from typing import Optional, List, Dict, Set
import re
import click
from rich.console import Console
import json


console = Console()


PLACEHOLDER_RE = re.compile(r"your_.*_here|placeholder|changeme", flags=re.I)
PROVIDER_PLACEHOLDER_RE = re.compile(r"your_value_here", flags=re.I)


def _validate_files(template_path: Path, secrets_path: Path) -> None:
	if not template_path.exists():
		raise click.ClickException("Template não encontrado")
	if not secrets_path.exists():
		raise click.ClickException("Segredos não encontrados")

	# Constrói lista de chaves do template
	required_keys: List[str] = []
	for line in template_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, default_value = line.partition('=')
		required_keys.append(name.strip())
		if PLACEHOLDER_RE.search(default_value):
			raise click.ClickException(f"Template contém placeholder fraco para {name}")

	# Lê segredos
	secrets: Dict[str, str] = {}
	for line in secrets_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, value = line.partition('=')
		secrets[name.strip()] = value.strip()

	# Presença
	missing = [k for k in required_keys if k not in secrets or not secrets[k]]
	if missing:
		raise click.ClickException(f"Segredos obrigatórios ausentes: {', '.join(missing)}")

	# Força mínima (ignora placeholders de provedores)
	weak = []
	for k, v in secrets.items():
		if k.endswith("SECRET") or k.endswith("KEY"):
			if len(v) < 16 and not PROVIDER_PLACEHOLDER_RE.search(v):
				weak.append(k)
	if weak:
		raise click.ClickException(f"Valores fracos detectados: {', '.join(weak)} (>=16 chars)")


@click.command()
@click.option("--environment", "environment", help="Ambiente alvo")
@click.option("--check-strength", is_flag=True, default=False)
@click.option("--audit-secrets", is_flag=True, default=False)
@click.option("--env", "env_short", help="Alias para --environment")
@click.option("--audit", "audit_short", is_flag=True, help="Alias para --audit-secrets")
@click.option("--report", type=click.Path(dir_okay=False))
@click.option("--strict/--no-strict", default=False, show_default=True, help="Modo estrito: todas as chaves do template são obrigatórias")
def validate_cmd(environment: Optional[str], check_strength: bool, audit_secrets: bool, env_short: Optional[str], audit_short: bool, report: Optional[str], strict: bool) -> None:
	"""Valida templates e segredos."""
	env = environment or env_short or "dev"
	base_dir = Path(".envsecure")
	secrets_path = base_dir / "secrets" / f"secrets.{env}"
	template_path = base_dir / "templates" / "app.env.safe"

	if strict:
		try:
			_validate_files(template_path, secrets_path)
			console.print("[green]Validação básica OK[/green]")
		except click.ClickException as e:
			console.print(f"[red]{e}[/red]")
			raise
	else:
		# Validação baseada no catálogo: só exige variáveis marcadas como required
		if not template_path.exists() or not secrets_path.exists():
			raise click.ClickException("Template ou segredos não encontrados")
		catalog_path = base_dir / "catalog.json"
		catalog: Dict[str, Dict] = {}
		if catalog_path.exists():
			catalog = json.loads(catalog_path.read_text())
		template_keys: List[str] = []
		for line in template_path.read_text().splitlines():
			if not line.strip() or line.strip().startswith('#'):
				continue
			name, _, _ = line.partition('=')
			template_keys.append(name.strip())
		secrets: Dict[str, str] = {}
		for line in secrets_path.read_text().splitlines():
			if not line.strip() or line.strip().startswith('#'):
				continue
			name, _, value = line.partition('=')
			secrets[name.strip()] = value.strip()
		required_names: Set[str] = set(
			name for name, meta in catalog.items() if meta.get("required", True)
		)
		# Considera apenas chaves presentes no template
		required_names &= set(template_keys)
		missing = [k for k in sorted(required_names) if not secrets.get(k)]
		if missing:
			raise click.ClickException("Segredos obrigatórios ausentes: " + ", ".join(missing))
		console.print("[green]Validação básica (não estrita) OK[/green]")

	if check_strength or audit_secrets or audit_short:
		weak: List[str] = []
		for line in secrets_path.read_text().splitlines():
			if not line.strip() or line.strip().startswith('#'):
				continue
			name, _, value = line.partition('=')
			if len(value.strip()) < 16:
				weak.append(name)
		if weak:
			msg = f"Fracos (<16 chars): {', '.join(weak)}"
			if report:
				Path(report).write_text(msg)
			console.print(f"[yellow]{msg}[/yellow]")
		else:
			console.print("[green]Força mínima OK[/green]")


