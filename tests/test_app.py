from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import (
    EDIT_COST_EUR,
    FINALIZE_COST_EUR,
    MAX_DIMENSION,
    _downscale_image,
    app,
    state,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Ensure each test starts with a clean session state."""
    state.original = None
    state.history = []
    state.cost_eur = 0.0
    yield
    state.original = None
    state.history = []
    state.cost_eur = 0.0


def create_image(size: tuple[int, int]) -> BytesIO:
    img = Image.new("RGB", size, color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_downscale_image_no_resize() -> None:
    buf = create_image((100, 50))
    data = _downscale_image(buf.getvalue())
    with Image.open(BytesIO(data)) as img:
        assert img.size == (100, 50)


def test_downscale_image_resizes() -> None:
    buf = create_image((4096, 2048))
    data = _downscale_image(buf.getvalue())
    with Image.open(BytesIO(data)) as img:
        assert max(img.size) == MAX_DIMENSION


def test_upload_image() -> None:
    buf = create_image((100, 100))
    files = {"file": ("test.png", buf, "image/png")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["width"] == 100
    assert data["height"] == 100


def test_edit_requires_upload() -> None:
    response = client.post("/edit", json={"prompt": "test"})
    assert response.status_code == 400
    assert response.json()["detail"] == "No image uploaded"


def test_edit_updates_cost() -> None:
    buf = create_image((100, 100))
    files = {"file": ("test.png", buf, "image/png")}
    client.post("/upload", files=files)
    cost_before = state.cost_eur
    response = client.post("/edit", json={"prompt": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["cost_eur"] == pytest.approx(cost_before + EDIT_COST_EUR)


def test_undo_requires_history() -> None:
    response = client.post("/undo")
    assert response.status_code == 400
    assert response.json()["detail"] == "Nothing to undo"


def test_undo_reverts_edit() -> None:
    buf = create_image((100, 100))
    files = {"file": ("test.png", buf, "image/png")}
    client.post("/upload", files=files)
    client.post("/edit", json={"prompt": "hello"})
    response = client.post("/undo")
    assert response.status_code == 200
    data = response.json()
    assert data["edits_remaining"] == 1


def test_finalize_requires_upload() -> None:
    response = client.post("/finalize")
    assert response.status_code == 400
    assert response.json()["detail"] == "No image uploaded"


def test_finalize_updates_cost() -> None:
    buf = create_image((100, 100))
    files = {"file": ("test.png", buf, "image/png")}
    client.post("/upload", files=files)
    cost_before = state.cost_eur
    response = client.post("/finalize")
    assert response.status_code == 200
    data = response.json()
    assert data["cost_eur"] == pytest.approx(cost_before + FINALIZE_COST_EUR)
