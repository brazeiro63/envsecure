from __future__ import annotations
from pathlib import Path
import shutil
import os


def ensure_mode(path: Path, mode: int = 0o600) -> None:
	try:
		os.chmod(path, mode)
	except Exception:
		pass


def atomic_write(path: Path, content: str) -> None:
	tmp = path.with_suffix(path.suffix + ".tmp")
	tmp.write_text(content)
	shutil.move(tmp, path)
	ensure_mode(path)



