package repository

import (
	"lengauers-bistro-api/internal/models"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// MenuRepository handles database operations for menu items
type MenuRepository interface {
	// GetMenuByDate retrieves all menu items for a specific date
	GetMenuByDate(date time.Time) ([]models.DailyMenu, error)

	// UpsertMenu inserts or updates menu items for a specific date
	UpsertMenu(date time.Time, items []models.DailyMenu) error

	// Migrate runs database migrations
	Migrate() error
}

type menuRepository struct {
	db *gorm.DB
}

// NewMenuRepository creates a new menu repository
func NewMenuRepository(db *gorm.DB) MenuRepository {
	return &menuRepository{
		db: db,
	}
}

// GetMenuByDate retrieves all menu items for a specific date
func (r *menuRepository) GetMenuByDate(date time.Time) ([]models.DailyMenu, error) {
	var menu []models.DailyMenu
	result := r.db.Where("menu_date = ?", date).Find(&menu)
	if result.Error != nil {
		return nil, result.Error
	}

	// Return empty slice instead of nil
	if menu == nil {
		menu = []models.DailyMenu{}
	}

	return menu, nil
}

// UpsertMenu inserts or updates menu items for a specific date
func (r *menuRepository) UpsertMenu(date time.Time, items []models.DailyMenu) error {
	if len(items) == 0 {
		return nil
	}

	// Set the date for all items
	for i := range items {
		items[i].MenuDate = date
	}

	// GORM Upsert (On Conflict):
	// If (MenuDate + Name) exists, update the Price and Category. Otherwise, Insert.
	err := r.db.Clauses(clause.OnConflict{
		Columns:   []clause.Column{{Name: "menu_date"}, {Name: "name"}},
		DoUpdates: clause.AssignmentColumns([]string{"price", "category", "updated_at"}),
	}).Create(&items).Error

	return err
}

// Migrate runs database migrations
func (r *menuRepository) Migrate() error {
	return r.db.AutoMigrate(&models.DailyMenu{})
}
