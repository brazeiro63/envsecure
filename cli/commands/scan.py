from pathlib import Path
import re
import json
import os
import fnmatch
from typing import Set, Dict, List, Optional
import click
from rich.console import Console


console = Console()


PATTERNS = [
	re.compile(r"os\.getenv\(['\"]([A-Z0-9_]+)['\"]\)"),
	re.compile(r"\$\{?([A-Z0-9_]+)\}?"),
	re.compile(r"ENV\s+([A-Z][A-Z0-9_]+)"),
]

ENV_VAR_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _scan_file(file_path: Path) -> Set[str]:
	content = file_path.read_text(errors="ignore")
	found: Set[str] = set()
	for pattern in PATTERNS:
		for match in pattern.findall(content):
			if isinstance(match, tuple):
				match = match[0]
			name = str(match)
			if ENV_VAR_RE.match(name):
				found.add(name)
	return found


@click.command()
@click.option("--path", "scan_path", default=".", show_default=True, type=click.Path(exists=True, file_okay=False))
@click.option("--output", type=click.Path(dir_okay=False), help="Arquivo de saída (csv/json)")
@click.option("--pattern", default="*.py,*.yml,*.yaml,*.json,Dockerfile", show_default=True)
@click.option(
	"--exclude",
	default=".venv,venv,.git,__pycache__,node_modules,.mypy_cache,.pytest_cache,.tox,dist,build,.envsecure",
	show_default=True,
	help="Pastas a serem ignoradas (lista separada por vírgulas)",
)
def scan_cmd(scan_path: str, output: Optional[str], pattern: str, exclude: str) -> None:
	"""Escaneia o código e detecta variáveis de ambiente."""
	path = Path(scan_path)
	extensions = [p.strip() for p in pattern.split(",") if p.strip()]
	excluded_dirs = {e.strip() for e in exclude.split(",") if e.strip()}
	variables: Dict[str, List[str]] = {}
	# Caminhada segura evitando entrar em diretórios excluídos
	for root, dirs, files in os.walk(path, topdown=True):
		# Prune de diretórios excluídos
		dirs[:] = [d for d in dirs if d not in excluded_dirs]
		for fname in files:
			if not any(fnmatch.fnmatch(fname, pat) for pat in extensions):
				continue
			file_path = Path(root) / fname
			try:
				if file_path.is_symlink():
					continue
				for var in _scan_file(file_path):
					variables.setdefault(var, []).append(str(file_path))
			except OSError:
				# Ignora arquivos inacessíveis
				continue

	console.print(f"[green]Encontradas {len(variables)} variáveis[/green]")
	if output:
		out_path = Path(output)
		if out_path.suffix.lower() == ".json":
			out_path.write_text(json.dumps(variables, indent=2, ensure_ascii=False))
		else:
			# CSV simples: VAR;path1,path2
			lines = ["name;detected_in"]
			for name, files in sorted(variables.items()):
				lines.append(f"{name};{','.join(files)}")
			out_path.write_text("\n".join(lines))
	else:
		console.print(variables)


