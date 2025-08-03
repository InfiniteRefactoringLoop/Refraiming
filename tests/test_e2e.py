from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.main import EDIT_COST_EUR, FINALIZE_COST_EUR, app, state

client = TestClient(app)


def create_image(size):
    img = Image.new("RGB", size, color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_full_workflow():
    state.original = None
    state.history = []
    state.cost_eur = 0.0

    buf = create_image((3000, 1500))
    files = {"file": ("big.png", buf, "image/png")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["width"] == 2048
    assert data["height"] == 1024

    response = client.post("/edit", json={"prompt": "add sun"})
    assert response.status_code == 200
    assert response.json()["cost_eur"] == pytest.approx(EDIT_COST_EUR)

    response = client.post("/undo")
    assert response.status_code == 200
    assert response.json()["edits_remaining"] == 1

    response = client.post("/finalize")
    assert response.status_code == 200
    expected_total = EDIT_COST_EUR + FINALIZE_COST_EUR
    assert response.json()["cost_eur"] == pytest.approx(expected_total)
