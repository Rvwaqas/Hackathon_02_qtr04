"""ChatKit Backend - Main FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from src.database import init_db, close_db
from src.api import chat_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize database
    await init_db()
    print("[INFO] Database initialized")
    yield
    # Shutdown: Close database connections
    await close_db()
    print("[INFO] Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="ChatKit Backend",
    description="Task management chatbot with OpenAI Agents SDK and MCP Tools",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ChatKit Backend API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /api/{user_id}/chat",
            "conversations": "GET /api/{user_id}/conversations"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8002"))

    print(f"[INFO] Starting ChatKit Backend on {HOST}:{PORT}")

    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
