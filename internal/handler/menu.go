package handler

import (
	"lengauers-bistro-api/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

// MenuHandler handles HTTP requests for menu endpoints
type MenuHandler struct {
	menuService service.MenuService
}

// NewMenuHandler creates a new menu handler
func NewMenuHandler(menuService service.MenuService) *MenuHandler {
	return &MenuHandler{
		menuService: menuService,
	}
}

// GetMenu handles GET /menu?date=YYYY-MM-DD requests
func (h *MenuHandler) GetMenu(c *gin.Context) {
	dateStr := c.Query("date")
	if dateStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'date' parameter"})
		return
	}

	menu, err := h.menuService.GetMenuByDate(dateStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, menu)
}
