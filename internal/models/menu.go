package models

import "time"

// DailyMenu represents a single dish on the menu.
// We use JSON tags to shape the API response and GORM tags to define the DB schema.
type DailyMenu struct {
	ID        uint      `gorm:"primaryKey" json:"-"`                             // Hide ID from JSON
	MenuDate  time.Time `gorm:"type:date;uniqueIndex:idx_date_name" json:"date"` // Part of unique constraint
	Name      string    `gorm:"uniqueIndex:idx_date_name" json:"name"`           // Part of unique constraint
	Category  string    `gorm:"default:Gerichte" json:"category"`
	Price     float64   `json:"price"`
	CreatedAt time.Time `json:"-"` // Hide internal timestamps
	UpdatedAt time.Time `json:"-"`
}
