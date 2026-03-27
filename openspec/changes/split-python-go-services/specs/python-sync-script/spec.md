## ADDED Requirements

### Requirement: Script downloads PDF from URL
The script SHALL download the menu PDF from a configured URL using HTTP GET request.

#### Scenario: Successful PDF download
- **WHEN** the script runs with a valid PDF_URL environment variable
- **THEN** the PDF content is downloaded successfully

#### Scenario: Download failure
- **WHEN** the PDF URL is unreachable or returns non-200 status
- **THEN** the script exits with non-zero exit code and logs the error

### Requirement: Script parses menu date from PDF
The script SHALL extract the menu date from the PDF content.

#### Scenario: Date found in PDF
- **WHEN** the PDF contains a valid date in DD.MM.YYYY format
- **THEN** the script extracts the date correctly

#### Scenario: No date found
- **WHEN** the PDF does not contain a recognizable date
- **THEN** the script exits with non-zero exit code and logs an error

### Requirement: Script parses menu items from PDF
The script SHALL extract menu items (dish name and price) from the PDF content.

#### Scenario: Menu items found
- **WHEN** the PDF contains menu items with prices in format "€ X.XX" or "X,XX €"
- **THEN** the script extracts all dish names and prices

#### Scenario: No menu items found
- **WHEN** the PDF does not contain recognizable menu items
- **THEN** the script exits with non-zero exit code and logs an error

### Requirement: Script inserts menu items into database
The script SHALL insert parsed menu items into the PostgreSQL database in the menu_items table.

#### Scenario: New menu items
- **WHEN** menu items for a date do not exist in the database
- **THEN** the script inserts all items and logs the count of items added

#### Scenario: Duplicate menu items
- **WHEN** menu items for a date already exist in the database (same date and name)
- **THEN** the script skips insertion for duplicate items and logs the count of items skipped

### Requirement: Script uses environment variables for database credentials
The script SHALL read database connection parameters from environment variables.

#### Scenario: All credentials provided
- **WHEN** DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME environment variables are set
- **THEN** the script connects to the database using these credentials

#### Scenario: Missing credentials
- **WHEN** any required database environment variable is missing
- **THEN** the script exits with non-zero exit code and logs which variable is missing

### Requirement: Script uses environment variable for PDF URL
The script SHALL read the PDF URL from the PDF_URL environment variable.

#### Scenario: PDF_URL provided
- **WHEN** PDF_URL environment variable is set
- **THEN** the script downloads the PDF from that URL

#### Scenario: PDF_URL not provided
- **WHEN** PDF_URL environment variable is not set
- **THEN** the script uses a default URL (https://lengauers-bistro.de/wp-content/uploads/Tageskarte.pdf)

### Requirement: Script logs execution status
The script SHALL output informative log messages about its execution.

#### Scenario: Successful execution
- **WHEN** the script completes successfully
- **THEN** it logs: PDF URL, date found, number of items parsed, number of items added, number skipped

#### Scenario: Failed execution
- **WHEN** the script encounters an error
- **THEN** it logs the error message and exits with non-zero exit code

### Requirement: Script is executable standalone
The script SHALL be executable independently without running a web server.

#### Scenario: Cronjob execution
- **WHEN** the script is executed via cronjob or command line
- **THEN** it runs once, completes the sync, and exits

#### Scenario: Manual execution
- **WHEN** a user runs the script manually (python scripts/sync_menu.py)
- **THEN** it executes and provides output to stdout/stderr
