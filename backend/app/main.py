from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import intent, places, distance, optimize, chat, geocode
from app.config.logging import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Server started")

app.include_router(intent.router, prefix="/api/v1")
app.include_router(places.router, prefix="/api/v1")
app.include_router(distance.router, prefix="/api/v1")
app.include_router(optimize.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(geocode.router, prefix="/api/v1")

# Serve frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")