.PHONY: help setup build up down restart logs shell test status clean clean-all vnc

# Kolory
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

help: ## Pokaż tę pomoc
	@echo "$(BLUE)Remote Automation - Docker Environment$(NC)"
	@echo ""
	@echo "$(YELLOW)Dostępne komendy:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Przygotuj środowisko (pierwszy raz)
	@echo "$(BLUE)Przygotowywanie środowiska...$(NC)"
	@chmod +x setup.sh
	@./setup.sh
	@echo "$(GREEN)✓ Setup zakończony$(NC)"

build: ## Zbuduj obrazy Docker
	@echo "$(BLUE)Budowanie obrazów Docker...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✓ Obrazy zbudowane$(NC)"

up: ## Uruchom wszystkie usługi
	@echo "$(BLUE)Uruchamianie usług...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Usługi uruchomione$(NC)"
	@echo ""
	@echo "$(YELLOW)Poczekaj 30-60 sekund na pełne uruchomienie$(NC)"
	@echo ""
	@$(MAKE) --no-print-directory info

start: up ## Alias dla 'up'

down: ## Zatrzymaj wszystkie usługi
	@echo "$(BLUE)Zatrzymywanie usług...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Usługi zatrzymane$(NC)"

stop: down ## Alias dla 'down'

restart: down up ## Zrestartuj usługi

logs: ## Pokaż logi wszystkich usług
	@docker-compose logs -f

logs-vnc: ## Pokaż logi VNC Desktop
	@docker-compose logs -f vnc-desktop

logs-ollama: ## Pokaż logi Ollama
	@docker-compose logs -f ollama

logs-controller: ## Pokaż logi Controller
	@docker-compose logs -f automation-controller

shell: ## Otwórz shell w kontenerze controller
	@docker-compose exec automation-controller /bin/bash

shell-vnc: ## Otwórz shell w kontenerze VNC
	@docker-compose exec vnc-desktop /bin/bash

test: ## Uruchom testy
	@echo "$(BLUE)Uruchamianie testów...$(NC)"
	@python3 run_tests.py

test-wait: ## Uruchom testy (z czekaniem na usługi)
	@echo "$(BLUE)Uruchamianie testów z czekaniem...$(NC)"
	@python3 run_tests.py --wait

test-basic: ## Uruchom podstawowy test scenariusza
	@echo "$(BLUE)Test podstawowy...$(NC)"
	@docker-compose exec automation-controller python3 automation_cli.py test_scenarios/test_basic.yaml --run test_connection

test-firefox: ## Uruchom test Firefox
	@echo "$(BLUE)Test Firefox...$(NC)"
	@docker-compose exec automation-controller python3 automation_cli.py test_scenarios/test_basic.yaml --run test_firefox

test-terminal: ## Uruchom test terminala
	@echo "$(BLUE)Test terminala...$(NC)"
	@docker-compose exec automation-controller python3 automation_cli.py test_scenarios/test_basic.yaml --run test_terminal

interactive: ## Tryb interaktywny CLI
	@docker-compose exec automation-controller python3 automation_cli.py test_scenarios/test_basic.yaml --interactive

status: ## Pokaż status usług
	@echo "$(BLUE)Status usług:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)Testy połączeń:$(NC)"
	@echo -n "VNC (5901): "
	@nc -z -w2 localhost 5901 && echo "$(GREEN)✓ Działa$(NC)" || echo "$(RED)✗ Nie działa$(NC)"
	@echo -n "noVNC (6080): "
	@nc -z -w2 localhost 6080 && echo "$(GREEN)✓ Działa$(NC)" || echo "$(RED)✗ Nie działa$(NC)"
	@echo -n "Ollama (11434): "
	@nc -z -w2 localhost 11434 && echo "$(GREEN)✓ Działa$(NC)" || echo "$(RED)✗ Nie działa$(NC)"

