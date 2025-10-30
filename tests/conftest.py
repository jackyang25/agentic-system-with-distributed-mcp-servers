import pytest
from langsmith import Client


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def langsmith_client():
    return Client()
