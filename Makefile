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

build: ## Zbuduj obrazy Docker (z cache)
	@echo "$(BLUE)Budowanie obrazów Docker z cache...$(NC)"
	@DOCKER_BUILDKIT=1 docker-compose build
	@echo "$(GREEN)✓ Obrazy zbudowane$(NC)"

build-no-cache: ## Zbuduj obrazy Docker bez cache
	@echo "$(BLUE)Budowanie obrazów Docker bez cache...$(NC)"
	@DOCKER_BUILDKIT=1 docker-compose build --no-cache
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

test-basic: ## Uruchom podstawowy test scenariusza (z nagrywaniem wideo)
	@echo "$(BLUE)Test podstawowy...$(NC)"
	@echo "$(YELLOW)⚠️  Ten test używa AI (Ollama) - może zająć 30-120s$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_basic.yaml test_connection

test-quick: ## Uruchom szybki test połączenia (bez AI, bez wideo)
	@echo "$(BLUE)Szybki test połączenia (5s)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/quick_test.yaml quick_connection_test --no-recording

test-firefox: ## Uruchom test Firefox (z nagrywaniem wideo)
	@echo "$(BLUE)Test Firefox...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_basic.yaml test_firefox

test-firefox-simple: ## Uruchom test Firefox (prosty, bez AI, bez recording)
	@echo "$(BLUE)Test Firefox (simple)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_firefox_simple.yaml test_firefox_simple --no-recording

test-firefox-ai: ## Uruchom test Firefox (z AI Vision)
	@echo "$(BLUE)Test Firefox (AI)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_firefox_simple.yaml test_firefox_ai

test-firefox-ai-debug: ## Uruchom test Firefox AI (z debug screenshotami)
	@echo "$(BLUE)Test Firefox AI (debug)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_firefox_simple.yaml test_firefox_ai --debug --no-recording

test-debug: ## Debug - pokaż co widzi AI na ekranie (z screenshotami)
	@echo "$(BLUE)Debug ekranu (AI Vision)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_firefox_simple.yaml test_debug_screen --debug --no-recording

test-debug-screenshots: ## Debug - zbieraj screenshoty co 1s przez 5s
	@echo "$(BLUE)Debug screenshotów (co 1s)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_firefox_simple.yaml test_debug_screenshots --no-recording
	@echo "$(GREEN)✓ Screenshoty zapisane w: results/screenshots/$(NC)"

# ===================================
# AI-Driven Tests - Zaawansowane testy z AI
# ===================================

test-ai-adaptive: ## AI: Adaptacyjna nawigacja Firefox
	@echo "$(BLUE)AI Test: Adaptacyjna nawigacja...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml adaptive_firefox_navigation --no-recording

test-ai-search: ## AI: Inteligentne wyszukiwanie i selekcja
	@echo "$(BLUE)AI Test: Smart search...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml smart_search_and_select --no-recording

test-ai-desktop-mapper: ## AI: Mapowanie pulpitu
	@echo "$(BLUE)AI Test: Desktop mapper...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml desktop_mapper --no-recording

test-ai-monitor: ## AI: Monitor stanu aplikacji
	@echo "$(BLUE)AI Test: Application state monitor...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml application_state_monitor --no-recording

test-ai-editor: ## AI: Inteligentna edycja tekstu
	@echo "$(BLUE)AI Test: Text editing + validation...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml intelligent_text_editing --no-recording

test-ai-files: ## AI: Nawigacja plików
	@echo "$(BLUE)AI Test: File navigation...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml smart_file_navigation --no-recording

test-ai-forms: ## AI: Rozpoznawanie formularzy
	@echo "$(BLUE)AI Test: Form interaction...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml smart_form_interaction --no-recording

test-ai-errors: ## AI: Detekcja i diagnoza błędów
	@echo "$(BLUE)AI Test: Error detection...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml intelligent_error_detection --no-recording

