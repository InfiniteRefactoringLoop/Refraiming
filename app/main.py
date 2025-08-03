from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from PIL import Image
from io import BytesIO

app = FastAPI()

MAX_DIMENSION = 2048

class EditRequest(BaseModel):
    prompt: str

class SessionState:
    """In-memory storage for a single editing session."""
    def __init__(self) -> None:
        self.original: bytes | None = None
        self.history: List[bytes] = []
        self.cost_eur: float = 0.0

state = SessionState()

def _downscale_image(data: bytes) -> bytes:
    """Downscale image so longest side equals MAX_DIMENSION using LANCZOS."""
    with Image.open(BytesIO(data)) as img:
        width, height = img.size
        if max(width, height) <= MAX_DIMENSION:
            buf = BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        if width >= height:
            new_w = MAX_DIMENSION
            new_h = int(height * MAX_DIMENSION / width)
        else:
            new_h = MAX_DIMENSION
            new_w = int(width * MAX_DIMENSION / height)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        buf = BytesIO()
        resized.save(buf, format="PNG")
        return buf.getvalue()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    data = await file.read()
    state.original = data
    processed = _downscale_image(data)
    state.history = [processed]
    state.cost_eur = 0.0
    with Image.open(BytesIO(processed)) as img:
        width, height = img.size
    return {"width": width, "height": height, "cost_eur": state.cost_eur}

@app.post("/edit")
async def edit_image(request: EditRequest):
    if not state.history:
        raise HTTPException(status_code=400, detail="No image uploaded")
    # Placeholder for call to Flux 1 Kontext API.
    # For now, we simply re-use the latest image and add a fixed cost.
    latest = state.history[-1]
    state.history.append(latest)
    state.cost_eur += 0.05
    return {"cost_eur": state.cost_eur, "prompt": request.prompt}

@app.post("/undo")
async def undo_last_edit():
    if len(state.history) <= 1:
        raise HTTPException(status_code=400, detail="Nothing to undo")
    state.history.pop()
    return {"cost_eur": state.cost_eur, "edits_remaining": len(state.history)}

@app.post("/finalize")
async def finalize_image():
    if not state.history:
        raise HTTPException(status_code=400, detail="No image uploaded")
    # Placeholder for Real-ESRGAN upscale and JPEG export.
    state.cost_eur += 0.01
    return JSONResponse({"message": "Upscale placeholder", "cost_eur": state.cost_eur})
