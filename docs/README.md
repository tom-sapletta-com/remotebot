# 🤖 Remote Automation Environment

> Kompletne środowisko Docker do automatyzacji zdalnej kontroli aplikacji z integracją AI Vision przez Ollama.

[![License: Apache Software](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)

## 🎯 Co to jest?

System do automatyzacji kontroli aplikacji desktop przez zdalne połączenia (VNC/RDP/SPICE) z wykorzystaniem AI vision models do inteligentnego znajdowania elementów interfejsu i analizy zawartości ekranu.

**Idealne do:**
- ✅ Automatycznego testowania UI
- ✅ Monitorowania aplikacji
- ✅ Web scraping z AI
- ✅ Zadań repetytywnych
- ✅ Accessibility testing
- ✅ RPA (Robotic Process Automation)

## ✨ Kluczowe funkcje

- **🖥️ Środowisko VNC Desktop** - Ubuntu 22.04 z XFCE w kontenerze Docker
- **🤖 AI Vision** - Ollama z modelami llava/moondream do analizy ekranu
- **📝 Prosty DSL** - Opisz zadania w YAML bez programowania
- **🔌 Multi-protocol** - VNC, RDP, SPICE support
- **🧪 Test Framework** - Automatyczne testy z raportami
- **📊 Monitoring** - Real-time dashboard wydajności
- **🐳 Docker Compose** - Wszystko w jednym `make up`

## 🚀 Quick Start

```bash
# 1. Klonuj repozytorium
git clone <repository-url>
cd remote-automation

# 2. Setup (tworzy strukturę katalogów)
chmod +x setup.sh && ./setup.sh

# 3. Zbuduj obrazy
make build

# 4. Uruchom środowisko
make up

# 5. Otwórz przeglądarkę (po 30-60 sekundach)
# http://localhost:6080/vnc.html

# 6. Uruchom przykładowy test
make test-basic
```

**To wszystko!** 🎉

## 📦 Co zawiera projekt

```
remote-automation/
│
├── 🐳 Docker Environment
│   ├── Dockerfile              # VNC Desktop
│   ├── Dockerfile.controller   # Test Controller
│   └── docker-compose.yml      # Orkiestracja
│
├── 🤖 Automation Core
│   ├── remote_automation.py    # Główna biblioteka
│   ├── automation_cli.py       # CLI interface
│   └── config.yaml            # Konfiguracja
│
├── 🧪 Testing
│   ├── run_tests.py           # Test suite
│   ├── test_scenarios/        # Scenariusze YAML
│   └── advanced_scenarios.yaml # Zaawansowane testy
│
├── 📊 Tools
│   ├── monitor.py             # Dashboard
│   ├── Makefile              # Komendy zarządzania
│   └── setup.sh              # Instalator
│
└── 📚 Documentation
    ├── QUICK_START.md        # Szybki start
    ├── INSTALL.md            # Instalacja
    ├── TROUBLESHOOTING.md    # Rozwiązywanie problemów
    └── PERFORMANCE.md        # Optymalizacja
```

## 🎮 Przykłady użycia

### Przykład 1: Automatyczne logowanie

```yaml
scenarios:
  web_login:
    - action: connect
    - action: find_and_click
      element: "Firefox browser icon"
    - action: type
      text: "https://example.com/login"
    - action: key
      key: enter
    - action: find_and_click
      element: "username field"
    - action: type
      text: "user@example.com"
    - action: key
      key: tab
    - action: type
      text: "password123"
    - action: find_and_click
      element: "login button"
    - action: verify
      expected: "dashboard is visible"
    - action: disconnect
```

### Przykład 2: Monitoring systemu

```yaml
scenarios:
  system_check:
    - action: connect
    - action: find_and_click
      element: "Terminal"
    - action: type
      text: "top -bn1"
    - action: key
      key: enter
    - action: analyze
      question: "What is CPU and memory usage?"
      save_to: system_stats
    - action: disconnect
```

### Przykład 3: Web scraping

```yaml
scenarios:
  data_extraction:
    - action: connect
    - action: find_and_click
      element: "Firefox"
    - action: type
      text: "https://quotes.toscrape.com"
    - action: key
      key: enter
    - action: wait
      seconds: 3
    - action: analyze
      question: "Extract first 3 quotes with authors"
      save_to: quotes_data
    - action: disconnect
```

## 🛠️ Wymagania

### Minimalne
- Docker & Docker Compose
- 4GB RAM wolnego
- 10GB miejsca na dysku
- 2 CPU cores

### Rekomendowane
- 8GB RAM wolnego
- 20GB miejsca (SSD)
- 4 CPU cores
- Szybkie połączenie internetowe (pierwszy start)

### Systemy
- ✅ Linux (Ubuntu 20.04+, Fedora, etc.)
- ✅ macOS (11+)
- ✅ Windows 10/11 (z WSL2)

## 📖 Dokumentacja

| Dokument | Opis |
|----------|------|
| [QUICK_START.md](QUICK_START.md) | Szybki start (3 minuty) |
| [INSTALL.md](INSTALL.md) | Szczegółowa instalacja dla każdego OS |
| [DOCKER_README.md](DOCKER_README.md) | Docker environment details |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Rozwiązywanie problemów |
| [PERFORMANCE.md](PERFORMANCE.md) | Optymalizacja wydajności |

## 🎯 Use Cases

### 1. Automatyczne testowanie UI
```bash
# Testuj aplikację webową
make test-firefox

# Testuj formularze
docker-compose exec automation-controller \
  python3 automation_cli.py advanced_scenarios.yaml --run multi_step_form
```

### 2. Monitoring i alerting
```bash
# Real-time dashboard
python3 monitor.py

# Scheduled checks
docker-compose exec automation-controller \
  python3 automation_cli.py scenarios.yaml --run system_dashboard_check
```

### 3. Web scraping z AI
```bash
# Ekstrakacja danych
docker-compose exec automation-controller \
  python3 automation_cli.py advanced_scenarios.yaml --run web_data_extraction
```

### 4. Accessibility testing
```bash
# Test dostępności
docker-compose exec automation-controller \
  python3 automation_cli.py advanced_scenarios.yaml --run accessibility_check
```

## 💡 Podstawowe komendy

```bash
# Zarządzanie środowiskiem
make up          # Uruchom wszystko
make down        # Zatrzymaj
make restart     # Restart
make status      # Status usług
make logs        # Zobacz logi

# Testy
make test               # Pełny test suite
make test-basic         # Podstawowy test
make test-firefox       # Test przeglądarki
make interactive        # Tryb interaktywny

# Narzędzia
make shell       # Shell w kontenerze
make vnc         # Otwórz VNC w przeglądarce
make monitor     # Dashboard monitorowania

# Ollama
make pull-model         # Pobierz llava:7b
make pull-model-small   # Pobierz moondream
make list-models        # Lista modeli

# Czyszczenie
make clean       # Usuń kontenery
make clean-all   # Usuń wszystko (włącznie z danymi)

# Pomoc
make help        # Lista wszystkich komend
```

## 🔌 Dostęp do usług

Po uruchomieniu `make up`:

| Usługa | URL | Opis |
|--------|-----|------|
| noVNC | http://localhost:6080/vnc.html | Desktop przez przeglądarkę |
| VNC | `localhost:5901` | Natywny VNC client (hasło: automation) |
| Ollama API | http://localhost:11434 | API AI vision |
| Portainer | http://localhost:9000 | Zarządzanie Docker |

## 🤖 Dostępne modele AI

| Model | Rozmiar | RAM | Szybkość | Jakość | Użycie |
|-------|---------|-----|----------|---------|---------|
| moondream | 1.7GB | 3GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Development |
| llava:7b | 4.5GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **Rekomendowany** |
| llava:13b | 8GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Production (high accuracy) |
| bakllava | 5GB | 8GB | ⚡⚡⭐ | ⭐⭐⭐⭐ | Alternative |

```bash
# Zmiana modelu
docker exec automation-ollama ollama pull moondream
```

## 🧪 Tworzenie własnych scenariuszy

### 1. Utwórz plik YAML

```bash
nano test_scenarios/my_scenario.yaml
```

### 2. Zdefiniuj scenariusz

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
  my_test:
    - action: connect
    - action: find_and_click
      element: "button I want to click"
    - action: type
      text: "some text"
    - action: verify
      expected: "expected result"
    - action: disconnect
```

### 3. Uruchom

```bash
docker-compose exec automation-controller \
  python3 automation_cli.py test_scenarios/my_scenario.yaml --run my_test
```

## 📊 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make setup
      - run: make build
      - run: make up
      - run: sleep 60
      - run: make test
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - make setup
    - make build
    - make up
    - sleep 60
    - make test
```

## 🔧 Konfiguracja

### Zmienne środowiskowe

```bash
# Skopiuj przykładową konfigurację
cp .env.example .env

# Edytuj wartości
nano .env

# Przykłady:
VNC_PASSWORD=my_secure_password
VNC_GEOMETRY=1920x1080
OLLAMA_MODEL=moondream
```

### Docker Compose override

```yaml
# docker-compose.override.yml
services:
  vnc-desktop:
    environment:
      - VNC_GEOMETRY=1920x1080
    mem_limit: 4g
```

## 🐛 Troubleshooting

### Problem: Kontenery nie startują
```bash
make logs          # Zobacz logi
make status        # Sprawdź status
make restart       # Restart
```

### Problem: VNC nie odpowiada
```bash
make logs-vnc      # Logi VNC
docker exec automation-vnc pgrep Xvnc  # Sprawdź proces
```

### Problem: Ollama timeout
```bash
# Użyj lżejszego modelu
docker exec automation-ollama ollama pull moondream
```

**Więcej:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📈 Performance Tips

```bash
# 1. Użyj lżejszego modelu
OLLAMA_MODEL=moondream

# 2. Zmniejsz rozdzielczość
VNC_GEOMETRY=1024x768

# 3. Zwiększ zasoby Docker
# Settings → Resources → 8GB RAM, 4 CPUs

# 4. Monitoring
python3 monitor.py
```

**Więcej:** [PERFORMANCE.md](PERFORMANCE.md)

## 🤝 Contributing

Contributions are welcome! 

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

MIT License - zobacz [LICENSE](LICENSE) file.

## 🙏 Credits

- **Docker** - Containerization
- **Ollama** - Local AI models
- **TigerVNC** - VNC server
- **noVNC** - Browser-based VNC client
- **XFCE** - Desktop environment

## 📞 Support

- **Documentation:** Zobacz pliki *.md w projekcie
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

## 🗺️ Roadmap

- [ ] Obsługa większej liczby protokołów (X2Go, X11vnc)
- [ ] Web UI do zarządzania testami
- [ ] Integracja z więcej AI providers (OpenAI, Anthropic)
- [ ] Plugin system
- [ ] Visual regression testing
- [ ] Video recording testów
- [ ] Cloud deployment (AWS, Azure, GCP)

## ⭐ Star History

Jeśli projekt Ci pomógł, zostaw ⭐ na GitHub!

---

**Made with ❤️ for automation enthusiasts**

[⬆ Back to top](#-remote-automation-environment)
