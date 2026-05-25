from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, races, bet_plans

app = FastAPI(title="RaceNavi AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(races.router, prefix="/api", tags=["races"])
app.include_router(bet_plans.router, prefix="/api", tags=["bet_plans"])
app.include_router(admin.router, prefix="/api", tags=["admin"])


@app.get("/health")
def health():
    return {"status": "ok"}
