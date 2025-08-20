from dataclasses import dataclass


@dataclass
class Secret:
	name: str
	value: str
	environment: str



