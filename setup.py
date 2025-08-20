from setuptools import setup, find_packages


setup(
	name="envsecure-manager",
	version="0.1.0",
	description="EnvSecure Manager: CLI para gerenciamento seguro de variáveis de ambiente e segredos",
	packages=find_packages(exclude=("tests", "templates")),
	python_requires=">=3.8",
	install_requires=[
		"click>=8.0.0",
		"cryptography>=3.0.0",
		"paramiko>=2.7.0",
		"pydantic>=1.8.0,<3.0.0",
		"rich>=10.0.0",
		"PyYAML>=5.4.0",
		"python-dotenv>=0.19.0",
		"Jinja2>=3.0.0",
	],
	entry_points={
		"console_scripts": [
			"envsecure=cli.main:cli",
		]
	},
)



