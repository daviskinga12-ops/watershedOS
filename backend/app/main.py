from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import alerts, carbon, restoration, watersheds

app = FastAPI(
    title="WatershedOS API",
    description="Watershed degradation intelligence platform for East Africa",
    version="0.1.0",
)

# HTTPS is enforced by Railway/Vercel in production — no HTTP fallback routes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(watersheds.router)
app.include_router(alerts.router)
app.include_router(restoration.router)
app.include_router(carbon.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "watershedos"}