test-ai-windows: ## AI: Zarządzanie wieloma oknami
	@echo "$(BLUE)AI Test: Multi-window management...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml window_management_test --no-recording

test-ai-visual: ## AI: Detekcja zmian wizualnych
	@echo "$(BLUE)AI Test: Visual regression...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml visual_change_detection --no-recording

test-ai-performance: ## AI: Monitoring wydajności
	@echo "$(BLUE)AI Test: Performance monitor...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml ai_performance_monitor --no-recording

test-ai-ui: ## AI: Walidacja UI
	@echo "$(BLUE)AI Test: UI validation...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml ui_validation_test --no-recording

test-ai-commands: ## AI: Analiza wyników komend
	@echo "$(BLUE)AI Test: Command output analysis...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml command_output_analysis --no-recording

test-ai-all: ## AI: Uruchom wszystkie testy AI (może zająć 10-30min)
	@echo "$(YELLOW)⚠️  Uruchamianie wszystkich testów AI - to może zająć 10-30 minut!$(NC)"
	@$(MAKE) --no-print-directory test-ai-adaptive
	@$(MAKE) --no-print-directory test-ai-desktop-mapper
	@$(MAKE) --no-print-directory test-ai-monitor
	@$(MAKE) --no-print-directory test-ai-editor
	@$(MAKE) --no-print-directory test-ai-files
	@$(MAKE) --no-print-directory test-ai-errors
	@$(MAKE) --no-print-directory test-ai-windows
	@$(MAKE) --no-print-directory test-ai-visual
	@$(MAKE) --no-print-directory test-ai-performance
	@$(MAKE) --no-print-directory test-ai-ui
	@$(MAKE) --no-print-directory test-ai-commands
	@echo "$(GREEN)✓ Wszystkie testy AI zakończone!$(NC)"

list-ai-tests: ## Pokaż listę testów AI
	@echo "$(BLUE)Dostępne testy AI:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_driven_tests.yaml dummy --list || true

# ===================================
# AI Hybrid Tests - Niezawodne (AI analiza + click_position)
# ===================================

test-hybrid-performance: ## Hybrid: Terminal performance analysis
	@echo "$(BLUE)Hybrid Test: Terminal performance...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml terminal_performance_analysis --no-recording

test-hybrid-desktop: ## Hybrid: Desktop visual analysis
	@echo "$(BLUE)Hybrid Test: Desktop analysis...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml desktop_visual_analysis --no-recording

test-hybrid-firefox: ## Hybrid: Firefox launch & page analysis
	@echo "$(BLUE)Hybrid Test: Firefox analysis...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml firefox_simple_analysis --no-recording

test-hybrid-editor: ## Hybrid: Text editor code validation
	@echo "$(BLUE)Hybrid Test: Text editor...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml text_editor_validation --no-recording

test-hybrid-state: ## Hybrid: System state comparison
	@echo "$(BLUE)Hybrid Test: State monitoring...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml system_state_comparison --no-recording

test-hybrid-errors: ## Hybrid: Error message analysis
	@echo "$(BLUE)Hybrid Test: Error analysis...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml error_message_analysis --no-recording

test-hybrid-commands: ## Hybrid: Command output parsing
	@echo "$(BLUE)Hybrid Test: Command parsing...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml command_parsing_test --no-recording

test-hybrid-accessibility: ## Hybrid: UI accessibility check
	@echo "$(BLUE)Hybrid Test: Accessibility...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml ui_accessibility_test --no-recording

test-hybrid-windows: ## Hybrid: Multi-window stress test
	@echo "$(BLUE)Hybrid Test: Window stress...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml window_stress_test --no-recording

