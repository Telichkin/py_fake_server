import pytest

from py_fake_server import FakeServer


@pytest.fixture(scope="session")
def server() -> FakeServer:
    server = FakeServer(host="localhost", port=8081)
    server.start()
    yield server
    server.stop()


@pytest.fixture(autouse=True)
def clear_server(server: FakeServer):
    server.clear()
    yield
    server.clear()
