.PHONY: help install setup-env run run-facebook run-telegram run-pinterest run-threads run-video token-check token-refresh token-page token-threads token-setup test clean

# Default target
.DEFAULT_GOAL := help

PYTHON := python

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install Python dependencies
	$(PYTHON) -m pip install -r requirements.txt

setup-env: ## Copy .env.example to .env
	@if not exist .env (copy .env.example .env) else (echo .env already exists)

run: ## Run main bot scheduler
	$(PYTHON) main.py

run-facebook: ## Post once to Facebook
	$(PYTHON) -c "from bot.botFacebook import autoPostingFacebook; autoPostingFacebook()"

run-telegram: ## Post once to Telegram
	$(PYTHON) -c "from bot.botTelegram import autoPostingTelegram; autoPostingTelegram()"

run-pinterest: ## Post once to Pinterest
	$(PYTHON) -c "from bot.botPinterest import autoPostingPinterest; autoPostingPinterest()"

run-threads: ## Post once to Threads
	$(PYTHON) -c "from bot.botThreads import autoPostingThreads; autoPostingThreads()"

run-video: ## Post video to all platforms
	$(PYTHON) -c "from bot.postVideoTwiiter import postingVideo; postingVideo()"

token-check: ## Check all tokens validity
	$(PYTHON) bot/token_manager.py check
	$(PYTHON) bot/token_manager.py check-th

token-refresh: ## Refresh Facebook long-lived token (60 days)
	$(PYTHON) bot/token_manager.py exchange

token-page: ## Generate permanent Facebook page token
	$(PYTHON) bot/token_manager.py page

token-threads: ## Generate OAuth URL for Threads
	$(PYTHON) bot/token_manager.py oauth-th

token-setup: ## Setup tokens via Graph API Explorer (interactive)
	$(PYTHON) setup_token.py

test: ## Run basic tests
	$(PYTHON) test_post_video.py

clean: ## Remove temporary and cache files
	@echo Cleaning up...
	@if exist bot\__pycache__ rmdir /s /q bot\__pycache__
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist *.pyc del /q *.pyc
	@echo Done.
