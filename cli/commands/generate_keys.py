import os
import secrets as pysecrets
import base64
import click
from rich.console import Console


console = Console()


@click.command()
@click.option("--bytes", "num_bytes", type=int, default=32, show_default=True)
@click.option("--format", "fmt", type=click.Choice(["hex", "base64"]), default="base64")
def generate_keys_cmd(num_bytes: int, fmt: str) -> None:
	"""Gera chaves seguras aleatórias."""
	data = pysecrets.token_bytes(num_bytes)
	if fmt == "hex":
		value = data.hex()
	else:
		value = base64.urlsafe_b64encode(data).decode().rstrip("=")
	console.print(value)


