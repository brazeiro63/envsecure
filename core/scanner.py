from pathlib import Path
import re
from typing import Dict, List


PATTERNS = [
	re.compile(r"os\.getenv\(['\"]([A-Z0-9_]+)['\"]\)"),
	re.compile(r"\$\{?([A-Z0-9_]+)\}?"),
	re.compile(r"ENV\s+([A-Z0-9_]+)"),
]


def scan_paths(base: Path, globs: List[str]) -> Dict[str, List[str]]:
	variables: Dict[str, List[str]] = {}
	for pattern in globs:
		for file in base.rglob(pattern):
			if not file.is_file():
				continue
			content = file.read_text(errors="ignore")
			for regex in PATTERNS:
				for match in regex.findall(content):
					name = match[0] if isinstance(match, tuple) else match
					variables.setdefault(name, []).append(str(file))
	return variables


