
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import init_database
from app.logger import get_logger, LOGGING_CONFIG
import asyncio
from app.api import router as api_router
from app.mcp import router as mcp_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # App Startup
    try:
        # Initialize database
        await asyncio.to_thread(init_database)
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
    
    yield
    
    # App Shutdown
    try:
        logger.info("Application shutting down")
    except Exception as e:
        logger.error(f"Failed to shut down application: {e}")


app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

app.include_router(
    api_router,  # Import the API router from the app.api module
    prefix="/api",  # Set a prefix for all routes in this router
    tags=["api"]  # Tag for grouping in the OpenAPI documentation
)

app.include_router(
    mcp_router,  # Import the MCP router from the app.mcp module
    prefix="/mcp",  # Set a prefix for all routes in this router
    tags=["mcp"]  # Tag for grouping in the OpenAPI documentation
)

def main():
    """Main entry point for the application."""
    import os
    import uvicorn
    # Load environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port, log_config=LOGGING_CONFIG)


if __name__ == "__main__":
    main()