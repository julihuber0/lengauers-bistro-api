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

// ParsePDF handles POST /menu/parse requests to manually trigger PDF parsing
func (h *MenuHandler) ParsePDF(c *gin.Context) {
	// Get optional PDF URL from request body or use default
	var requestBody struct {
		PdfURL string `json:"pdf_url"`
	}

	_ = c.ShouldBindJSON(&requestBody)

	pdfURL := requestBody.PdfURL
	if pdfURL == "" {
		// Use default URL from config (we'll pass it through service or get from env)
		pdfURL = "https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf"
	}

	date, dishes, err := h.menuService.FetchAndParsePDF(pdfURL)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to parse PDF",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"date":       date.Format("2006-01-02"),
		"items":      dishes,
		"item_count": len(dishes),
		"source":     pdfURL,
	})
}
