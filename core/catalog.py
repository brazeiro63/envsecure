import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any
from models.variable import EnvironmentVariable


CATALOG_FILE = Path(".envsecure/catalog.json")


def load_catalog() -> Dict[str, Any]:
	if CATALOG_FILE.exists():
		return json.loads(CATALOG_FILE.read_text())
	return {}


def save_catalog(catalog: Dict[str, Any]) -> None:
	CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)
	CATALOG_FILE.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))


def add_variable(variable: EnvironmentVariable) -> None:
	catalog = load_catalog()
	catalog[variable.name] = asdict(variable)
	save_catalog(catalog)



