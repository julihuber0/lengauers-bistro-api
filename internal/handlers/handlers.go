package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/lengauers-bistro/api/internal/database"
	"github.com/lengauers-bistro/api/internal/models"
	"github.com/rs/zerolog/log"
)

// HealthCheck handles GET /api/health
func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// GetMenu handles GET /api/menu?date=YYYY-MM-DD
func GetMenu(c *gin.Context) {
	dateParam := c.Query("date")
	
	// Check if date parameter is present
	if dateParam == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Missing required parameter 'date'. Use format: YYYY-MM-DD",
		})
		return
	}

	// Validate date format by attempting to parse
	_, err := time.Parse("2006-01-02", dateParam)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid date format. Use YYYY-MM-DD (e.g., 2026-02-03)",
		})
		return
	}

	// Query database
	items, err := database.GetMenuByDate(c.Request.Context(), dateParam)
	if err != nil {
		log.Error().Err(err).Str("date", dateParam).Msg("Failed to query menu")
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to query menu",
		})
		return
	}

	// Return 404 if no items found
	if len(items) == 0 {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "No menu found for " + dateParam,
		})
		return
	}

	// Convert to response format
	var response []models.MenuItemResponse
	for _, item := range items {
		response = append(response, item.ToResponse())
	}

	c.JSON(http.StatusOK, response)
}

// GetAvailableDates handles GET /api/menu/dates
func GetAvailableDates(c *gin.Context) {
	dates, err := database.GetAllDatesWithMenu(c.Request.Context())
	if err != nil {
		log.Error().Err(err).Msg("Failed to query available dates")
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to query available dates",
		})
		return
	}

	// Return empty array if no dates found
	if dates == nil {
		dates = []string{}
	}

	c.JSON(http.StatusOK, gin.H{
		"dates": dates,
	})
}

// Root handles GET /
func Root(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"name":    "Lengauer's Bistro API",
		"version": "2.0.0",
		"endpoints": gin.H{
			"health":          "/api/health",
			"get_menu":        "/api/menu?date=YYYY-MM-DD",
			"available_dates": "/api/menu/dates",
		},
	})
}
