package repository

import (
	"lengauers-bistro-api/internal/models"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	assert.NoError(t, err)

	err = db.AutoMigrate(&models.DailyMenu{})
	assert.NoError(t, err)

	return db
}

func TestMenuRepository_UpsertMenu(t *testing.T) {
	db := setupTestDB(t)
	repo := NewMenuRepository(db)

	date := time.Date(2026, 2, 3, 0, 0, 0, 0, time.UTC)
	items := []models.DailyMenu{
		{Name: "Schnitzel", Category: "Gerichte", Price: 9.90},
		{Name: "Currywurst", Category: "Gerichte", Price: 7.50},
	}

	// Test insert
	err := repo.UpsertMenu(date, items)
	assert.NoError(t, err)

	// Verify insert
	result, err := repo.GetMenuByDate(date)
	assert.NoError(t, err)
	assert.Len(t, result, 2)

	// Test update
	items[0].Price = 10.90
	err = repo.UpsertMenu(date, items)
	assert.NoError(t, err)

	// Verify update
	result, err = repo.GetMenuByDate(date)
	assert.NoError(t, err)
	assert.Len(t, result, 2)

	// Find the Schnitzel item and check its price
	var schnitzelPrice float64
	for _, item := range result {
		if item.Name == "Schnitzel" {
			schnitzelPrice = item.Price
			break
		}
	}
	assert.Equal(t, 10.90, schnitzelPrice)
}

func TestMenuRepository_GetMenuByDate(t *testing.T) {
	db := setupTestDB(t)
	repo := NewMenuRepository(db)

	date := time.Date(2026, 2, 3, 0, 0, 0, 0, time.UTC)
	items := []models.DailyMenu{
		{Name: "Schnitzel", Category: "Gerichte", Price: 9.90},
	}

	err := repo.UpsertMenu(date, items)
	assert.NoError(t, err)

	// Test retrieval
	result, err := repo.GetMenuByDate(date)
	assert.NoError(t, err)
	assert.Len(t, result, 1)
	assert.Equal(t, "Schnitzel", result[0].Name)

	// Test non-existent date
	futureDate := time.Date(2026, 12, 31, 0, 0, 0, 0, time.UTC)
	result, err = repo.GetMenuByDate(futureDate)
	assert.NoError(t, err)
	assert.Len(t, result, 0)
}