info: ## Pokaż informacje o dostępie
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Remote Automation Environment$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)📺 VNC Desktop:$(NC)"
	@echo "   VNC Client: localhost:5901 (hasło: automation)"
	@echo "   Przeglądarka: $(BLUE)http://localhost:6080/vnc.html$(NC)"
	@echo ""
	@echo "$(YELLOW)🤖 Ollama API:$(NC)"
	@echo "   URL: $(BLUE)http://localhost:11434$(NC)"
	@echo ""
	@echo "$(YELLOW)📊 Portainer:$(NC)"
	@echo "   URL: $(BLUE)http://localhost:9000$(NC)"
	@echo ""
	@echo "$(YELLOW)🧪 Szybkie testy:$(NC)"
	@echo "   make test          - Pełny test suite"
	@echo "   make test-basic    - Podstawowy test"
	@echo "   make interactive   - Tryb interaktywny"
	@echo ""
	@echo "$(YELLOW)📚 Więcej komend:$(NC)"
	@echo "   make help          - Pełna lista komend"
	@echo ""

vnc: ## Otwórz VNC w przeglądarce (Linux/Mac)
	@echo "$(BLUE)Otwieranie VNC w przeglądarce...$(NC)"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:6080/vnc.html || open http://localhost:6080/vnc.html

ps: status ## Alias dla 'status'

pull-model: ## Pobierz model Ollama (llava:7b)
	@echo "$(BLUE)Pobieranie modelu llava:7b...$(NC)"
	@docker-compose exec ollama ollama pull llava:7b
	@echo "$(GREEN)✓ Model pobrany$(NC)"

pull-model-small: ## Pobierz najmniejszy model (moondream)
	@echo "$(BLUE)Pobieranie modelu moondream...$(NC)"
	@docker-compose exec ollama ollama pull moondream
	@echo "$(GREEN)✓ Model pobrany$(NC)"

list-models: ## Lista zainstalowanych modeli Ollama
	@echo "$(BLUE)Zainstalowane modele:$(NC)"
	@docker-compose exec ollama ollama list

clean: ## Usuń kontenery (zachowaj volumes)
	@echo "$(BLUE)Usuwanie kontenerów...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Kontenery usunięte$(NC)"

clean-all: ## Usuń wszystko (włącznie z volumes)
	@echo "$(RED)Usuwanie wszystkiego (włącznie z danymi)...$(NC)"
	@read -p "Czy na pewno? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi local; \
		echo "$(GREEN)✓ Wszystko usunięte$(NC)"; \
	else \
		echo "$(YELLOW)Anulowano$(NC)"; \
	fi

backup-results: ## Backup wyników testów
	@echo "$(BLUE)Tworzenie backup wyników...$(NC)"
	@mkdir -p backups
	@tar -czf backups/results-$$(date +%Y%m%d-%H%M%S).tar.gz results/
	@echo "$(GREEN)✓ Backup utworzony$(NC)"

install-deps: ## Zainstaluj zależności Python lokalnie
	@echo "$(BLUE)Instalowanie zależności...$(NC)"
	@pip3 install pillow requests pynput PyYAML vncdotool pytest
	@echo "$(GREEN)✓ Zależności zainstalowane$(NC)"

check-docker: ## Sprawdź instalację Docker
	@echo "$(BLUE)Sprawdzanie Docker...$(NC)"
	@docker --version && echo "$(GREEN)✓ Docker OK$(NC)" || echo "$(RED)✗ Docker nie znaleziony$(NC)"
	@docker-compose --version 2>/dev/null && echo "$(GREEN)✓ Docker Compose OK$(NC)" || \
		(docker compose version >/dev/null 2>&1 && echo "$(GREEN)✓ Docker Compose (plugin) OK$(NC)" || echo "$(RED)✗ Docker Compose nie znaleziony$(NC)")

# Szybkie komendy do developmentu
dev: up test-wait ## Szybki start dla developmentu (up + test)

quick: ## Najszybszy start (up + info)
	@$(MAKE) --no-print-directory up
	@sleep 5
	@$(MAKE) --no-print-directory info

# Default target
.DEFAULT_GOAL := help
