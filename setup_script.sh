#!/bin/bash
set -e

# Kolory dla outputu
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "  Remote Automation Setup"
echo "  Docker + VNC + Ollama Environment"
echo "=========================================="
echo -e "${NC}"

# Funkcja do wyświetlania komunikatów
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Sprawdź wymagania
info "Sprawdzanie wymagań systemowych..."

if ! command -v docker &> /dev/null; then
    error "Docker nie jest zainstalowany!"
    echo "Zainstaluj Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    if ! docker compose version &> /dev/null; then
        error "Docker Compose nie jest zainstalowany!"
        echo "Zainstaluj Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    else
        info "Używam 'docker compose' zamiast 'docker-compose'"
        DOCKER_COMPOSE="docker compose"
    fi
else
    DOCKER_COMPOSE="docker-compose"
fi

success "Docker i Docker Compose są zainstalowane"

# Utwórz strukturę katalogów
info "Tworzenie struktury katalogów..."

mkdir -p automation
mkdir -p test_scenarios
mkdir -p shared
mkdir -p results
mkdir -p logs

success "Katalogi utworzone"

# Skopiuj pliki automatyzacji
info "Kopiowanie plików automatyzacji..."

# Sprawdź czy pliki istnieją w bieżącym katalogu
if [ -f "remote_automation.py" ]; then
    cp remote_automation.py automation/
    success "remote_automation.py skopiowany"
else
    warning "remote_automation.py nie znaleziony - musisz go dodać ręcznie"
fi

if [ -f "automation_cli.py" ]; then
    cp automation_cli.py automation/
    success "automation_cli.py skopiowany"
fi

if [ -f "config.yaml" ]; then
    cp config.yaml automation/
    success "config.yaml skopiowany"
fi

# Utwórz przykładowy scenariusz testowy
info "Tworzenie przykładowych scenariuszy testowych..."

cat > test_scenarios/test_basic.yaml << 'EOF'
# Test podstawowy - sprawdzenie połączenia i desktop
connection:
  protocol: vnc
  host: vnc-desktop
  port: 5901
  password: automation

ollama:
  url: http://ollama:11434
  model: llava:7b

scenarios:
  test_connection:
    - action: connect
    - action: wait
      seconds: 2
    - action: analyze
      question: "What desktop environment is visible? Describe what you see."
      save_to: desktop_check
    - action: disconnect
  
  test_firefox:
    - action: connect
    - action: wait
      seconds: 2
    - action: find_and_click
      element: "Firefox browser icon on desktop"
    - action: wait
      seconds: 5
    - action: verify
      expected: "Firefox browser is open"
    - action: key
      key: ctrl+l
    - action: type
      text: "about:about"
    - action: key
      key: enter
    - action: wait
      seconds: 2
    - action: analyze
      question: "Is the Firefox about page loaded with list of about pages?"
      save_to: firefox_test
    - action: disconnect
  
  test_terminal:
    - action: connect
    - action: find_and_click
      element: "Terminal icon on desktop"
    - action: wait
      seconds: 3
    - action: type
      text: "echo 'Test successful' && date"
    - action: key
      key: enter
    - action: wait
      seconds: 1
    - action: analyze
      question: "What is the output in the terminal?"
      save_to: terminal_output
    - action: disconnect
EOF

success "Scenariusz testowy utworzony: test_scenarios/test_basic.yaml"

# Utwórz skrypt quick start
info "Tworzenie skryptów pomocniczych..."

cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Uruchamianie środowiska automatyzacji..."
docker-compose up -d

echo ""
echo "⏳ Czekam na uruchomienie usług (30 sekund)..."
sleep 30

echo ""
echo "✅ Środowisko uruchomione!"
echo ""
echo "📺 Dostęp do VNC Desktop:"
echo "   - VNC Client: localhost:5901 (hasło: automation)"
echo "   - Przeglądarka: http://localhost:6080/vnc.html"
echo ""
echo "🤖 Ollama API: http://localhost:11434"
echo ""
echo "📊 Portainer (zarządzanie): http://localhost:9000"
echo ""
echo "🧪 Uruchom test:"
echo "   docker-compose exec automation-controller ./wait-for-services.sh"
echo "   docker-compose exec automation-controller python3 automation_cli.py test_scenarios/test_basic.yaml --run test_connection"
echo ""
EOF

chmod +x start.sh

cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Zatrzymywanie środowiska..."
docker-compose down
echo "✅ Zatrzymano"
EOF

chmod +x stop.sh

cat > test.sh << 'EOF'
#!/bin/bash
echo "🧪 Uruchamianie testów automatyzacji..."
docker-compose exec automation-controller /bin/bash -c "
    ./wait-for-services.sh && 
    cd /app &&
    python3 automation_cli.py test_scenarios/test_basic.yaml --interactive
"
EOF

chmod +x test.sh

cat > logs.sh << 'EOF'
#!/bin/bash
SERVICE=${1:-vnc-desktop}
echo "📋 Logi dla: $SERVICE"
docker-compose logs -f $SERVICE
EOF

chmod +x logs.sh

cat > shell.sh << 'EOF'
#!/bin/bash
SERVICE=${1:-automation-controller}
echo "🐚 Połączenie z kontenerem: $SERVICE"
docker-compose exec $SERVICE /bin/bash
EOF

chmod +x shell.sh

