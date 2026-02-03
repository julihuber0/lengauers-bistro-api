"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import uvicorn
import logging

from src.config import config
from src.database import init_db, get_db
from src.services.menu_service import MenuService
from src.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lengauer's Bistro API",
    description="API for accessing daily menu from Lengauer's Bistro",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Scheduler for periodic PDF sync
scheduler = BackgroundScheduler()


def scheduled_sync():
    """Background task to sync menu from PDF."""
    logger.info("Running scheduled PDF sync...")
    try:
        with get_db() as db:
            service = MenuService(db)
            result = service.sync_from_pdf()
            
            if result['success']:
                logger.info(f"Sync successful: {result}")
            else:
                logger.error(f"Sync failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Error during scheduled sync: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Lengauer's Bistro API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Run initial sync
    try:
        with get_db() as db:
            service = MenuService(db)
            result = service.sync_from_pdf()
            logger.info(f"Initial sync result: {result}")
    except Exception as e:
        logger.warning(f"Initial sync failed: {e}")
    
    # Start scheduler for periodic sync
    scheduler.add_job(
        scheduled_sync,
        trigger=IntervalTrigger(hours=config.SYNC_INTERVAL_HOURS),
        id="pdf_sync",
        name="Sync menu from PDF",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Scheduler started. PDF will sync every {config.SYNC_INTERVAL_HOURS} hours")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Lengauer's Bistro API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "get_menu": "/api/menu?date=YYYY-MM-DD",
            "available_dates": "/api/menu/dates",
            "manual_sync": "/api/menu/sync (POST)"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True  # Set to False in production
    )
