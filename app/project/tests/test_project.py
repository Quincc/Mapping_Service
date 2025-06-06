# app/project/tests/test_project.py
import os, asyncio, uuid, pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.project.db import init_models, engine

@pytest.fixture(scope="session", autouse=True)
def setup_db(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    os.environ["DB_PATH"] = str(db_file)     # переопределяем перед init_models
    asyncio.run(init_models())
    yield
    # ничего не чистим — tmp-директория удалится сама

@pytest.fixture
def client():
    return TestClient(create_app())

def test_create_project(client):
    rnd_name = f"Demo-{uuid.uuid4().hex[:6]}"
    r = client.post("/projects/", json={"name": rnd_name})
    assert r.status_code == 201
    assert r.json()["name"] == rnd_name
