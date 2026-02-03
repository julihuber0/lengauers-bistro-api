package scheduler

import (
	"lengauers-bistro-api/internal/service"
	"log"
	"time"
)

// Scheduler handles periodic tasks
type Scheduler struct {
	menuService   service.MenuService
	pdfURL        string
	fetchInterval time.Duration
	stopChan      chan bool
}

// NewScheduler creates a new scheduler
func NewScheduler(menuService service.MenuService, pdfURL string, fetchInterval time.Duration) *Scheduler {
	return &Scheduler{
		menuService:   menuService,
		pdfURL:        pdfURL,
		fetchInterval: fetchInterval,
		stopChan:      make(chan bool),
	}
}

// Start begins the periodic PDF fetching
func (s *Scheduler) Start() {
	// Run immediately on start
	s.processPDF()

	// Start ticker for periodic execution
	ticker := time.NewTicker(s.fetchInterval)

	go func() {
		for {
			select {
			case <-ticker.C:
				s.processPDF()
			case <-s.stopChan:
				ticker.Stop()
				log.Println("Scheduler stopped")
				return
			}
		}
	}()

	log.Printf("Scheduler started with interval: %v", s.fetchInterval)
}

// Stop stops the scheduler
func (s *Scheduler) Stop() {
	close(s.stopChan)
}

// processPDF fetches and processes the PDF
func (s *Scheduler) processPDF() {
	err := s.menuService.FetchAndProcessPDF(s.pdfURL)
	if err != nil {
		log.Printf("Error processing PDF: %v", err)
	}
}
