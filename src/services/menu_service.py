"""Menu service for business logic and database operations."""

from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database.models import MenuItem
from src.services.pdf_parser import PDFParserService
from src.config import config


class MenuService:
    """Service for managing menu items."""
    
    def __init__(self, db: Session):
        """
        Initialize menu service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_menu_by_date(self, menu_date: date) -> List[MenuItem]:
        """
        Get all menu items for a specific date.
        
        Args:
            menu_date: Date to query
            
        Returns:
            List of MenuItem objects
        """
        return self.db.query(MenuItem).filter(
            MenuItem.date == menu_date
        ).order_by(MenuItem.id).all()
    
    def add_menu_items(self, menu_date: date, items: List[dict]) -> int:
        """
        Add menu items to database if they don't exist for the date.
        Only skips dishes that already exist (same name).
        
        Args:
            menu_date: Date of the menu
            items: List of items with 'name' and 'price' keys
            
        Returns:
            Number of items added
        """
        # Get existing menu items for this date
        existing_items = self.get_menu_by_date(menu_date)
        
        # Create a set of existing names for quick lookup
        existing_dishes = {item.name for item in existing_items}
        
        # Add only new items that don't exist yet
        added_count = 0
        skipped_count = 0
        for item in items:
            if item['name'] in existing_dishes:
                skipped_count += 1
                continue
            
            menu_item = MenuItem(
                date=menu_date,
                name=item['name'],
                price=item['price']
            )
            self.db.add(menu_item)
            added_count += 1
        
        self.db.commit()
        
        if added_count > 0:
            print(f"Added {added_count} new menu items for {menu_date}")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} existing menu items for {menu_date}")
        
        return added_count
    
    def sync_from_pdf(self) -> dict:
        """
        Download and parse PDF, then add items to database.
        
        Returns:
            Dictionary with sync status information
        """
        try:
            print(f"Downloading PDF from {config.PDF_URL}")
            
            # Parse PDF
            result = PDFParserService.parse_pdf_from_url(config.PDF_URL)
            menu_date = result['date']
            items = result['items']
            
            if not menu_date:
                return {
                    'success': False,
                    'error': 'Could not extract date from PDF'
                }
            
            if not items:
                return {
                    'success': False,
                    'error': 'No menu items found in PDF'
                }
            
            # Convert datetime to date
            if isinstance(menu_date, datetime):
                menu_date = menu_date.date()
            
            print(f"Found {len(items)} items for {menu_date}")
            
            # Add to database
            added_count = self.add_menu_items(menu_date, items)
            
            return {
                'success': True,
                'date': menu_date.isoformat(),
                'items_found': len(items),
                'items_added': added_count,
                'already_existed': added_count == 0
            }
            
        except Exception as e:
            error_msg = f"Failed to sync from PDF: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_all_dates_with_menu(self) -> List[date]:
        """
        Get all dates that have menu items.
        
        Returns:
            List of dates
        """
        dates = self.db.query(MenuItem.date).distinct().order_by(MenuItem.date.desc()).all()
        return [d[0] for d in dates]
