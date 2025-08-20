from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import paramiko


@dataclass
class SSHConfig:
	host: str
	user: str
	key_file: Optional[str] = None


def send_file(config: SSHConfig, local_path: str, remote_path: str) -> None:
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(
		hostname=config.host,
		username=config.user,
		key_filename=config.key_file,
	)
	sftp = client.open_sftp()
	sftp.put(local_path, remote_path)
	sftp.close()
	client.close()