test-hybrid-all: ## Hybrid: Uruchom wszystkie hybrid testy (10-20min)
	@echo "$(YELLOW)⚠️  Uruchamianie wszystkich hybrid testów - może zająć 10-20 minut!$(NC)"
	@$(MAKE) --no-print-directory test-hybrid-performance
	@$(MAKE) --no-print-directory test-hybrid-desktop
	@$(MAKE) --no-print-directory test-hybrid-firefox
	@$(MAKE) --no-print-directory test-hybrid-editor
	@$(MAKE) --no-print-directory test-hybrid-state
	@$(MAKE) --no-print-directory test-hybrid-errors
	@$(MAKE) --no-print-directory test-hybrid-commands
	@$(MAKE) --no-print-directory test-hybrid-accessibility
	@$(MAKE) --no-print-directory test-hybrid-windows
	@echo "$(GREEN)✓ Wszystkie hybrid testy zakończone!$(NC)"

list-hybrid-tests: ## Pokaż listę hybrid testów
	@echo "$(BLUE)Dostępne hybrid testy:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/ai_hybrid_tests.yaml dummy --list || true

# ===================================
# Auto-Login Tests - Automatyczne wykrywanie i logowanie
# ===================================

test-auto-login: ## Auto: Wykryj i wypełnij okno logowania (AI - wolne)
	@echo "$(BLUE)Auto Login: Smart detection (AI - slow)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml smart_login_detection --no-recording

test-auto-login-cv: ## Auto: CV Fast login (milisekundy!) ⚡
	@echo "$(BLUE)Auto Login: CV Fast (milliseconds)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml cv_fast_login --no-recording

test-auto-login-retry: ## Auto: Logowanie z retry
	@echo "$(BLUE)Auto Login: With retry...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml advanced_login_with_retry --no-recording

test-system-login: ## Auto: Logowanie do systemu (username + password)
	@echo "$(BLUE)Auto Login: System login...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml system_user_login --no-recording

test-app-login: ## Auto: Logowanie do aplikacji
	@echo "$(BLUE)Auto Login: Application login...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml application_login_handler --no-recording

test-password-manager: ## Auto: Smart password manager
	@echo "$(BLUE)Auto Login: Smart password manager...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml smart_password_manager --no-recording

test-multi-login: ## Auto: Logowanie wieloetapowe (VNC + System + App)
	@echo "$(BLUE)Auto Login: Multi-stage login...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml multi_stage_login --no-recording

list-auto-login: ## Pokaż listę testów auto-login
	@echo "$(BLUE)Dostępne testy auto-login:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/auto_login.yaml dummy --list || true

# ===================================
# CV Detection Tests - Super Fast! (milisekundy zamiast sekund)
# ===================================

test-cv-speed: ## CV: Szybka detekcja (milisekundy!)
	@echo "$(BLUE)CV Test: Fast detection (milliseconds)...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/cv_speed_test.yaml cv_fast_detection --no-recording

test-cv-unlock: ## CV: Fast unlock screen
	@echo "$(BLUE)CV Test: Fast unlock...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/cv_speed_test.yaml cv_fast_unlock --no-recording

test-cv-auto-login: ## CV: Complete auto-login (super fast!)
	@echo "$(BLUE)CV Test: Auto-login complete...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/cv_speed_test.yaml cv_auto_login_complete --no-recording

test-cv-vs-ai: ## CV vs AI: Speed benchmark
	@echo "$(BLUE)Speed Benchmark: CV vs AI...$(NC)"
	@echo "$(YELLOW)⚠️  This will take ~1min (AI is slow)$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/cv_speed_test.yaml speed_benchmark --no-recording

list-cv-tests: ## Pokaż listę testów CV
	@echo "$(BLUE)Dostępne testy CV:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/cv_speed_test.yaml dummy --list || true

# ===================================
# Diagnostics - Sprawdzanie połączenia i problemów
# ===================================

test-diag-screen: ## Diag: Sprawdź stan ekranu (brightness, content, issues)
	@echo "$(BLUE)Diagnostics: Screen check...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml screen_diagnostics --no-recording

