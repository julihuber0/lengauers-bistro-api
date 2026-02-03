package service

import (
	"bytes"
	"fmt"
	"io"
	"lengauers-bistro-api/internal/models"
	"lengauers-bistro-api/internal/repository"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/ledongthuc/pdf"
)

// MenuService handles business logic for menu operations
type MenuService interface {
	// GetMenuByDate retrieves menu for a specific date
	GetMenuByDate(dateStr string) ([]models.DailyMenu, error)

	// FetchAndProcessPDF fetches the PDF and processes it
	FetchAndProcessPDF(pdfURL string) error

	// FetchAndParsePDF fetches and parses PDF without saving to database
	FetchAndParsePDF(pdfURL string) (time.Time, []models.DailyMenu, error)
}

type menuService struct {
	repo repository.MenuRepository
}

// NewMenuService creates a new menu service
func NewMenuService(repo repository.MenuRepository) MenuService {
	return &menuService{
		repo: repo,
	}
}

// GetMenuByDate retrieves menu for a specific date
func (s *menuService) GetMenuByDate(dateStr string) ([]models.DailyMenu, error) {
	// Parse date
	parsedDate, err := time.Parse("2006-01-02", dateStr)
	if err != nil {
		return nil, fmt.Errorf("invalid date format. Use YYYY-MM-DD: %w", err)
	}

	return s.repo.GetMenuByDate(parsedDate)
}

// FetchAndProcessPDF fetches the PDF and processes it
func (s *menuService) FetchAndProcessPDF(pdfURL string) error {
	log.Println("Fetching PDF from:", pdfURL)

	// Fetch PDF
	resp, err := http.Get(pdfURL)
	if err != nil {
		return fmt.Errorf("error fetching PDF: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("error reading PDF body: %w", err)
	}

	// Parse PDF content
	content, err := s.readPdfContent(bytes.NewReader(bodyBytes), int64(len(bodyBytes)))
	if err != nil {
		return fmt.Errorf("error parsing PDF: %w", err)
	}

	// Parse menu text
	date, dishes := s.parseMenuText(content)
	if date.IsZero() || len(dishes) == 0 {
		log.Println("No valid menu data found in PDF")
		return fmt.Errorf("no valid menu data found")
	}

	// Save to database
	err = s.repo.UpsertMenu(date, dishes)
	if err != nil {
		return fmt.Errorf("error saving menu to database: %w", err)
	}

	log.Printf("Successfully saved/updated %d items for %s", len(dishes), date.Format("2006-01-02"))
	return nil
}

// FetchAndParsePDF fetches and parses PDF without saving to database
func (s *menuService) FetchAndParsePDF(pdfURL string) (time.Time, []models.DailyMenu, error) {
	log.Println("Fetching PDF from:", pdfURL)

	// Fetch PDF
	resp, err := http.Get(pdfURL)
	if err != nil {
		return time.Time{}, nil, fmt.Errorf("error fetching PDF: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return time.Time{}, nil, fmt.Errorf("error reading PDF body: %w", err)
	}

	// Parse PDF content
	content, err := s.readPdfContent(bytes.NewReader(bodyBytes), int64(len(bodyBytes)))
	if err != nil {
		return time.Time{}, nil, fmt.Errorf("error parsing PDF: %w", err)
	}

	// Parse menu text
	date, dishes := s.parseMenuText(content)
	if date.IsZero() || len(dishes) == 0 {
		log.Println("No valid menu data found in PDF")
		return time.Time{}, nil, fmt.Errorf("no valid menu data found")
	}

	// Set the date for all items
	for i := range dishes {
		dishes[i].MenuDate = date
	}

	log.Printf("Successfully parsed %d items for %s", len(dishes), date.Format("2006-01-02"))
	return date, dishes, nil
}

// readPdfContent extracts text content from PDF
func (s *menuService) readPdfContent(r io.ReaderAt, size int64) (string, error) {
	pdfReader, err := pdf.NewReader(r, size)
	if err != nil {
		return "", err
	}
	if pdfReader.NumPage() < 1 {
		return "", fmt.Errorf("PDF has no pages")
	}

	page := pdfReader.Page(1)
	if page.V.IsNull() {
		return "", fmt.Errorf("invalid PDF page")
	}

	// GetPlainText requires a font map parameter
	return page.GetPlainText(nil)
}

// parseMenuText parses the text extracted from PDF
func (s *menuService) parseMenuText(text string) (time.Time, []models.DailyMenu) {
	var menuDate time.Time
	var menuItems []models.DailyMenu

	// Regex for "03.02.2026"
	dateRegex := regexp.MustCompile(`(\d{2}\.\d{2}\.\d{4})`)
	// Regex for "6,90"
	priceRegex := regexp.MustCompile(`(\d{1,2},\d{2})\s*€?`)

	lines := strings.Split(text, "\n")
	var currentDishNameBuilder strings.Builder

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// 1. Find Date
		if menuDate.IsZero() {
			if dateStr := dateRegex.FindString(line); dateStr != "" {
				if parsed, err := time.Parse("02.01.2006", dateStr); err == nil {
					menuDate = parsed
					continue
				}
			}
		}

		// 2. Find Price
		priceMatch := priceRegex.FindStringSubmatch(line)
		if len(priceMatch) > 1 {
			priceStr := strings.Replace(priceMatch[1], ",", ".", 1)
			price, _ := strconv.ParseFloat(priceStr, 64)

			// Everything before the price is the last part of the name
			namePart := line[:strings.Index(line, priceMatch[0])]
			currentDishNameBuilder.WriteString(" " + namePart)

			fullName := s.cleanDishName(currentDishNameBuilder.String())

			// Filter out invalid items (like the "surcharge" note)
			if !strings.Contains(strings.ToLower(fullName), "aufschlag") && len(fullName) > 2 {
				menuItems = append(menuItems, models.DailyMenu{
					Name:     fullName,
					Category: "Gerichte", // Default
					Price:    price,
				})
			}
			currentDishNameBuilder.Reset()
			continue
		}

		// 3. Build Name (only if date is found to avoid header noise)
		if !menuDate.IsZero() {
			if currentDishNameBuilder.Len() > 0 {
				currentDishNameBuilder.WriteString(" ")
			}
			currentDishNameBuilder.WriteString(line)
		}
	}
	return menuDate, menuItems
}

// cleanDishName cleans and normalizes dish names
func (s *menuService) cleanDishName(raw string) string {
	cleaned := strings.Join(strings.Fields(raw), " ")
	cleaned = strings.TrimPrefix(cleaned, "Heute gibt's:")
	return strings.TrimSpace(cleaned)
}
