"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Stock Trader."""


if __name__ == "__main__":
    main(prog_name="stock_trader")  # pragma: no cover
