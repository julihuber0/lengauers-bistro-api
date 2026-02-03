"""Database models for the menu application."""

from sqlalchemy import Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
