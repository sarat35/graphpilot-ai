# Infrastructure

Use this directory for shared local-development and deployment infrastructure. Application-specific Dockerfiles live alongside their respective applications.


===
Local development

Run the frontend:
    cd apps/web
    npm run dev

Run the future backend in another terminal:
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --port 8000
