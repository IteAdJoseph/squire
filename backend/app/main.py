from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
