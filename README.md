# Remote Control Automation z Ollama Vision

System automatyzacji zdalnej kontroli komputera z integracją AI vision models przez Ollama.

## 🚀 Funkcje

- **Zdalna kontrola**: VNC, RDP, SPICE
- **AI Vision**: Analiza ekranu przez Ollama (modele do 12B)
- **⚡ CV Detection**: Computer Vision - 100x szybsze niż AI! (milisekundy)
- **🎬 Live Monitor**: Web interface z real-time preview (http://localhost:5000)
- **🔐 Auto-Login**: Automatyczne wykrywanie i wypełnianie okien logowania
- **🔍 Diagnostics**: Automatyczne wykrywanie problemów (VNC, lock screen)
- **Prosty DSL**: Opis zadań w YAML/JSON
- **Automatyzacja**: Klik, pisanie, weryfikacja, analiza
- **📹 Nagrywanie wideo**: Każdy test nagrywany do MP4 (10 fps)
- **Optymalizacja**: Cache'owanie warstw Dockera i modeli
- **Persystencja danych**: Modele i cache są zachowywane między uruchomieniami

## 🎯 Quick Start - Testy AI

### ⚡ Zacznij Tu!
➡️ **[START_HERE.md](START_HERE.md)** - Quick Start (3 minuty)

### ✅ Działające Testy (Przetestowane 2025-10-18)
```bash
# Szybki test połączenia (5s)
make test-quick

# AI Desktop Analysis (2 min)
make test-debug-screenshots      # Screenshoty + AI analiza
make test-hybrid-desktop         # Analiza pulpitu: ikony, kolory, layout

# Firefox bez AI (1 min)
make test-firefox-simple
```

### 🔐 Auto-Login - Nowe! (Wykrywanie i Wypełnianie)
```bash
# AI wykrywa okno logowania i automatycznie wypełnia
make test-auto-login              # Smart detection
make test-password-manager        # Inteligentne zarządzanie hasłami
make test-multi-login             # Multi-stage (VNC + System + App)

# Zobacz pełną listę:
make list-auto-login
```

**Zobacz:** [AUTO_LOGIN_GUIDE.md](AUTO_LOGIN_GUIDE.md) - Pełna dokumentacja

### ⚡ CV Detection - Super Fast! (100x szybsze niż AI!)
```bash
# Computer Vision - milisekundy zamiast sekund!
make test-cv-speed                # Fast detection (milisekundy)
make test-cv-unlock               # Fast unlock screen
make test-cv-auto-login           # Complete auto-login (super fast!)
make test-cv-vs-ai                # Speed benchmark

# Zobacz pełną listę:
make list-cv-tests
```

**Zobacz:** [CV_DETECTION_GUIDE.md](CV_DETECTION_GUIDE.md) - Pełna dokumentacja

### 🎬 Live Monitor - Real-Time Web Interface (NOWE!)
```bash
# Uruchom web monitoring z live preview
make live-monitor

# Otwórz w przeglądarce:
http://localhost:5000
```

**Features:**
- 📋 Lista kroków scenariusza (po lewej)
- 📺 Live VNC preview (po prawej) 
- 🔄 Real-time updates (1 FPS)
- 🎯 Wszystkie scenariusze dostępne
- 🐛 Perfect dla debugowania

**Zobacz:** [LIVE_MONITOR_GUIDE.md](LIVE_MONITOR_GUIDE.md) - Pełna dokumentacja

### 📚 Dokumentacja (Przeczytaj w tej kolejności)
1. **[START_HERE.md](START_HERE.md)** ⭐ - Zacznij tu! (3 min)
2. **[LIVE_MONITOR_GUIDE.md](LIVE_MONITOR_GUIDE.md)** 🎬 - Live web monitoring (real-time preview)
3. **[DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md)** 🔍 - Rozwiązywanie problemów (VNC, lock screen)
4. **[AI_VS_CV_COMPARISON.md](AI_VS_CV_COMPARISON.md)** 📊 - Rzeczywiste porównanie (60s vs <1s!)
5. **[CV_DETECTION_GUIDE.md](CV_DETECTION_GUIDE.md)** ⚡ - CV Detection (100x szybsze!)
6. **[AUTO_LOGIN_GUIDE.md](AUTO_LOGIN_GUIDE.md)** 🔐 - Auto-Login (wykrywanie i wypełnianie)
7. **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** 🎯 - Finalne podsumowanie + AI limitations
8. **[WORKING_TESTS_GUIDE.md](WORKING_TESTS_GUIDE.md)** - Co naprawdę działa
9. **[TEST_RESULTS_SUMMARY.md](TEST_RESULTS_SUMMARY.md)** - Wyniki testów
10. [HYBRID_TESTS_README.md](HYBRID_TESTS_README.md) - Hybrid approach (teoria)
11. [AI_TESTS_QUICK_START.md](AI_TESTS_QUICK_START.md) - Quick start guide
12. [docs/AI_TESTS.md](docs/AI_TESTS.md) - Pełna dokumentacja (teoria)

### 🎓 Co Działa vs Co Nie (Rzeczywiste Testy)
| Test | Status | Czas | Metoda |
|------|--------|------|--------|
| `test-quick` | ✅ 100% | 5s | Simple |
| `test-cv-speed` | ✅ 100% | <1s | CV ⚡ |
| `test-cv-unlock` | ✅ 95% | <3s | CV ⚡ |
| `test-debug-screenshots` | ✅ 100% | 2min | AI (30s) |
| `test-hybrid-desktop` | ✅ 95% | 2min | AI (varied) |
| `test-firefox-simple` | ✅ 90% | 1min | Simple |
| `test-ai-adaptive` | ❌ 30% | 3min | AI (zawodzi) |
| `test-hybrid-performance` | ⚠️ 40% | - | Hybrid (fix needed) |

**Zobacz [TEST_RESULTS_SUMMARY.md](TEST_RESULTS_SUMMARY.md) dla pełnych wyników.**

## 📋 Wymagania

### System
- Python 3.8+
- Ollama zainstalowane i uruchomione
- Klient VNC/RDP/SPICE

### Instalacja zależności

```bash
# Podstawowe pakiety Python
pip install pillow requests pynput PyYAML

# Dla VNC
pip install vncdotool

# Dla RDP (Linux)
sudo apt-get install freerdp2-x11

# Dla SPICE (Linux)
sudo apt-get install virt-viewer
```

### Instalacja Ollama (w kontenerze)

System automatycznie pobiera i konfiguruje Ollama w kontenerze. Domyślnie używany jest model `llava:7b`.

Dostępne komendy zarządzania modelami:

```bash
# Lista zainstalowanych modeli
make models

# Backup modeli do pliku
make backup-models

# Przywróć modele z backupu
make restore-models

# Usuń cache (zachowując modele)
make clean-cache
```

### Zoptymalizowane budowanie

```bash
# Buduj z cache (domyślnie)
make build

# Wymuś pełny rebuild
make build-no-cache
```

## 🛠️ Rozwiązywanie problemów

### Problem: Błąd połączenia VNC

Jeśli testy nie mogą się połączyć z VNC, sprawdź:

```bash
# Sprawdź status kontenera VNC
docker-compose ps vnc-desktop

# Zobacz logi VNC
docker-compose logs vnc-desktop

# Sprawdź, czy port 5901 jest otwarty
ss -tuln | grep 5901
```

### Problem: Brak modeli Ollama

Jeśli modele nie są dostępne:

```bash
# Sprawdź, czy kontener Ollama działa
docker-compose ps ollama

# Zobacz logi Ollama
docker-compose logs ollama

# Ręczne pobranie modelu
docker-compose exec ollama ollama pull llava:7b
```

### Problem: Brak miejsca na dysku

```bash
# Wyczyść nieużywane obrazy i kontenery
docker system prune -a

# Sprawdź zajętość volumes
docker system df -v
```

## 🎯 Szybki start

### 1. Uruchom Ollama

```bash
# Ollama musi działać w tle
ollama serve
```

### 2. Skonfiguruj połączenie

W pliku Python zmień konfigurację:

```python
config = {
    'protocol': 'vnc',  # lub 'rdp', 'spice'
    'host': 'localhost',
    'port': 5900,
    'password': 'your_password'
}
```

### 3. Uruchom przykład

```bash
python remote_automation.py
```

## 📝 DSL - Język kontroli

### Podstawowe akcje

```yaml
# Połącz się
- action: connect

# Czekaj
- action: wait
  seconds: 2

# Kliknij na współrzędnych
- action: click
  x: 100
  y: 200

# Znajdź i kliknij (AI)
- action: find_and_click
  element: "Chrome browser icon"

# Wpisz tekst
- action: type
  text: "Hello World"

# Naciśnij klawisz
- action: key
  key: enter  # enter, tab, esc, space, ctrl+c, etc.

# Zweryfikuj stan (AI)
- action: verify
  expected: "login page is displayed"

# Analizuj ekran (AI)
- action: analyze
  question: "What is the error message?"
  save_to: error_text

# Zapisz screenshot (dla debugowania)
- action: screenshot
  name: "my_screenshot"

# Rozłącz
- action: disconnect
```

### Tryb debugowania ze screenshotami

Podczas uruchamiania scenariuszy możesz włączyć tryb debug, który:
- Dodaje timestampy do wszystkich logów
- Zapisuje screenshoty **przed i po każdej akcji**
- Zapisuje screenshoty w `/app/results/screenshots/`

```bash
# Uruchom scenariusz z debug mode
python run_scenario.py scenario.yaml test_name --debug --no-recording

# Lub przez Make
make test-debug              # Debug z AI Vision
make test-debug-screenshots  # Zbieranie screenshotów co 1s
make test-firefox-ai-debug   # Firefox test z debug screenshotami
```

**Format nazw screenshotów:**
```
20251018_190433_001_before_connect.png
20251018_190435_002_after_connect.png
20251018_190436_003_before_find_and_click.png
```

Gdzie:
- `20251018_190433` - timestamp (YYYYMMDD_HHMMSS)
- `001` - numer kroku
- `before_connect` - nazwa akcji

## 💡 Przykładowe scenariusze

### Przykład 1: Automatyczne logowanie

```python
script = [
    {'action': 'connect'},
    {'action': 'find_and_click', 'element': 'browser icon'},
    {'action': 'wait', 'seconds': 2},
    {'action': 'type', 'text': 'https://example.com/login'},
    {'action': 'key', 'key': 'enter'},
    {'action': 'wait', 'seconds': 3},
    {'action': 'find_and_click', 'element': 'username field'},
    {'action': 'type', 'text': 'user@example.com'},
    {'action': 'key', 'key': 'tab'},
    {'action': 'type', 'text': 'password123'},
    {'action': 'find_and_click', 'element': 'login button'},
    {'action': 'verify', 'expected': 'dashboard is visible'},
    {'action': 'disconnect'}
]
```

### Przykład 2: Monitoring terminala

```python
script = [
    {'action': 'connect'},
    {'action': 'find_and_click', 'element': 'terminal'},
    {'action': 'type', 'text': 'htop'},
    {'action': 'key', 'key': 'enter'},
    {'action': 'wait', 'seconds': 2},
    {'action': 'analyze', 'question': 'What is CPU and memory usage?'},
    {'action': 'key', 'key': 'q'},
    {'action': 'disconnect'}
]
```

### Przykład 3: Test aplikacji webowej

```python
script = [
    {'action': 'connect'},
    {'action': 'find_and_click', 'element': 'search button'},
    {'action': 'verify', 'expected': 'search results appear'},
    {'action': 'analyze', 'question': 'How many results are shown?'},
    {'action': 'find_and_click', 'element': 'first result link'},
    {'action': 'wait', 'seconds': 2},
    {'action': 'verify', 'expected': 'detail page is loaded'},
    {'action': 'disconnect'}
]
```

## 🔧 Zaawansowana konfiguracja

### Użycie z YAML

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

script = config['scenarios']['browser_search']
engine.execute_dsl(script)
```

### Zmienne i warunki

```python
# Zapisz wynik do zmiennej
{'action': 'analyze', 'question': 'Is logged in?', 'save_to': 'login_status'}

# Użyj później
print(engine.variables['login_status'])
```

### Własne akcje

```python
class CustomAutomation(AutomationEngine):
    def execute_dsl(self, script):
        for step in script:
            if step['action'] == 'custom_scroll':
                # Twoja logika
                pass
            else:
                super().execute_dsl([step])
```

## 🎨 Dostępne modele Ollama

| Model | Rozmiar | RAM | Opis |
|-------|---------|-----|------|
| moondream | 1.7GB | 4GB | Najmniejszy, bardzo szybki |
| llava:7b | 4.5GB | 8GB | Dobry balans |
| bakllava | 5GB | 8GB | Dobra jakość |
| llava:13b | 8GB | 16GB | Najdokładniejszy |

## 🔒 Bezpieczeństwo

⚠️ **WAŻNE**:
- Używaj tylko na własnych systemach lub z odpowiednimi pozwoleniami
- Nie przechowuj haseł w kodzie - użyj zmiennych środowiskowych
- Testuj skrypty w bezpiecznym środowisku przed produkcją

```bash
# Bezpieczne hasła
export VNC_PASSWORD="your_password"
```

```python
import os
config['password'] = os.getenv('VNC_PASSWORD')
```

## 🐛 Debugowanie

### Sprawdź Ollama

```bash
# Test podstawowy
curl http://localhost:11434/api/generate -d '{
  "model": "llava:7b",
  "prompt": "Hello"
}'
```

### Logi połączenia

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Screenshot debugowy

```python
# Zapisz screenshot
screen = controller.capture_screen()
screen.save('debug_screen.png')
```

## 📚 Użyteczne komendy

```bash
# Lista modeli Ollama
ollama list

