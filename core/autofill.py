from __future__ import annotations
from pathlib import Path
from typing import Dict, List
import base64
import os
import json


SENSITIVE_HINTS = ("PASSWORD", "SECRET", "TOKEN", "KEY")
PROVIDER_HINTS = (
	"OPENAI",
	"ANTHROPIC",
	"GROQ",
	"DEEPSEEK",
	"EVOLUTION",
	"TELEGRAM",
	"FACEBOOK",
	"INSTAGRAM",
	"GHCR",
)


def _rand_b64(num_bytes: int = 24) -> str:
	return base64.urlsafe_b64encode(os.urandom(num_bytes)).decode().rstrip("=")


def _guess_default(name: str) -> str:
	upper = name.upper()
	# Preferir placeholder para chaves de provedores (LLMs, redes sociais, registries etc.)
	if any(h in upper for h in PROVIDER_HINTS) and any(s in upper for s in ("API_KEY", "TOKEN", "ACCESS_TOKEN")):
		return "your_value_here"
	if upper == "DB_HOST":
		return "localhost"
	if upper == "DB_PORT":
		return "5432"
	if upper == "DB_USER":
		return "app"
	if upper == "DB_PASSWORD":
		return _rand_b64()
	if upper == "DB_NAME":
		return "app"
	if upper == "REDIS_HOST":
		return "localhost"
	if upper == "REDIS_PORT":
		return "6379"
	if upper == "REDIS_DB":
		return "0"
	if upper.endswith("_PORT"):
		return "8000"
	if upper in {"JWT_REFRESH_TOKEN_EXPIRE_DAYS"}:
		return "7"
	if upper in {"JWT_ACCESS_TOKEN_EXPIRE_MINUTES"}:
		return "15"
	if upper in {"EMAIL_TOKEN_EXPIRE_HOURS"}:
		return "24"
	if any(h in upper for h in SENSITIVE_HINTS):
		return _rand_b64(32)
	return ""


def generate_dev_defaults(template_path: Path, catalog_path: Path) -> Dict[str, str]:
	# Carrega chaves do template
	keys: List[str] = []
	for line in template_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, _ = line.partition('=')
		keys.append(name.strip())

	# Carrega required do catálogo, se existir
	catalog_required: Dict[str, bool] = {}
	if catalog_path.exists():
		catalog = json.loads(catalog_path.read_text())
		for name, meta in catalog.items():
			catalog_required[name] = bool(meta.get("required", True))

	values: Dict[str, str] = {}
	for name in keys:
		# apenas chaves marcadas como required (quando catálogo existe)
		if catalog_required and not catalog_required.get(name, True):
			continue
		values[name] = _guess_default(name)
	return values


