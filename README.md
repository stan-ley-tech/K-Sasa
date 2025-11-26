# K‑Sasa

K‑Sasa is a Kiswahili‑first AI assistant for schools and public services.
It combines a local Kiswahili language model with an English–Kiswahili translation and retrieval pipeline to support use cases like:

- Education: answering curriculum questions, explaining concepts in Kiswahili.
- Health: helping explain health materials and clinic information.
- Governance: helping citizens understand forms, procedures, and public information.

The goal is to provide a **privacy‑aware, locally deployable** assistant that works well in Kiswahili, with a simple web UI and an API backend.

---

## Project structure

```text
backend/         # Backend API, model loading, RAG, agents
  app/           # Application code (agents, orchestration, endpoints)
  kiswahili-model-local/  # Local Kiswahili model weights (model.pt)
  requirements.txt

frontend/        # React/Vite frontend for the chat-style UI and dashboards
  src/           # React components and UI logic

data/            # Seed datasets & scripts for Kiswahili training / prep
demo_scripts/    # Convenience scripts and demo flows
docs/            # Runbooks and schema docs
infra/           # Docker/docker-compose configuration
```

---

## Prerequisites

- **Python 3.11+** for the backend
- **Node.js 18+** and npm (or pnpm/yarn) for the frontend
- (Optional) Docker & docker‑compose if you prefer containerized deployment

---

## Backend setup

From the `backend` folder:

```bash
cd backend

# Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Running the backend API

```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then the API should be available at:

- `http://localhost:8000`
- Interactive docs (if enabled): `http://localhost:8000/docs`

(If your actual start command or port is different, update this section.)

---

## Frontend setup

From the `frontend` folder:

```bash
cd frontend

# Install dependencies (npm or your preferred package manager)
npm install
```

### Running the frontend

```bash
cd frontend
npm run dev
```

By default Vite runs on port `5173`, so you can open:

- `http://localhost:5173`

Make sure the backend (`http://localhost:8000`) is running so the UI can call the API.

---

## Environment variables

Example environment settings:

- Backend: see `.env.example` in the project root for the variables used by the API (e.g. model paths, OpenAI keys if needed).
- Frontend: `frontend/.env` can hold the base URL for the backend API, e.g.:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Never commit real secrets (API keys, passwords) to git.

---

## Deployment

A basic Docker setup is provided in `infra/docker-compose.yml`.
You can use it as a starting point to run the backend and frontend together, or adapt it for your hosting environment (cloud VM, on‑prem server, etc.).

---

## License

_(Add a license here, e.g. MIT, once you decide how you want to share the project.)_
