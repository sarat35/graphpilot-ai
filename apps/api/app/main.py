import uvicorn
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.app_env == "development")


if __name__ == "__main__":
    main()