# Usuń model
ollama rm llava:7b

# Status Ollama
systemctl status ollama

# Test VNC
vncviewer localhost:5900

# Test RDP
xfreerdp /v:localhost:3389
```

## 🤝 Zastosowania

- 🧪 Automatyczne testowanie UI
- 📊 Monitoring aplikacji
- 🔄 Zadania repetytywne
- 📋 Web scraping z AI
- ♿ Narzędzia accessibility
- 🎮 Automatyzacja gier (testy)

## ⚡ Optymalizacja

### Szybsze działanie

```python
# Używaj lżejszego modelu
vision = OllamaVision(model="moondream")

# Zmniejsz rozdzielczość
screen = screen.resize((800, 600))

# Cache połączeń
```

### Mniejsze zużycie RAM

```python
# Uruchom Ollama z limitem
OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 ollama serve
```

## 📄 Licencja

Apache Software License - do użytku edukacyjnego i zgodnego z prawem.

## 🆘 Pomoc

Problemy? Sprawdź:
1. Czy Ollama działa: `ollama list`
2. Czy połączenie VNC/RDP jest aktywne
3. Czy model jest pobrany: `ollama pull llava:7b`
4. Logi w konsoli


# 🚀 Quick Start Guide - Remote Automation

Kompletne środowisko Docker do automatyzacji zdalnej kontroli z AI Vision.

## ⚡ 3-minutowy start

```bash
# 1. Setup (tylko za pierwszym razem)
chmod +x setup.sh && ./setup.sh