test-diag-vnc: ## Diag: Sprawdź połączenie VNC
	@echo "$(BLUE)Diagnostics: VNC connection check...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml vnc_connection_check --no-recording

test-diag-lock: ## Diag: Wykryj lock screen
	@echo "$(BLUE)Diagnostics: Lock screen detection...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml lock_screen_detection --no-recording

test-diag-ready: ## Diag: Sprawdź czy desktop jest gotowy
	@echo "$(BLUE)Diagnostics: Desktop ready check...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml desktop_ready_check --no-recording

test-diag-full: ## Diag: Pełne sprawdzenie systemu (CV + AI)
	@echo "$(BLUE)Diagnostics: Full system check...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml full_system_check --no-recording

test-diag-recovery: ## Diag: Auto-recovery (spróbuj odblokować)
	@echo "$(BLUE)Diagnostics: Auto-recovery...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml auto_recovery --no-recording

list-diag-tests: ## Pokaż listę testów diagnostycznych
	@echo "$(BLUE)Dostępne testy diagnostyczne:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/diagnostics.yaml dummy --list || true

# ===================================

test-terminal: ## Uruchom test terminala (z nagrywaniem wideo)
	@echo "$(BLUE)Test terminala...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_basic.yaml test_terminal

test-no-recording: ## Uruchom test bez nagrywania (szybszy)
	@echo "$(BLUE)Test bez nagrywania...$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_basic.yaml test_connection --no-recording

list-scenarios: ## Pokaż listę dostępnych scenariuszy
	@echo "$(BLUE)Dostępne scenariusze:$(NC)"
	@docker-compose exec automation-controller python3 /app/run_scenario.py /app/test_scenarios/test_basic.yaml dummy --list || true

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
	@echo "   make test-quick          - Szybki test (BEZ AI, 5s)"
	@echo "   make test-debug          - Debug ekranu (co widzi AI)"
	@echo "   make test-debug-screenshots - Screenshoty co 1s (5s)"
	@echo "   make test-firefox-simple - Firefox (BEZ AI)"
	@echo "   make test-firefox-ai-debug - Firefox AI + screenshoty"
	@echo "   make test-basic          - Podstawowy test (z AI, 30-60s)"
	@echo "   make test                - Pełny test suite"
	@echo ""
	@echo "$(YELLOW)🤖 Testy AI-Driven:$(NC)"
	@echo "   make list-ai-tests       - Lista wszystkich testów AI"
	@echo "   make test-ai-adaptive    - Adaptacyjna nawigacja Firefox"
	@echo "   make test-ai-desktop-mapper - AI mapuje pulpit"
	@echo "   make test-ai-monitor     - Monitor stanu aplikacji"
	@echo "   make test-ai-editor      - Inteligentna edycja tekstu"
	@echo "   make test-ai-errors      - Detekcja i diagnoza błędów"
	@echo "   make test-ai-performance - Monitoring wydajności systemu"
	@echo "   make test-ai-all         - Wszystkie testy AI (10-30min)"
	@echo ""
	@echo "$(YELLOW)🔀 Testy Hybrid (AI + Niezawodne akcje):$(NC)"
	@echo "   make list-hybrid-tests   - Lista hybrid testów"
	@echo "   make test-hybrid-performance - Terminal performance"
	@echo "   make test-hybrid-desktop - Analiza pulpitu"
	@echo "   make test-hybrid-errors  - Analiza błędów"
	@echo "   make test-hybrid-commands - Parsing komend"
	@echo "   make test-hybrid-all     - Wszystkie hybrid (10-20min)"
	@echo ""
	@echo "$(YELLOW)🔐 Auto-Login (Wykrywanie i wypełnianie):$(NC)"
	@echo "   make list-auto-login     - Lista testów logowania"
	@echo "   make test-auto-login-cv  - CV Fast login (milisekundy!) ⚡"
	@echo "   make test-auto-login     - AI detection (wolne ~60s)"
	@echo "   make test-system-login   - Logowanie do systemu"
	@echo "   make test-app-login      - Logowanie do aplikacji"
	@echo "   make test-password-manager - Smart password manager"
	@echo "   make test-multi-login    - Multi-stage login"
	@echo ""
	@echo "$(YELLOW)⚡ CV Detection (100x szybsze niż AI!):$(NC)"
	@echo "   make list-cv-tests       - Lista testów CV"
	@echo "   make test-cv-speed       - Fast detection (milisekundy!)"
	@echo "   make test-cv-unlock      - Fast unlock screen"
	@echo "   make test-cv-auto-login  - Complete auto-login (super fast)"
	@echo "   make test-cv-vs-ai       - Speed benchmark: CV vs AI"
	@echo ""
	@echo "$(YELLOW)🔍 Diagnostics (Sprawdzanie problemów):$(NC)"
	@echo "   make list-diag-tests     - Lista testów diagnostycznych"
	@echo "   make test-diag-screen    - Sprawdź stan ekranu"
	@echo "   make test-diag-vnc       - Sprawdź połączenie VNC"
	@echo "   make test-diag-lock      - Wykryj lock screen"
	@echo "   make test-diag-ready     - Czy desktop gotowy?"
	@echo "   make test-diag-full      - Pełne sprawdzenie (CV+AI)"
	@echo "   make test-diag-recovery  - Auto-recovery (odblokuj)"
	@echo ""
	@echo "$(YELLOW)🎬 Nagrania testów:$(NC)"
	@echo "   Lokalizacja: $(BLUE)results/videos/$(NC)"
	@echo "   Format: MP4 (10 fps)"
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

