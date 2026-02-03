package service

import (
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestMenuService_ParseMenuText(t *testing.T) {
	s := &menuService{}

	testPDF := `
Lengauers Bistro
Tageskarte
03.02.2026

Heute gibt's:
Schnitzel mit Pommes 9,90 €
Currywurst mit Kartoffelsalat 7,50 €
Vegetarische Lasagne 8,50 €
`

	date, items := s.parseMenuText(testPDF)

	// Check date
	expectedDate := time.Date(2026, 2, 3, 0, 0, 0, 0, time.UTC)
	assert.Equal(t, expectedDate.Format("2006-01-02"), date.Format("2006-01-02"))

	// Check items
	assert.Len(t, items, 3)
	assert.Equal(t, "Schnitzel mit Pommes", items[0].Name)
	assert.Equal(t, 9.90, items[0].Price)
	assert.Equal(t, "Gerichte", items[0].Category)
}

func TestMenuService_CleanDishName(t *testing.T) {
	s := &menuService{}

	tests := []struct {
		input    string
		expected string
	}{
		{"  Schnitzel   mit   Pommes  ", "Schnitzel mit Pommes"},
		{"Heute gibt's: Currywurst", "Currywurst"},
		{"Normal Dish", "Normal Dish"},
		{"   ", ""},
	}

	for _, tt := range tests {
		result := s.cleanDishName(tt.input)
		assert.Equal(t, tt.expected, result)
	}
}

func TestMenuService_ParseMenuText_NoDate(t *testing.T) {
	s := &menuService{}

	testPDF := `
Lengauers Bistro
Schnitzel mit Pommes 9,90 €
`

	date, items := s.parseMenuText(testPDF)

	// Without date, parsing returns zero date but may still parse items
	assert.True(t, date.IsZero())
	// This is expected behavior - items are parsed but date is zero
	// In production, the date would be set by the repository
	_ = items // Suppress unused variable warning
}

func TestMenuService_ParseMenuText_FilterAufschlag(t *testing.T) {
	s := &menuService{}

	testPDF := `
03.02.2026
Schnitzel 9,90 €
Vegetarisch Aufschlag 2,00 €
`

	_, items := s.parseMenuText(testPDF)

	// Should filter out the "Aufschlag" line
	assert.Len(t, items, 1)
	assert.False(t, strings.Contains(strings.ToLower(items[0].Name), "aufschlag"))
}
