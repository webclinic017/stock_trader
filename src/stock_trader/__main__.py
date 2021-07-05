"""Command-line interface."""
from ast import Str
import typer

command_line = typer.Typer()


@command_line.command()
@command_line.version_option()
def main() -> None:
    """Stock Trader."""


if __name__ == "__main__":
    main(prog_name="stock_trader")  # pragma: no cover
