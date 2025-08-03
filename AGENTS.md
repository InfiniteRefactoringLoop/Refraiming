# Implementation Plan for AI-Based Photo Editing Tool

## Goal
Develop a local web application that allows photographers to perform high-quality photo edits using natural language prompts. The app should offload compute-heavy tasks to external APIs so it runs on typical laptops without dedicated GPUs.

## 1. Research & Model Selection

### 1.1 Downscaling
- **Options**
  - **Pillow (LANCZOS filter)** – open-source Python library, zero cost, high quality, runs on CPU.
  - **OpenCV resize** – fast C++ bindings, similar quality, larger dependency.
  - **Cloudinary/Imgix APIs** – external services, charge per image, require account.
- **Decision**: Use **Pillow** locally with the LANCZOS filter. It is cost-free, easy to install, and good enough for high-resolution photos. External services add cost and require network round-trips without quality benefits.
- **Resolution**: Downscale so that the longest side is **2048 px**, the upper limit published for Flux 1 Kontext. Maintain aspect ratio.

### 1.2 Image Editing
- **Model**: **Flux 1 Kontext** by Black Forest Labs. Supports prompt-based editing and compositional changes.
- **Provider**: Use the official Black Forest Labs API (or Replicate as a fallback) to avoid GPU requirements locally.
- **Estimated cost**: ~€0.04–€0.06 per 2048² edit depending on provider pricing. The API returns compute time that can be converted to cost for monitoring.

### 1.3 Upscaling
- **Options**
  - **Real‑ESRGAN** (4×) – open-source, high fidelity, available via Replicate/HuggingFace; moderate cost.
  - **Stable Diffusion Upscaler** – heavier model, higher cost, slower; sometimes introduces artifacts.
  - **Commercial tools (Topaz Gigapixel)** – high quality but closed-source and expensive per license.
- **Decision**: Use **Real‑ESRGAN** through an API provider. It balances quality and cost (<€0.01 for a 2048² → 8192² upscale) and has predictable behaviour.

## 2. System Architecture
- **Backend**: Python **FastAPI** server.
- **Frontend**: Minimal React (via Vite) + TailwindCSS for a clean, single-page interface.
- **Image Processing**: `Pillow` for local downscaling, format conversion, and JPEG export.
- **Storage**: Keep the original image and a stack of intermediate edits in memory or temporary files. Stack depth limited to enable single-level undo.
- **Secrets**: Store API keys in a `.env` file loaded with `python-dotenv`. `.env` added to `.gitignore` to prevent commits.

## 3. User Workflow Implementation
1. **Upload Image**
   - Accept high-resolution JPG/PNG.
   - Save original resolution and file; downscale to 2048px max using Pillow.
   - Initialize cost counter to zero.
2. **Preview & Prompt Input**
   - Display downscaled image and text field for editing instructions.
3. **Edit via Flux 1 Kontext**
   - Send current image and prompt to the external API.
   - On response, append new image to history stack, update cost (based on API response), and show before/after side-by-side.
4. **Undo**
   - Pop the latest image from history stack and update preview.
5. **Finalize & Export**
   - Invoke Real‑ESRGAN API to upscale the latest image back to original dimensions.
   - Convert to JPEG and provide download link.
   - Display total cost incurred for the session.

## 4. Documentation Outline
- **Setup (macOS/Linux/WSL2)**
  - Install Python, Node.js, and Git.
  - For Windows: enable WSL2, install Ubuntu, and follow Linux steps.
- **Install Dependencies**
  - `python -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
  - `npm install` in the `frontend` directory.
- **API Accounts**
  - Create accounts with Black Forest Labs (Flux) and Replicate.
  - Obtain API tokens and place them in `.env` as `FLUX_API_KEY` and `REPLICATE_API_KEY`.
- **Running Locally**
  - `uvicorn app.main:app --reload` for backend.
  - `npm run dev` for frontend, which proxies API requests to FastAPI.
- **Secret Handling**
  - Never commit `.env` or any keys.
  - Optionally use a secrets manager (1Password, Bitwarden) and environment variables for deployment.

## 5. Stretch Goal – Cost Monitoring
- Persist total cost per image in backend session.
- Fetch pricing info from provider metadata (compute time × rate) and accumulate.
- Expose cost to frontend via API; reset when a new image is uploaded.

## 6. Future Enhancements (Out of Scope for Now)
- Multiple undo steps and full edit history.
- Alternative models or advanced parameter controls.
- Collaborative or cloud-hosted versions.

