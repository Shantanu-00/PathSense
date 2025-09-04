from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import places, optimize, chat, geocode
from app.config.logging import logger
import os

app = FastAPI()

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://v0-path-sense.vercel.app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle Hooks
@app.on_event("startup")
async def on_startup():
    logger.info("🔧 Application startup complete")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🛑 Application shutdown complete")

# Health Check Routes
@app.get("/")
@app.head("/")
def health_check(request: Request):
    return {"status": "ok", "message": "PathSense API is running!"}

# Optional: Redirect /docs for convenience later feature
@app.get("/docs", include_in_schema=False)
def redirect_docs():
    return RedirectResponse(url="/docs")

# Register API Routes
app.include_router(places.router, prefix="/api/v1")
app.include_router(optimize.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(geocode.router, prefix="/api/v1")

# Log server start
logger.info(" Server initialized and routes mounted")