clean-cache: ## Usuń tylko cache (pozostaw modele)
	@echo "$(BLUE)Usuwanie cache Docker...$(NC)"
	@docker volume rm -f remote-automation_pip-cache remote-automation_apt-cache 2>/dev/null || true
	@docker builder prune -f
	@echo "$(GREEN)✓ Cache usunięty$(NC)"

volumes: ## Pokaż status volumes (modele, cache)
	@echo "$(BLUE)Status volumes:$(NC)"
	@echo ""
	@echo "$(YELLOW)Ollama modele:$(NC)"
	@docker volume inspect remote-automation_ollama-data --format="Size: {{.Options}}" 2>/dev/null || echo "  Brak volume"
	@echo ""
	@echo "$(YELLOW)Cache volumes:$(NC)"
	@docker volume ls | grep remote-automation || echo "  Brak cache volumes"

models: ## Pokaż zainstalowane modele Ollama
	@echo "$(BLUE)Zainstalowane modele Ollama:$(NC)"
	@docker-compose exec ollama ollama list 2>/dev/null || echo "Ollama nie działa"

backup-results: ## Backup wyników testów
	@echo "$(BLUE)Tworzenie backup wyników...$(NC)"
	@mkdir -p backups
	@tar -czf backups/results-$$(date +%Y%m%d-%H%M%S).tar.gz results/
	@echo "$(GREEN)✓ Backup utworzony$(NC)"

backup-models: ## Backup modeli Ollama
	@echo "$(BLUE)Tworzenie backup modeli Ollama...$(NC)"
	@mkdir -p backups
	@docker run --rm -v remote-automation_ollama-data:/data -v $$(pwd)/backups:/backup alpine tar czf /backup/ollama-models-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "$(GREEN)✓ Backup modeli utworzony$(NC)"

restore-models: ## Przywróć modele Ollama z backupu
	@echo "$(BLUE)Dostępne backupy modeli:$(NC)"
	@ls -la backups/ollama-models-*.tar.gz 2>/dev/null || echo "Brak backupów modeli"
	@echo ""
	@echo "$(YELLOW)Aby przywrócić, użyj: docker run --rm -v remote-automation_ollama-data:/data -v \$$(pwd)/backups:/backup alpine tar xzf /backup/NAZWA_PLIKU.tar.gz -C /data$(NC)"

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
