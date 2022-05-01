import os
from sanic import Sanic
from booktracker.server import create_app
import pytest


@pytest.fixture
def app():
    os.environ["SANIC_LOCAL"] = "True"
    app = create_app(
        module_names=[
            "booktracker.blueprints.view",
            "booktracker.middleware.request_context",
            "booktracker.middleware.redirect",
        ]
    )
    return app


def test_root(app: Sanic):
    _, response = app.test_client.get("/api/v1")

    assert response.status == 200
