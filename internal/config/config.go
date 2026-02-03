package config

import (
	"os"
	"time"
)

// Config holds all configuration for the application
type Config struct {
	// PDF Configuration
	PdfURL        string
	FetchInterval time.Duration

	// Server Configuration
	Port string

	// Database Configuration
	DBHost     string
	DBPort     string
	DBDatabase string
	DBUsername string
	DBPassword string
	DBSchema   string
}

// Load loads configuration from environment variables
func Load() *Config {
	return &Config{
		// PDF Settings
		PdfURL:        getEnv("PDF_URL", "https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf"),
		FetchInterval: getDurationEnv("FETCH_INTERVAL", 1*time.Hour),

		// Server Settings
		Port: getEnv("PORT", "8080"),

		// Database Settings
		DBHost:     getEnv("BLUEPRINT_DB_HOST", "localhost"),
		DBPort:     getEnv("BLUEPRINT_DB_PORT", "5432"),
		DBDatabase: getEnv("BLUEPRINT_DB_DATABASE", "blueprint"),
		DBUsername: getEnv("BLUEPRINT_DB_USERNAME", "postgres"),
		DBPassword: getEnv("BLUEPRINT_DB_PASSWORD", "password"),
		DBSchema:   getEnv("BLUEPRINT_DB_SCHEMA", "public"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getDurationEnv(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if duration, err := time.ParseDuration(value); err == nil {
			return duration
		}
	}
	return defaultValue
}