success "Skrypty pomocnicze utworzone"

# Utwórz README dla środowiska
cat > DOCKER_README.md << 'EOF'
# Środowisko Docker dla Remote Automation

## 🚀 Szybki start

```bash
# 1. Uruchom środowisko
./start.sh

# 2. Poczekaj 30 sekund na pełne uruchomienie

# 3. Otwórz przeglądarkę
# http://localhost:6080/vnc.html

# 4. Uruchom test
./test.sh
```

## 📦 Komponenty

- **vnc-desktop**: Ubuntu Desktop z XFCE + VNC
- **ollama**: AI Vision model server
- **automation-controller**: Kontener z skryptami automatyzacji
- **portainer**: Web UI do zarządzania

## 🔌 Porty

- `5901` - VNC Server
- `6080` - noVNC (przeglądarka)
- `11434` - Ollama API
- `9000` - Portainer

## 🛠️ Komendy

```bash
# Uruchom środowisko
./start.sh

# Zatrzymaj środowisko
./stop.sh

# Uruchom testy
./test.sh

# Zobacz logi
./logs.sh vnc-desktop
./logs.sh ollama

# Połącz się z kontenerem
./shell.sh automation-controller
./shell.sh vnc-desktop

# Ręczne uruchomienie testów
docker-compose exec automation-controller python3 automation_cli.py \
    test_scenarios/test_basic.yaml --list

docker-compose exec automation-controller python3 automation_cli.py \
    test_scenarios/test_basic.yaml --run test_connection
```

## 📁 Struktura katalogów

```
.
├── automation/          # Skrypty automatyzacji
├── test_scenarios/      # Scenariusze testowe (YAML)
├── shared/             # Pliki współdzielone
├── results/            # Wyniki testów
├── logs/               # Logi
├── docker-compose.yml  # Konfiguracja Docker
└── Dockerfile          # Obraz VNC Desktop
```

## 🧪 Testowanie

### Test 1: Sprawdzenie desktop
```bash
docker-compose exec automation-controller python3 automation_cli.py \
    test_scenarios/test_basic.yaml --run test_connection
```

### Test 2: Test Firefox
```bash
docker-compose exec automation-controller python3 automation_cli.py \
    test_scenarios/test_basic.yaml --run test_firefox
```

### Test 3: Test terminala
```bash
docker-compose exec automation-controller python3 automation_cli.py \
    test_scenarios/test_basic.yaml --run test_terminal
```

## 🐛 Debugging

### Sprawdź czy wszystkie serwisy działają
```bash
docker-compose ps
```

### Zobacz logi VNC
```bash
docker-compose logs vnc-desktop
```

### Zobacz logi Ollama
```bash
docker-compose logs ollama
```

### Połącz się z VNC Desktop bezpośrednio
```bash
docker-compose exec vnc-desktop /bin/bash
```

### Sprawdź czy Ollama działa
```bash
curl http://localhost:11434/api/tags
```

### Ręczne połączenie VNC
```bash
vncviewer localhost:5901
# Hasło: automation
```

## 🔧 Konfiguracja

### Zmiana hasła VNC
W `docker-compose.yml` zmień:
```yaml
environment:
  - VNC_PASSWORD=twoje_haslo
```

### Zmiana rozdzielczości
```yaml
environment:
  - VNC_GEOMETRY=1920x1080
```

### Zmiana modelu Ollama
W `test_scenarios/test_basic.yaml`:
```yaml
ollama:
  model: moondream  # lub llava:13b, bakllava
```

## 📊 Monitorowanie

Portainer Web UI: http://localhost:9000
- Pierwsza wizyta: utwórz konto administratora
- Podłącz do lokalnego Docker

## 🧹 Czyszczenie

```bash
# Zatrzymaj i usuń kontenery
docker-compose down

# Usuń również volumes (dane Ollama)
docker-compose down -v

# Usuń obrazy
docker-compose down --rmi all
```

## 💡 Wskazówki

1. **Pierwsze uruchomienie jest wolne** - Ollama pobiera model (~4.5GB)
2. **Poczekaj 30-60 sekund** po uruchomieniu przed testami
3. **Używaj noVNC** (przeglądarka) dla łatwego dostępu
4. **Zapisuj zmiany** w katalogu `shared/` - są trwałe
5. **Logi** sprawdzaj przez `./logs.sh [service]`

## 🔗 Przydatne linki

- Docker Desktop: https://docs.docker.com/get-docker/
- Ollama: https://ollama.ai/
- TigerVNC: https://tigervnc.org/
- noVNC: https://novnc.com/
EOF

success "DOCKER_README.md utworzony"

# Podsumowanie
echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ Setup zakończony pomyślnie!"
echo "==========================================${NC}"
echo ""
info "Struktura katalogów utworzona"
info "Skrypty pomocnicze gotowe"
info "Przykładowe scenariusze utworzone"
echo ""
echo -e "${YELLOW}Następne kroki:${NC}"
echo "1. Upewnij się że masz pliki: remote_automation.py, automation_cli.py, config.yaml"
echo "2. Uruchom: ./start.sh"
echo "3. Poczekaj 30-60 sekund"
echo "4. Otwórz: http://localhost:6080/vnc.html"
echo "5. Uruchom test: ./test.sh"
echo ""
echo -e "${BLUE}Dokumentacja: DOCKER_README.md${NC}"
echo ""
