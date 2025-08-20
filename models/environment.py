from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DeployTarget:
	type: str  # 'local', 'ssh', 'docker', 'k8s'
	host: Optional[str] = None
	user: Optional[str] = None
	key_file: Optional[str] = None
	target_path: str = ".env"


@dataclass
class Environment:
	name: str
	description: str = ""
	variables: Optional[Dict[str, str]] = None
	secrets: Optional[Dict[str, str]] = None
	deploy_target: Optional[DeployTarget] = None


