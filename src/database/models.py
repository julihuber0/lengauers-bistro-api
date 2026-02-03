"""Database models for the menu application."""

from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MenuItem(Base):
    """Model for menu items."""
    
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    # Ensure we don't have duplicate dishes for the same date
    __table_args__ = (
        UniqueConstraint('date', 'name', name='unique_date_dish'),
    )
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, date={self.date}, name={self.name}, price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "category": "Gericht",
            "price": self.price
        }
