#!/usr/bin/env python3
"""
Parse PDF menu and extract dish information (date, name, price)
"""

import pdfplumber
import re
from datetime import datetime


def parse_menu_pdf(pdf_path):
    """
    Parse the menu PDF and extract date, dish names, and prices.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries containing date, dish name, and price
    """
    dishes = []
    menu_date = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text from the page
                text = page.extract_text()
                
                if text:
                    # Try to find the date in various formats
                    # Looking for patterns like "03.02.2026" or "3. Februar 2026"
                    date_patterns = [
                        r'(\d{1,2}\.\s*\w+\s*\d{4})',  # 3. Februar 2026
                        r'(\d{1,2}\.\d{1,2}\.\d{4})',   # 03.02.2026
                        r'(\d{1,2}/\d{1,2}/\d{4})',     # 03/02/2026
                    ]
                    
                    for pattern in date_patterns:
                        date_match = re.search(pattern, text)
                        if date_match and not menu_date:
                            menu_date = date_match.group(1)
                            break
                    
                    # Extract dishes and prices
                    # Looking for patterns: dish name followed by price (e.g., "€ 12.50" or "12,50 €")
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines):
                        # Skip empty lines and headers
                        if not line.strip() or len(line.strip()) < 3:
                            continue
                        
                        # Try to find price patterns in the line or next line
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
                                price = price_match.group(1).replace(',', '.')
                                # Remove the price from dish name
                                dish_name = re.sub(r'€?\s*\d+[.,]\d{2}\s*€?', '', line).strip()
                                break
                        
                        # If no price found in this line, check next line
                        if not price and i + 1 < len(lines):
                            next_line = lines[i + 1]
                            for pattern in price_patterns:
                                price_match = re.search(pattern, next_line)
                                if price_match:
                                    price = price_match.group(1).replace(',', '.')
                                    break
                        
                        # If we have a dish name and price, add to list
                        if price and dish_name and len(dish_name) > 2:
                            # Filter out common headers/footers and non-dish information
                            skip_keywords = ['tageskarte', 'speisekarte', 'menu', 'seite', 'page', 
                                           'externe', 'aufschlag', 'surcharge', 'zusätzlich']
                            if not any(keyword in dish_name.lower() for keyword in skip_keywords):
                                dishes.append({
                                    'date': menu_date or 'Date not found',
                                    'name': dish_name,
                                    'price': f"€ {price}"
                                })
    
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []
    
    return dishes


def print_dishes(dishes):
    """Print dishes in a formatted way."""
    if not dishes:
        print("No dishes found in the PDF.")
        return
    
    print("\n" + "="*70)
    print("MENU ITEMS")
    print("="*70)
    
    for dish in dishes:
        print(f"Date: {dish['date']}")
        print(f"Dish: {dish['name']}")
        print(f"Price: {dish['price']}")
        print("-"*70)


if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "Tageskarte.pdf"
    
    print(f"Parsing menu from: {pdf_path}")
    
    # Parse the PDF
    dishes = parse_menu_pdf(pdf_path)
    
    # Print the results
    print_dishes(dishes)
    
    # Also print in simple format
    print("\n" + "="*70)
    print("SIMPLE FORMAT")
    print("="*70)
    for dish in dishes:
        print(f"{dish['date']} | {dish['name']} | {dish['price']}")
