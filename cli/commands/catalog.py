import json
from pathlib import Path
from typing import Optional, Dict, List
import click
from rich.table import Table
from rich.console import Console


console = Console()


CATALOG_FILE = Path(".envsecure/catalog.json")


def _load_catalog() -> dict:
	if CATALOG_FILE.exists():
		return json.loads(CATALOG_FILE.read_text())
	return {}


def _save_catalog(data: dict) -> None:
	CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)
	CATALOG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


@click.group()
def catalog_cmd() -> None:
	"""Gerencia o catálogo de variáveis."""
	pass


@catalog_cmd.command("add")
@click.argument("name")
@click.option("--category", default="general")
@click.option("--sensitive", is_flag=True, default=False)
@click.option("--required", is_flag=True, default=False)
@click.option("--min-length", type=int)
def add_cmd(name: str, category: str, sensitive: bool, required: bool, min_length: Optional[int]) -> None:
	catalog = _load_catalog()
	catalog[name] = {
		"category": category,
		"sensitive": sensitive,
		"required": required,
		"min_length": min_length,
	}
	_save_catalog(catalog)
	console.print(f"[green]Adicionada {name}[/green]")


@catalog_cmd.command("list")
@click.option("--filter", "filter_expr", help="Ex: sensitive=true")
def list_cmd(filter_expr: Optional[str]) -> None:
	catalog = _load_catalog()
	items = list(catalog.items())
	if filter_expr:
		key, _, value = filter_expr.partition("=")
		if key and _:
			value_norm = value.lower() in {"1", "true", "yes"}
			items = [(k, v) for k, v in items if str(v.get(key)).lower() in {value.lower(), str(value_norm)}]
	
	table = Table(title="Catálogo")
	table.add_column("Name")
	table.add_column("Category")
	table.add_column("Sensitive")
	table.add_column("Required")
	table.add_column("MinLen")
	for name, meta in items:
		table.add_row(
			name,
			str(meta.get("category", "")),
			str(meta.get("sensitive", False)),
			str(meta.get("required", False)),
			str(meta.get("min_length", "")),
		)
	console.print(table)


@catalog_cmd.command("export")
@click.option("--format", "fmt", type=click.Choice(["json", "csv"]), default="json")
@click.option("--output", required=True)
def export_cmd(fmt: str, output: str) -> None:
	catalog = _load_catalog()
	out_path = Path(output)
	if fmt == "json":
		out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
	else:
		lines = ["name;category;sensitive;required;min_length"]
		for name, meta in catalog.items():
			lines.append(
				f"{name};{meta.get('category','')};{meta.get('sensitive',False)};{meta.get('required',False)};{meta.get('min_length','')}"
			)
		out_path.write_text("\n".join(lines))
	console.print(f"[green]Exportado para {out_path}[/green]")


@catalog_cmd.command("clean-invalid")
def clean_invalid_cmd() -> None:
	"""Remove entradas inválidas (nomes fora de ^[A-Z][A-Z0-9_]*$)."""
	import re
	env_re = re.compile(r"^[A-Z][A-Z0-9_]*$")
	catalog = _load_catalog()
	before = len(catalog)
	catalog = {k: v for k, v in catalog.items() if env_re.match(k)}
	_save_catalog(catalog)
	console.print(f"[green]Removidas {before - len(catalog)} entradas inválidas[/green]")


def _auto_category(name: str) -> str:
	lower = name.lower()
	if any(k in lower for k in ["password", "passwd", "secret", "token", "key"]):
		return "secrets"
	if any(k in lower for k in ["db", "database", "postgres", "mysql", "mongo"]):
		return "database"
	if any(k in lower for k in ["url", "endpoint", "host", "port"]):
		return "network"
	return "general"


@catalog_cmd.command("import-scan")
@click.option("--file", "scan_file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--auto-categorize", is_flag=True, default=False, help="Tentar categorizar automaticamente")
def import_scan_cmd(scan_file: str, auto_categorize: bool) -> None:
	"""Importa variáveis a partir de um JSON gerado por 'envsecure scan'."""
	data: Dict[str, List[str]] = json.loads(Path(scan_file).read_text())
	catalog = _load_catalog()
	for name, detected_in in data.items():
		meta = catalog.get(name, {})
		category = meta.get("category") or (_auto_category(name) if auto_categorize else "general")
		sensitive_default = any(k in name.lower() for k in ["password", "passwd", "secret", "token", "key"])
		meta.update(
			{
				"category": category,
				"sensitive": meta.get("sensitive", sensitive_default),
				"required": meta.get("required", True),
				"min_length": meta.get("min_length", None),
				"detected_in": detected_in,
			}
		)
		catalog[name] = meta
	_save_catalog(catalog)
	console.print(f"[green]Importadas {len(data)} variáveis do scan[/green]")


@catalog_cmd.command("generate-template")
@click.option("--output", default=str(Path(".envsecure") / "templates" / "app.env.safe"), show_default=True)
@click.option("--only-required", is_flag=True, default=False, help="Incluir apenas variáveis marcadas como required")
def generate_template_cmd(output: str, only_required: bool) -> None:
	"""Gera o template .env seguro com base no catálogo atual."""
	catalog = _load_catalog()
	lines: List[str] = ["# Template gerado a partir do catálogo", "# Não inclua valores sensíveis aqui"]
	for name in sorted(catalog.keys()):
		if only_required and not catalog.get(name, {}).get("required", True):
			continue
		lines.append(f"{name}=")
	out_path = Path(output)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text("\n".join(lines) + "\n")
	console.print(f"[green]Template gerado em {out_path}[/green]")


@catalog_cmd.command("set-required")
@click.option("--all", "set_all", is_flag=True, default=False, help="Aplicar a todos do catálogo")
@click.option("--name", "name", help="Aplicar a um nome específico")
@click.option("--pattern", "pattern", help="Aplicar a nomes que casem com padrão simples (*, ?)")
@click.option("--required/--optional", default=True, show_default=True)
def set_required_cmd(set_all: bool, name: str | None, pattern: str | None, required: bool) -> None:
	"""Marca variáveis como obrigatórias ou opcionais."""
	import fnmatch
	catalog = _load_catalog()
	changed = 0
	for var_name, meta in catalog.items():
		match = False
		if set_all:
			match = True
		elif name and var_name == name:
			match = True
		elif pattern and fnmatch.fnmatch(var_name, pattern):
			match = True
		if match:
			meta["required"] = required
			changed += 1
	_save_catalog(catalog)
	console.print(f"[green]Atualizadas {changed} entradas (required={required})[/green]")


@catalog_cmd.command("auto-required")
def auto_required_cmd() -> None:
	"""Define 'required' com heurística: secrets/database obrigatórias, demais opcionais."""
	catalog = _load_catalog()
	changed = 0
	for var_name, meta in catalog.items():
		category = meta.get("category", "general")
		is_sensitive = bool(meta.get("sensitive", False))
		req = category in {"secrets", "database"} or is_sensitive
		if meta.get("required") != req:
			meta["required"] = req
			changed += 1
	_save_catalog(catalog)
	console.print(f"[green]Heurística aplicada. Atualizadas {changed} entradas[/green]")


