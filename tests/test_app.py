from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def test_upload_image() -> None:
    img = Image.new("RGB", (100, 100), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    files = {"file": ("test.png", buf, "image/png")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["width"] == 100
    assert data["height"] == 100
