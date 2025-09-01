from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import  places, optimize, chat, geocode
from app.config.logging import logger
import os

app = FastAPI()

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("🚀 Server started")

# API routes
@app.get("/")
def root():
    return {"status": "ok", "message": "PathSense API is running!"}

app.include_router(places.router, prefix="/api/v1")
app.include_router(optimize.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(geocode.router, prefix="/api/v1")

