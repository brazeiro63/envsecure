from pathlib import Path
from typing import Dict


def render_from_template(template_path: Path, variables: Dict[str, str]) -> str:
	content = []
	for line in template_path.read_text().splitlines():
		if not line.strip() or line.strip().startswith('#'):
			continue
		name, sep, _ = line.partition('=')
		value = variables.get(name.strip(), "")
		content.append(f"{name}{sep}{value}")
	return "\n".join(content) + "\n"