# 2. Uruchom środowisko
make up
# lub: ./start.sh

# 3. Poczekaj 30-60 sekund

# 4. Otwórz przeglądarkę
# http://localhost:6080/vnc.html

# 5. Uruchom test
make test-basic
```

**Gotowe!** 🎉

---

## 📋 Wymagania

- **Docker** i **Docker Compose**
- **4GB RAM** wolnego (minimum)
- **10GB miejsca** na dysku
- System: Linux, macOS, Windows (z WSL2)

### Sprawdź instalację

```bash
make check-docker
```

---

## 🎯 Krok po kroku

### 1️⃣ Pobierz i rozpakuj

```bash
# Sklonuj lub pobierz projekt
git clone <repository-url>
cd remote-automation

# Lub po prostu rozpakuj ZIP
unzip remote-automation.zip
cd remote-automation
```

### 2️⃣ Uruchom setup

```bash
# Setup utworzy strukturę katalogów i pliki
make setup
# lub: chmod +x setup.sh && ./setup.sh
```

To utworzy:
```
.
├── automation/         # Skrypty automatyzacji
├── test_scenarios/     # Scenariusze testowe
├── shared/            # Pliki współdzielone
├── results/           # Wyniki testów
└── logs/              # Logi
```

### 3️⃣ Zbuduj obrazy (pierwsze uruchomienie)

```bash
make build
```

To może zająć 5-10 minut za pierwszym razem.

### 4️⃣ Uruchom środowisko

```bash
make up
```

Usługi które się uruchomią:
- **vnc-desktop** - Ubuntu Desktop z VNC
- **ollama** - AI Vision server (automatycznie pobierze model)
- **automation-controller** - Kontener ze skryptami
- **portainer** - Web UI (opcjonalne)

### 5️⃣ Poczekaj na pełne uruchomienie

```bash
# Sprawdź status
make status

