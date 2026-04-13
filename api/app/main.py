from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.app.core.config import settings
from api.app.core.database import engine, Base

app = FastAPI(
    title="HYPPO API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
