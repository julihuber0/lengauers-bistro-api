"""PDF parser service for extracting menu information."""

import re
import requests
import pdfplumber
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO


class PDFParserService:
    """Service for parsing menu PDFs."""
    
    @staticmethod
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
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return BytesIO(response.content)
    
    @staticmethod
    def parse_date_string(date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        # Try different date formats
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
    
    @staticmethod
    def extract_date_from_text(text: str) -> Optional[str]:
        """
        Extract date from PDF text.
        
        Args:
            text: Text content from PDF
            
        Returns:
            Date string in DD.MM.YYYY format or None
        """
        # Try to find date patterns
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
    
    @staticmethod
    def parse_menu_items(text: str) -> List[Dict[str, str]]:
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
            'externe', 'aufschlag', 'surcharge', 'zusätzlich'
        ]
        
        for i, line in enumerate(lines):
            # Skip empty lines and very short lines
            if not line.strip() or len(line.strip()) < 3:
                continue
            
            # Price patterns to match
            price_patterns = [
                r'€\s*(\d+[.,]\d{2})',      # € 12.50
                r'(\d+[.,]\d{2})\s*€',      # 12,50 €
                r'EUR\s*(\d+[.,]\d{2})',    # EUR 12.50
            ]
            
            price = None
            dish_name = line.strip()
            
            # Check if price is in the same line
            for pattern in price_patterns:
                price_match = re.search(pattern, line)
                if price_match:
                    price_str = price_match.group(1).replace(',', '.')
                    price = float(price_str)
                    # Remove the price from dish name
                    dish_name = re.sub(r'€?\s*\d+[.,]\d{2}\s*€?', '', line).strip()
                    break
            
            # If no price found in this line, check next line
            if not price and i + 1 < len(lines):
                next_line = lines[i + 1]
                for pattern in price_patterns:
                    price_match = re.search(pattern, next_line)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '.')
                        price = float(price_str)
                        break
            
            # If we have a valid dish name and price, add it
            if price and dish_name and len(dish_name) > 2:
                # Skip if it contains filter keywords
                if not any(keyword in dish_name.lower() for keyword in skip_keywords):
                    items.append({
                        'name': dish_name,
                        'price': price
                    })
        
        return items
    
    @classmethod
    def parse_pdf_from_url(cls, url: str) -> Dict[str, any]:
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
            pdf_data = cls.download_pdf(url)
            
            # Parse PDF
            menu_date = None
            all_items = []
            
            with pdfplumber.open(pdf_data) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    
                    if text:
                        # Extract date if not found yet
                        if not menu_date:
                            date_str = cls.extract_date_from_text(text)
                            if date_str:
                                menu_date = cls.parse_date_string(date_str)
                        
                        # Extract menu items
                        items = cls.parse_menu_items(text)
                        all_items.extend(items)
            
            return {
                'date': menu_date,
                'items': all_items
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