# Lub zobacz logi
make logs
```

Wszystko gotowe gdy zobaczysz:
- ✓ VNC (5901) - Działa
- ✓ noVNC (6080) - Działa  
- ✓ Ollama (11434) - Działa

### 6️⃣ Otwórz VNC Desktop

**Opcja A: Przeglądarka (najprostsze)**
```
http://localhost:6080/vnc.html
```

**Opcja B: VNC Client**
```bash
vncviewer localhost:5901
# Hasło: automation
```

**Opcja C: Automatycznie (Linux/Mac)**
```bash
make vnc
```

### 7️⃣ Uruchom testy

```bash
# Pełny test suite
make test

# Lub pojedyncze testy (z nagrywaniem wideo 📹)
make test-basic      # Podstawowy test połączenia
make test-firefox    # Test przeglądarki
make test-terminal   # Test terminala

# Test bez nagrywania (szybszy)
make test-no-recording

# Lista dostępnych scenariuszy
make list-scenarios

# Tryb interaktywny
make interactive
```

**📹 Nagrania wideo testów**: Wszystkie testy są automatycznie nagrywane do `results/videos/*.mp4`. Zobacz [VIDEO_RECORDING.md](VIDEO_RECORDING.md) dla szczegółów.

---

## 🎮 Codzienne użycie

### Uruchom środowisko

```bash
make up         # Uruchom wszystko
make info       # Pokaż informacje o dostępie
```

### Zatrzymaj środowisko

```bash
make down       # Zatrzymaj wszystko
```

### Zobacz co się dzieje

```bash
make status     # Status wszystkich usług
make logs       # Logi wszystkich usług
make logs-vnc   # Tylko logi VNC
```

### Wejdź do kontenera

```bash
make shell      # Shell w kontenerze controller
make shell-vnc  # Shell w VNC Desktop
```

### Uruchom scenariusze

```bash
# Tryb interaktywny
make interactive

# Konkretny scenariusz
docker-compose exec automation-controller \
  python3 automation_cli.py \
  test_scenarios/test_basic.yaml \
  --run nazwa_scenariusza
```

---

## 📁 Struktura projektu

```
remote-automation/
│
├── Dockerfile              # Obraz VNC Desktop
├── Dockerfile.controller   # Obraz Controller
├── docker-compose.yml      # Konfiguracja usług
├── Makefile               # Komendy zarządzania
│
├── setup.sh               # Skrypt instalacyjny
├── start.sh               # Szybki start
├── stop.sh                # Szybkie zatrzymanie
├── test.sh                # Szybkie testy
├── run_tests.py           # Test suite
│
├── automation/            # Twoje skrypty automatyzacji
│   ├── remote_automation.py
│   ├── automation_cli.py
│   └── config.yaml
│
├── test_scenarios/        # Scenariusze testowe (YAML)
│   └── test_basic.yaml
│
├── shared/                # Pliki współdzielone między hostom a kontenerem
├── results/               # Wyniki testów (JSON)
└── logs/                  # Logi aplikacji
```

---

## 🔧 Konfiguracja

### Zmiana hasła VNC

W `docker-compose.yml`:
```yaml
environment:
  - VNC_PASSWORD=twoje_nowe_haslo
```

### Zmiana rozdzielczości

```yaml
environment:
  - VNC_GEOMETRY=1920x1080
```

### Zmiana modelu Ollama

```bash
# W kontenerze
docker-compose exec ollama ollama pull moondream  # Najmniejszy
docker-compose exec ollama ollama pull llava:13b  # Większy

# Lista modeli
make list-models
```

W `test_scenarios/test_basic.yaml`:
```yaml
ollama:
  model: moondream  # lub llava:7b, llava:13b, bakllava
```

---

## 🧪 Tworzenie własnych scenariuszy

### Przykład: Automatyczne logowanie

Utwórz `test_scenarios/my_login.yaml`:

```yaml
connection:
  protocol: vnc
  host: vnc-desktop
  port: 5901
  password: automation

ollama:
  url: http://ollama:11434
  model: llava:7b

scenarios:
  login_test:
    - action: connect
    
    - action: find_and_click
      element: "Firefox browser icon"
    
    - action: wait
      seconds: 3
    
    - action: type
      text: "https://example.com/login"
    
    - action: key
      key: enter
    
    - action: wait
      seconds: 2
    
    - action: find_and_click
      element: "username input field"
    
    - action: type
      text: "user@example.com"
    
    - action: key
      key: tab
    
    - action: type
      text: "password123"
    
    - action: find_and_click
      element: "login button"
    
    - action: verify
      expected: "dashboard is visible after login"
    
    - action: disconnect
```

### Uruchom swój scenariusz

```bash
docker-compose exec automation-controller \
  python3 automation_cli.py \
  test_scenarios/my_login.yaml \
  --run login_test
```

---

## 🐛 Rozwiązywanie problemów

### Problem: Kontenery się nie uruchamiają

```bash
# Sprawdź logi
make logs

# Restart
make restart

# Sprawdź czy porty są wolne
netstat -tuln | grep -E '5901|6080|11434|9000'
```

### Problem: Ollama nie pobiera modelu

```bash
# Ręcznie pobierz model
make pull-model

# Lub najmniejszy model
make pull-model-small

# Sprawdź logi Ollama
make logs-ollama
```

### Problem: VNC nie odpowiada

```bash
# Sprawdź logi VNC
make logs-vnc

# Restart kontenera VNC
docker-compose restart vnc-desktop

# Sprawdź czy port jest otwarty
nc -zv localhost 5901
```

### Problem: Testy nie przechodzą

```bash
# Uruchom testy z pełną diagnozą
python3 run_tests.py --wait

# Sprawdź wyniki
cat results/test_results.json

# Ręcznie połącz się z kontenerem
make shell
```

### Problem: Brak miejsca na dysku

```bash
# Wyczyść stare obrazy
docker system prune -a

# Sprawdź zużycie
docker system df
```

---

## 📊 Monitorowanie

### Portainer Web UI

```
http://localhost:9000
```

- Pierwsza wizyta: utwórz konto admina
- Wybierz "Get Started"
- Zobacz wszystkie kontenery, logi, metryki

### Metryki w czasie rzeczywistym

```bash
# Stats wszystkich kontenerów
docker stats

# Tylko VNC
docker stats automation-vnc
```

---

## 🧹 Czyszczenie

### Zatrzymaj i usuń kontenery

```bash
make clean
```

### Usuń wszystko (włącznie z danymi)

```bash
make clean-all
```

⚠️ **To usunie:**
- Wszystkie kontenery
- Volumes (dane Ollama, modele)
- Lokalne obrazy

---

## 💡 Wskazówki

### Optymalizacja wydajności

1. **Używaj lżejszych modeli** w trakcie developmentu
   ```bash
   make pull-model-small  # moondream - 1.7GB
   ```

2. **Zmniejsz rozdzielczość VNC** jeśli wolno działa
   ```yaml
   VNC_GEOMETRY=1024x768
   ```

3. **Ogranic równoległe połączenia Ollama**
   ```yaml
   environment:
     - OLLAMA_NUM_PARALLEL=1
   ```

### Best practices

1. ✅ **Zawsze czekaj 30-60s** po `make up`
2. ✅ **Używaj `shared/`** dla plików między hostem a kontenerem
3. ✅ **Zapisuj wyniki testów** w `results/`
4. ✅ **Twórz kopie** scenariuszy przed edycją
5. ✅ **Sprawdzaj logi** przy problemach

### Przydatne komendy

```bash
# Szybki restart z testami
make dev

# Najszybszy start
make quick

# Backup wyników
make backup-results

# Lista wszystkich komend
make help
```

---

## 🆘 Pomoc

### Dokumentacja

- `DOCKER_README.md` - Szczegółowa dokumentacja Docker
- `README.md` - Dokumentacja głównej aplikacji
- `make help` - Lista wszystkich komend

### Sprawdź instalację

```bash
make check-docker  # Docker
make status        # Usługi
make test          # Testy funkcjonalne
```

### Dodatkowe zasoby

- Docker: https://docs.docker.com
- Ollama: https://ollama.ai
- VNC: https://tigervnc.org
- noVNC: https://novnc.com

---

## 🎓 Przykładowe use cases

### 1. Testowanie UI aplikacji webowej

```bash
# Utwórz scenariusz testowy
# Uruchom wielokrotne testy
# Zbierz screenshots i raporty
```

### 2. Automatyzacja zadań administracyjnych

```bash
# Monitoring serwerów przez terminal
# Automatyczne updaty
# Zbieranie metryk
```

### 3. Web scraping z AI

```bash
# Nawigacja przez strony
# Ekstrakcja danych przez AI
# Analiza treści wizualnych
```

### 4. Automatyzacja pracy biurowej

```bash
# Wypełnianie formularzy
# Generowanie raportów
# Przetwarzanie dokumentów
```

---

## 📚 Dokumentacja

- **[VIDEO_RECORDING.md](VIDEO_RECORDING.md)** - Szczegóły nagrywania testów do MP4
- **[CACHING.md](CACHING.md)** - Optymalizacja Docker i cache
- **[test_scenarios/](test_scenarios/)** - Przykładowe scenariusze testowe

---

## 🚀 Co dalej?

1. **Przejrzyj przykładowe scenariusze** w `test_scenarios/`
2. **Stwórz własny scenariusz** automatyzacji
3. **Eksperymentuj z różnymi modelami** Ollama
4. **Dziel się swoimi scenariuszami** z zespołem

---

**Powodzenia! 🎉**

Jeśli masz pytania, sprawdź dokumentację lub uruchom:
```bash
make help
```
