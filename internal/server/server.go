package server

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/joho/godotenv/autoload"

	"lengauers-bistro-api/internal/config"
	"lengauers-bistro-api/internal/database"
	"lengauers-bistro-api/internal/handler"
	"lengauers-bistro-api/internal/repository"
	"lengauers-bistro-api/internal/scheduler"
	"lengauers-bistro-api/internal/service"
)

type Server struct {
	port int

	db          database.Service
	menuHandler *handler.MenuHandler
	scheduler   *scheduler.Scheduler
}

func NewServer() *http.Server {
	port, _ := strconv.Atoi(os.Getenv("PORT"))

	// Load configuration
	cfg := config.Load()

	// Initialize database
	dbService := database.New()
	gormDB := dbService.GetGormDB()

	// Initialize repository
	menuRepo := repository.NewMenuRepository(gormDB)

	// Run migrations
	if err := menuRepo.Migrate(); err != nil {
		log.Fatal("Failed to migrate database:", err)
	}

	// Initialize service
	menuService := service.NewMenuService(menuRepo)

	// Initialize handler
	menuHandler := handler.NewMenuHandler(menuService)

	// Initialize and start scheduler
	menuScheduler := scheduler.NewScheduler(menuService, cfg.PdfURL, cfg.FetchInterval)
	menuScheduler.Start()

	NewServer := &Server{
		port:        port,
		db:          dbService,
		menuHandler: menuHandler,
		scheduler:   menuScheduler,
	}

	// Declare Server config
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", NewServer.port),
		Handler:      NewServer.RegisterRoutes(),
		IdleTimeout:  time.Minute,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	return server
}
