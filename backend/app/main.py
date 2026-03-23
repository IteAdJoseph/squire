from fastapi import FastAPI

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.config import settings
from app.operational.router import router as operational_router

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(operational_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
