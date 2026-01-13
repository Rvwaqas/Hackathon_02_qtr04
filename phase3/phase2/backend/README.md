# Todo Application - Backend API

FastAPI-based backend for the full-stack multi-user todo application.

## Features

- User authentication with JWT tokens
- Full CRUD operations for tasks
- Task prioritization (High, Medium, Low)
- Task tagging and filtering
- Advanced search with AND logic
- Multiple sort options
- Recurring tasks with smart date calculation
- Due dates and reminder notifications
- Database persistence with PostgreSQL
- Type-safe API with automatic validation
- API documentation with Swagger/OpenAPI

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens
- **Server**: Uvicorn ASGI server

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create `.env` file from `.env.example`

3. Start the server:
```bash
uvicorn src.main:app --reload
```

API available at `http://localhost:8000`

## API Documentation

Visit: http://localhost:8000/docs

## Development

All endpoints documented in code and Swagger UI.
