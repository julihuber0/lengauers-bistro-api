package models

import "time"

// MenuItem represents a menu item in the database
type MenuItem struct {
	ID    int       `json:"id"`
	Date  time.Time `json:"-"`
	Name  string    `json:"name"`
	Price float64   `json:"price"`
}

// MenuItemResponse is the API response format for a menu item
type MenuItemResponse struct {
	ID       int     `json:"id"`
	Name     string  `json:"name"`
	Category string  `json:"category"`
	Price    float64 `json:"price"`
}

// ToResponse converts MenuItem to MenuItemResponse
func (m *MenuItem) ToResponse() MenuItemResponse {
	return MenuItemResponse{
		ID:       m.ID,
		Name:     m.Name,
		Category: "Gericht",
		Price:    m.Price,
	}
}
