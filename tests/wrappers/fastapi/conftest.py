from main import app
import pytest
from starlette.testclient import TestClient


@pytest.fixture(autouse=True)
def test_app():
    client = TestClient(app)
    yield client  # testing happens here