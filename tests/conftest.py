"""Test fixtures."""

from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture
def anyio_backend():
    return "asyncio"


def load_environment_variables() -> None:
    """Load environment variables from .env file."""
    creds_path: Path = Path(__file__).parent.parent.joinpath(".env")
    load_dotenv(dotenv_path=creds_path)
