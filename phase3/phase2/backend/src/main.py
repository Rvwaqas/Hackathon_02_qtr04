"""FastAPI application setup."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

from .database import init_db
from .api import auth, tasks

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS origins
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    '["http://localhost:3000"]'
)

# Parse CORS origins
import json
try:
    cors_origins = json.loads(CORS_ORIGINS)
except:
    cors_origins = ["http://localhost:3000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Todo Application API",
    description="Full-stack multi-user todo application API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request/response logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Todo Application API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=True
    )
