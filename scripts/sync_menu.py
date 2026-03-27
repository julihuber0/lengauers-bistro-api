#!/usr/bin/env python3
"""
Standalone script to download, parse, and store menu from PDF.
This script is designed to be run independently via cronjob or manual execution.
All dependencies are self-contained - no external modules from src/ required.
"""

import os
import sys
import logging
import re
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Optional

import requests
import pdfplumber
from sqlalchemy import create_engine, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class MenuItem(Base):
    """Model for menu items."""
    
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Ensure we don't have duplicate dishes for the same date
    __table_args__ = (
        UniqueConstraint('date', 'name', name='unique_date_dish'),
    )


# ============================================================================
# PDF PARSING FUNCTIONS
# ============================================================================

def download_pdf(url: str) -> BytesIO:
    """
    Download PDF from URL.
    
    Args:
        url: URL of the PDF file
        
    Returns:
        BytesIO object containing PDF data
        
    Raises:
        requests.RequestException: If download fails
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return BytesIO(response.content)


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object or None if parsing fails
    """
    date_formats = [
        "%d.%m.%Y",      # 03.02.2026
        "%d/%m/%Y",      # 03/02/2026
        "%Y-%m-%d",      # 2026-02-03
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Extract date from PDF text.
    
    Args:
        text: Text content from PDF
        
    Returns:
        Date string in DD.MM.YYYY format or None
    """
    date_patterns = [
        r'(\d{1,2}\.\d{1,2}\.\d{4})',   # 03.02.2026 or 3.2.2026
        r'(\d{1,2}/\d{1,2}/\d{4})',     # 03/02/2026
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1).replace('/', '.')
            # Ensure we have leading zeros
            parts = date_str.split('.')
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2]
                return f"{day}.{month}.{year}"
    
    return None


def parse_menu_items(text: str) -> List[Dict[str, any]]:
    """
    Extract menu items (name and price) from PDF text.
    
    Args:
        text: Text content from PDF
        
    Returns:
        List of dictionaries with 'name' and 'price' keys
    """
    items = []
    lines = text.split('\n')
    
    # Filter keywords to skip
    skip_keywords = [
        'tageskarte', 'speisekarte', 'menu', 'seite', 'page',
        'externe', 'aufschlag', 'surcharge', 'zusätzlich', 'desserts'
    ]
    
    # Price patterns to match
    price_patterns = [
        r'€\s*(\d+[.,]\d{2})',      # € 12.50
        r'(\d+[.,]\d{2})\s*€',      # 12,50 €
        r'EUR\s*(\d+[.,]\d{2})',    # EUR 12.50
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines and very short lines
        if not line.strip() or len(line.strip()) < 3:
            i += 1
            continue
        
        price = None
        dish_name_parts = []
        
        # Check if price is in the current line
        for pattern in price_patterns:
            price_match = re.search(pattern, line)
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                price = float(price_str)
                # Remove the price from dish name
                dish_name_text = re.sub(r'€?\s*\d+[.,]\d{2}\s*€?', '', line).strip()
                if dish_name_text:
                    dish_name_parts.append(dish_name_text)
                break
        
        # If no price in current line, accumulate lines until we find a price
        if not price:
            dish_name_parts.append(line.strip())
            j = i + 1
            
            # Look ahead to find the price and accumulate dish name parts
            while j < len(lines) and not price:
                next_line = lines[j]
                
                # Check if this line contains a price
                for pattern in price_patterns:
                    price_match = re.search(pattern, next_line)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '.')
                        price = float(price_str)
                        # Get any text before the price in this line
                        dish_name_text = re.sub(r'€?\s*\d+[.,]\d{2}\s*€?', '', next_line).strip()
                        if dish_name_text:
                            dish_name_parts.append(dish_name_text)
                        break
                
                # If no price found and line is not empty, it's part of the dish name
                if not price and next_line.strip() and len(next_line.strip()) >= 3:
                    # Stop if we hit another keyword that might indicate a new section
                    if any(keyword in next_line.lower() for keyword in skip_keywords):
                        break
                    dish_name_parts.append(next_line.strip())
                    j += 1
                elif not price:
                    # Empty line or very short line without price - stop accumulating
                    break
                else:
                    # Found price, continue
                    j += 1
                    break
            
            # Move index past all processed lines
            i = j
        else:
            i += 1
        
        # Combine all parts of the dish name, handling hyphens at line breaks
        dish_name = ''
        for idx, part in enumerate(dish_name_parts):
            if idx == 0:
                dish_name = part
            else:
                # If previous part ends with hyphen, don't add space
                if dish_name.endswith('-'):
                    dish_name += part
                else:
                    dish_name += ' ' + part
        
        # Remove header text before colon if present
        if ':' in dish_name:
            dish_name = dish_name.split(':')[-1].strip()
        
        # If we have a valid dish name and price, add it
        if price and dish_name and len(dish_name) > 2:
            # Skip if it contains filter keywords
            if not any(keyword in dish_name.lower() for keyword in skip_keywords):
                items.append({
                    'name': dish_name,
                    'price': price
                })
    
    return items


def parse_pdf_from_url(url: str) -> Dict[str, any]:
    """
    Download and parse PDF from URL.
    
    Args:
        url: URL of the PDF file
        
    Returns:
        Dictionary with 'date' and 'items' keys
        
    Raises:
        Exception: If parsing fails
    """
    try:
        # Download PDF
        pdf_data = download_pdf(url)
        
        # Parse PDF
        menu_date = None
        all_items = []
        
        with pdfplumber.open(pdf_data) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                
                if text:
                    # Extract date if not found yet
                    if not menu_date:
                        date_str = extract_date_from_text(text)
                        if date_str:
                            menu_date = parse_date_string(date_str)
                    
                    # Extract menu items
                    items = parse_menu_items(text)
                    all_items.extend(items)
        
        return {
            'date': menu_date,
            'items': all_items
        }
        
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_env_var(name, default=None):
    """Get environment variable or exit if required and missing."""
    value = os.getenv(name, default)
    if value is None:
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    return value


def create_db_connection():
    """Create database connection using individual environment variables."""
    logger.info("Connecting to database...")
    
    db_host = get_env_var('DB_HOST')
    db_port = get_env_var('DB_PORT')
    db_user = get_env_var('DB_USER')
    db_password = get_env_var('DB_PASSWORD')
    db_name = get_env_var('DB_NAME')
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(database_url)
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)


def add_menu_items(db_session, menu_date, items):
    """
    Add menu items to database if they don't exist for the date.
    
    Args:
        db_session: Database session
        menu_date: Date of the menu
        items: List of items with 'name' and 'price' keys
        
    Returns:
        Tuple of (items_added, items_skipped)
    """
    # Get existing menu items for this date
    existing_items = db_session.query(MenuItem).filter(
        MenuItem.date == menu_date
    ).all()
    
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
        db_session.add(menu_item)
        added_count += 1
    
    try:
        db_session.commit()
        logger.info(f"Added {added_count} new menu items for {menu_date}")
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} existing menu items for {menu_date}")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Failed to commit menu items to database: {e}")
        sys.exit(1)
    
    return added_count, skipped_count


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main script execution."""
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Get PDF URL (with default)
    pdf_url = os.getenv(
        'PDF_URL',
        'https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf'
    )
    
    logger.info(f"Starting menu sync from PDF: {pdf_url}")
    
    # Create database connection
    db_session = create_db_connection()
    
    try:
        # Download and parse PDF
        logger.info(f"Downloading PDF from {pdf_url}")
        result = parse_pdf_from_url(pdf_url)
        
        menu_date = result['date']
        items = result['items']
        
        # Validate parsed data
        if not menu_date:
            logger.error("Could not extract date from PDF")
            sys.exit(1)
        
        if not items:
            logger.error("No menu items found in PDF")
            sys.exit(1)
        
        # Convert datetime to date if needed
        if isinstance(menu_date, datetime):
            menu_date = menu_date.date()
        
        logger.info(f"Date extracted from PDF: {menu_date}")
        logger.info(f"Number of items parsed: {len(items)}")
        
        # Add items to database
        added_count, skipped_count = add_menu_items(db_session, menu_date, items)
        
        logger.info(f"Sync completed successfully")
        logger.info(f"Summary: {len(items)} items parsed, {added_count} added, {skipped_count} skipped")
        
        # Exit with success
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Failed to sync from PDF: {e}")
        sys.exit(1)
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
