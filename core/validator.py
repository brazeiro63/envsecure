from pathlib import Path
import re


PLACEHOLDER_RE = re.compile(r"your_.*_here|placeholder|changeme", flags=re.I)


def validate_template_and_secrets(template_path: Path, secrets_path: Path) -> None:
	if not template_path.exists():
		raise ValueError("Template não encontrado")
	if not secrets_path.exists():
		raise ValueError("Segredos não encontrados")

	required: list[str] = []
	for line in template_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, default_value = line.partition('=')
		required.append(name.strip())
		if PLACEHOLDER_RE.search(default_value):
			raise ValueError(f"Template contém placeholder fraco para {name}")

	secrets: dict[str, str] = {}
	for line in secrets_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, _, value = line.partition('=')
		secrets[name.strip()] = value.strip()

	missing = [k for k in required if k not in secrets or not secrets[k]]
	if missing:
		raise ValueError("Segredos obrigatórios ausentes: " + ", ".join(missing))



