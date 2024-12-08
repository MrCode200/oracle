import typer

app = typer.Typer()

from src.cli.commands import *


def main():
    app()
