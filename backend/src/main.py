"""
FastAPI application entry point.

This module initializes the FastAPI application with:
- CORS middleware
- Database connection
- API routers
- OpenAPI documentation
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from src.config import settings
from src.database import create_db_and_tables
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.workspaces import router as workspaces_router
from src.api.projects import router as projects_router
from src.api.activities import router as activities_router
from src.api.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Create database tables
    print("🚀 Starting up application...")
    print(f"📊 Connecting to database: {settings.DATABASE_URL[:30]}...")
    create_db_and_tables()
    print("✅ Database tables created/verified")

    yield

    # Shutdown
    print("🛑 Shutting down application...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Secure REST API for Todo application with user authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=True,  # Enable debug mode to see full error traces
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, PATCH)
    allow_headers=["*"],  # Allow all headers including Authorization
)


# Global exception handler to ensure JSON responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and return proper JSON response.
    """
    error_detail = str(exc)
    
    # Log the full traceback for debugging
    print(f"❌ Unhandled exception: {error_detail}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal server error: {error_detail}",
            "type": "internal_error"
        }
    )


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API health check.

    Returns:
        dict: API status and version information
    """
    return {
        "status": "healthy",
        "message": "Todo App API is running",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint.

    Returns:
        dict: Application health status
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
    }


# Register API routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(activities_router)
app.include_router(analytics_router)

