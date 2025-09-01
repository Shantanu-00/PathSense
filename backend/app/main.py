from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import places, optimize, chat, geocode
from app.config.logging import logger
import os

app = FastAPI()

# ✅ Updated CORS origins to include your deployed Vercel frontend
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://v0-path-sense-jnh21ix8m-ibm1433fe-gmailcoms-projects.vercel.app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("🚀 Server started")

# ✅ Health check route
@app.get("/")
def root():
    return {"status": "ok", "message": "PathSense API is running!"}

# ✅ Register API routes
app.include_router(places.router, prefix="/api/v1")
app.include_router(optimize.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(geocode.router, prefix="/api/v1")
