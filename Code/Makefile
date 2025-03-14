# Makefile for Python project automation

# Variables
PYTHON = python3
PIP = pip3
SRC_DIR = .
TEST_DIR = tests
DATA_DIR = .
REQUIREMENTS = requirements.txt

# Default target: run the main workflow
all: clean install process plot

# Install dependencies
install:
	$(PIP) install -r $(REQUIREMENTS)

# Process data using pipeline.py
process: $(DATA_DIR)/data.csv
	$(PYTHON) $(SRC_DIR)/pipeline.py

# Run main.py (assumed to generate plots or perform analysis)
plot: $(DATA_DIR)/cleaned_music_data.csv
	$(PYTHON) $(SRC_DIR)/main.py


# Clean up temporary files
clean:
    @echo "Are you sure you want to clean? (y/n)"
    @read ans && [ "$$ans" = "y" ] && rm -rf __pycache__ *.csv

# Phony targets (not associated with actual files)
.PHONY: all install process plot test clean