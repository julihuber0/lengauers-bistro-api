package database

import (
	"context"
	"fmt"
	"time"

	"github.com/lengauers-bistro/api/internal/models"
)

// GetMenuByDate retrieves all menu items for a specific date
func GetMenuByDate(ctx context.Context, date string) ([]models.MenuItem, error) {
	// Parse date string to validate format
	parsedDate, err := time.Parse("2006-01-02", date)
	if err != nil {
		return nil, fmt.Errorf("invalid date format: %v", err)
	}

	query := `
		SELECT id, date, name, price
		FROM menu_items
		WHERE date = $1
		ORDER BY id
	`

	rows, err := DB.Query(ctx, query, parsedDate)
	if err != nil {
		return nil, fmt.Errorf("database query failed: %v", err)
	}
	defer rows.Close()

	var items []models.MenuItem
	for rows.Next() {
		var item models.MenuItem
		err := rows.Scan(&item.ID, &item.Date, &item.Name, &item.Price)
		if err != nil {
			return nil, fmt.Errorf("failed to scan row: %v", err)
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration error: %v", err)
	}

	return items, nil
}

// GetAllDatesWithMenu retrieves all distinct dates that have menu items
func GetAllDatesWithMenu(ctx context.Context) ([]string, error) {
	query := `
		SELECT DISTINCT date
		FROM menu_items
		ORDER BY date DESC
	`

	rows, err := DB.Query(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("database query failed: %v", err)
	}
	defer rows.Close()

	var dates []string
	for rows.Next() {
		var date time.Time
		err := rows.Scan(&date)
		if err != nil {
			return nil, fmt.Errorf("failed to scan row: %v", err)
		}
		dates = append(dates, date.Format("2006-01-02"))
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration error: %v", err)
	}

	return dates, nil
}
