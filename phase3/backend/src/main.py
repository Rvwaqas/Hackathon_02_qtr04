"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings
from src.database import init_db, close_db, get_session
from src.api import auth_router, tasks_router, notifications_router
from src.services import NotificationService

# Initialize scheduler
scheduler = AsyncIOScheduler()


async def check_reminders_job():
    """Background job to check for reminders every 60 seconds."""
    async for session in get_session():
        try:
            await NotificationService.check_and_create_reminders(session)
        except Exception as e:
            print(f"Error checking reminders: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting TaskFlow API...")
    await init_db()
    print("Database initialized")

    # Start reminder scheduler
    scheduler.add_job(check_reminders_job, 'interval', seconds=60)
    scheduler.start()
    print("Reminder scheduler started")

    yield

    # Shutdown
    print("Shutting down...")
    scheduler.shutdown()
    await close_db()
    print("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="TaskFlow API",
    description="Backend API for TaskFlow - Professional Task Management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(notifications_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TaskFlow API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
