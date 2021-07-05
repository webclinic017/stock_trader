"""Test cases for the __main__ module."""
import pytest
from typer.testing import CliRunner

from stock_trader import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.command_line, ["stock_trader"])
    assert result.exit_code == 0
