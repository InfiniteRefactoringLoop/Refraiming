# Refraiming

An AI-based tool to edit high-quality photographs using text descriptions.

Reframing photos with **AI** = Refr**ai**ming

## Setup (macOS/Linux/WSL2)
1. Install Python, Node.js, and [uv](https://github.com/astral-sh/uv).
2. Create a virtual environment and install backend dependencies with uv:
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync --all-extras
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## API Accounts
Create accounts with Black Forest Labs (Flux) and Replicate. Place your API tokens in a `.env` file:
```
FLUX_API_KEY=your_flux_key
REPLICATE_API_KEY=your_replicate_key
```

## Running Locally
Start the FastAPI backend:
```bash
uv run uvicorn app.main:app --reload
```
Start the React frontend:
```bash
cd frontend
npm run dev
```
The frontend proxy is configured to forward `/api` requests to the backend.

## Formatting and Type Checking
Run the provided tools before committing changes:
```bash
uv run isort .
uv run black .
uv run mypy .
uv run pytest
```

## Secret Handling
Never commit the `.env` file or any keys. Use `.env.example` as a template for local development.
