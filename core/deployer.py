from pathlib import Path
import shutil
from typing import Optional
from utils.filesystem import ensure_mode


def backup_file(path: Path) -> Optional[Path]:
	if not path.exists():
		return None
	backup = path.with_suffix(path.suffix + ".bak")
	shutil.copy2(path, backup)
	return backup


def write_env_file(path: Path, content: str) -> None:
	path.write_text(content)
	ensure_mode(path)


