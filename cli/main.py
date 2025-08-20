#!/usr/bin/env python3
"""
EnvSecure Manager - CLI principal

Copyright (C) 2024  EnvSecure Manager Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import click
from rich.console import Console


console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="envsecure-manager")
def cli() -> None:
	"""EnvSecure Manager: gerenciamento seguro de variáveis de ambiente e segredos."""
	pass


def _register_commands() -> None:
	# Imports locais para evitar custo de import quando apenas --help é utilizado
	from cli.commands.init import init_cmd
	from cli.commands.scan import scan_cmd
	from cli.commands.catalog import catalog_cmd
	from cli.commands.configure import configure_cmd
	from cli.commands.deploy import deploy_cmd
	from cli.commands.validate import validate_cmd
	from cli.commands.generate_keys import generate_keys_cmd

	cli.add_command(init_cmd, name="init")
	cli.add_command(scan_cmd, name="scan")
	cli.add_command(catalog_cmd, name="catalog")
	cli.add_command(configure_cmd, name="configure")
	cli.add_command(deploy_cmd, name="deploy")
	cli.add_command(validate_cmd, name="validate")
	cli.add_command(generate_keys_cmd, name="generate-keys")


_register_commands()


