# K-Sasa Runbook (Prototype)

- Start locally with Docker Compose:
  - `docker compose -f infra/docker-compose.yml up --build`
- Backend health: http://localhost:8000/health
- MinIO console: http://localhost:9001 (admin/adminadmin)

Next steps:
- Wire orchestrator into FastAPI and implement adapters.
- Add RAG with FAISS and citations.
- Add voice/SMS endpoints and frontend PWA.
