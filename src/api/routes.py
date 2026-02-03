"""API routes for the menu application."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List

from src.database import get_db_session
from src.services.menu_service import MenuService

router = APIRouter(prefix="/api", tags=["menu"])


@router.get("/menu")
def get_menu(
    date_param: str = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db_session)
):
    """
    Get menu items for a specific date.
    
    Args:
        date_param: Date string in YYYY-MM-DD format
        db: Database session
        
    Returns:
        List of menu items in the format:
        [
            {
                "id": 1,
                "name": "Kartoffelcremesuppe",
                "category": "Gericht",
                "price": 3.20
            }
        ]
    """
    # Parse date
    try:
        menu_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD (e.g., 2026-02-03)"
        )
    
    # Get menu items
    service = MenuService(db)
    items = service.get_menu_by_date(menu_date)
    
    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"No menu found for {date_param}"
        )
    
    # Convert to response format
    return [item.to_dict() for item in items]


@router.get("/menu/dates")
def get_available_dates(db: Session = Depends(get_db_session)):
    """
    Get all dates that have menu items available.
    
    Returns:
        List of dates in YYYY-MM-DD format
    """
    service = MenuService(db)
    dates = service.get_all_dates_with_menu()
    return {
        "dates": [d.isoformat() for d in dates]
    }


@router.post("/menu/sync")
def sync_menu(db: Session = Depends(get_db_session)):
    """
    Manually trigger a sync from the PDF source.
    
    Returns:
        Sync status information
    """
    service = MenuService(db)
    result = service.sync_from_pdf()
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result.get('error', 'Unknown error during sync')
        )
    
    return result


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
