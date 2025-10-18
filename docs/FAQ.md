# ❓ FAQ - Często zadawane pytania

Odpowiedzi na najczęściej zadawane pytania o Remote Automation Environment.

## 📑 Kategorie

- [Ogólne](#ogólne)
- [Instalacja i Setup](#instalacja-i-setup)
- [Użytkowanie](#użytkowanie)
- [Ollama i AI](#ollama-i-ai)
- [VNC i Desktop](#vnc-i-desktop)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Zaawansowane](#zaawansowane)

---

## Ogólne

### Co to jest Remote Automation?

Remote Automation to system do automatyzacji kontroli aplikacji desktop przez zdalne połączenia (VNC/RDP/SPICE) z wykorzystaniem AI vision models. Pozwala pisać testy i scenariusze automatyzacji w prostym języku YAML, a AI znajduje elementy na ekranie.

### Czy to jest darmowe?

Tak! Projekt jest open-source (Apache Software License). Wszystkie komponenty są darmowe:
- Docker & Docker Compose (darmowe)
- Ollama (darmowe)
- Modele AI (darmowe, uruchamiane lokalnie)

### Do czego mogę to użyć?

- ✅ Automatyczne testowanie UI aplikacji
- ✅ Monitoring i health checks
- ✅ Web scraping z AI
- ✅ RPA (Robotic Process Automation)
- ✅ Accessibility testing
- ✅ Zadania repetytywne
- ✅ Screenshot analysis

### Czy potrzebuję umiejętności programowania?

**Podstawowe użycie:** NIE - możesz pisać scenariusze w YAML
```yaml
- action: find_and_click
  element: "Login button"
```

**Zaawansowane:** TAK - dla custom logic możesz użyć Python

### Czy dane są bezpieczne?

TAK! Wszystko działa lokalnie:
- Screenshots nie opuszczają Twojego komputera
- AI models działają lokalnie (nie w cloud)
- Żadne dane nie są wysyłane do external APIs

---

## Instalacja i Setup

### Jakie są wymagania systemowe?

**Minimum:**
- 4GB RAM wolnego
- 10GB miejsca na dysku
- 2 CPU cores
- Docker & Docker Compose

**Rekomendowane:**
- 8GB RAM wolnego
- 20GB miejsca (SSD)
- 4 CPU cores

### Czy działa na Windows?

TAK, przez WSL2 (Windows Subsystem for Linux). Zobacz [INSTALL.md](INSTALL.md#windows-wsl2).

### Czy działa na macOS?

TAK, zarówno na Intel jak i Apple Silicon (M1/M2/M3). Zobacz [INSTALL.md](INSTALL.md#macos).

### Jak długo trwa instalacja?

- Setup: ~2 minuty
- Docker build: ~5-10 minut (pierwsze uruchomienie)
- Model download: ~5-10 minut (llava:7b, 4.5GB)

**Łącznie:** 15-25 minut za pierwszym razem

### Czy mogę użyć bez Dockera?

Teoretycznie tak, ale **nie rekomendujemy**. Docker zapewnia:
- Izolację środowiska
- Łatwą instalację
- Reproducibility
- Cross-platform compatibility

### Otrzymuję błąd "no space left on device"

```bash
# Wyczyść stare obrazy Docker
docker system prune -a

# Sprawdź miejsce
docker system df

# Zobacz czy masz 20GB wolnego
df -h
```

---

## Użytkowanie

### Jak napisać pierwszy scenariusz?

1. Utwórz plik `my_test.yaml`:
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
  my_first_test:
    - action: connect
    - action: find_and_click
      element: "Firefox icon"
    - action: wait
      seconds: 3
    - action: verify
      expected: "Firefox is open"
    - action: disconnect
```

2. Uruchom:
```bash
docker-compose exec automation-controller \
  python3 automation_cli.py my_test.yaml --run my_first_test
```

### Jak działa `find_and_click`?

1. Przechwytuje screenshot ekranu
2. Wysyła do Ollama z opisem elementu
3. AI analizuje obraz i znajduje współrzędne
4. Klika na znalezionej pozycji

### Czy mogę użyć bez AI?

TAK! Możesz klikać na konkretnych współrzędnych:
```yaml
- action: click
  x: 100
  y: 200
```

Ale AI jest przydatne bo:
- Nie musisz znać dokładnych współrzędnych
- Działa przy różnych rozdzielczościach
- Adapts to UI changes

### Jak zapisać wyniki testu?

Wyniki są automatycznie zapisywane w `results/test_results.json`:
```json
{
  "summary": {
    "total": 5,
    "passed": 4,
    "failed": 1,
    "duration": 45.2
  },
  "tests": [...]
}
```

### Jak uruchomić wiele testów naraz?

```bash
# Pytest
pytest tests/

# Lub w YAML z wieloma scenariuszami
scenarios:
  test1: [...]
  test2: [...]
  test3: [...]

# Uruchom wszystkie
for scenario in test1 test2 test3; do
  python3 automation_cli.py scenarios.yaml --run $scenario
done
```

---

## Ollama i AI

### Który model AI powinienem użyć?

**Development/testing:** `moondream` (1.7GB, szybki)
**Production:** `llava:7b` (4.5GB, balanced)
**High accuracy:** `llava:13b` (8GB, wolniejszy ale dokładniejszy)

```bash
# Zmień model
docker exec automation-ollama ollama pull moondream
```

### Dlaczego AI jest wolne?

AI inference zajmuje czas:
- moondream: ~3 sekundy
- llava:7b: ~5 sekund
- llava:13b: ~12 sekund

**Optymalizacje:**
- Użyj lżejszego modelu
- Resize screenshots (800x600)
- Batch multiple requests
- Keep model loaded (warm cache)

### Czy mogę użyć OpenAI/Claude zamiast Ollama?

Obecnie nie ma natywnej integracji, ale możesz:
1. Fork projektu
2. Modify `OllamaVision` class
3. Add OpenAI/Anthropic API calls

**Dlaczego Ollama domyślnie?**
- Privacy (local inference)
- No API costs
- Offline capability

### Ollama timeout - co robić?

```python
# Zwiększ timeout w remote_automation.py
response = requests.post(
    ...,
    timeout=300  # z 120 do 300
)

# Lub użyj mniejszego modelu
```

### AI nie znajduje elementów - dlaczego?

**Możliwe przyczyny:**
1. Element nie jest widoczny (scroll, hidden)
2. Niewystarczająco precyzyjny opis
3. Zbyt niska rozdzielczość
4. Desktop się nie załadował

**Rozwiązania:**
```yaml
# Bardziej precyzyjny opis
element: "Blue Submit button in bottom right corner with white text"

# Dodaj więcej czasu
- action: wait
  seconds: 5

# Sprawdź screenshot
python3 -c "
from remote_automation import RemoteController
c = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
c.connect()
screen = c.capture_screen()
screen.save('debug.png')
"
```

---

## VNC i Desktop

### Jak otworzyć VNC w przeglądarce?

http://localhost:6080/vnc.html

(Hasło: `automation`)

### VNC jest wolne/laguje

**Rozwiązania:**
```yaml
# 1. Zmniejsz rozdzielczość
VNC_GEOMETRY=1024x768

# 2. Zmniejsz głębię kolorów
VNC_DEPTH=16

# 3. Zwiększ RAM dla VNC
services:
  vnc-desktop:
    mem_limit: 4g
```

### Czarny ekran w noVNC

```bash
# Poczekaj 30 sekund (desktop startuje)

# Sprawdź logi
make logs-vnc

# Restart VNC
docker-compose restart vnc-desktop

# Sprawdź proces
docker exec automation-vnc pgrep Xvnc
```

### Czy mogę zmienić rozdzielczość?

TAK:
```yaml
# docker-compose.yml
environment:
  - VNC_GEOMETRY=1920x1080  # Zmień tutaj
```

### Jak skopiować pliki do VNC Desktop?

```bash
# Do współdzielonego folderu
cp myfile.txt shared/

# Będzie widoczne w:
# /home/automation/shared/myfile.txt
```

### Czy mogę zainstalować więcej aplikacji w VNC?

TAK:
```bash
# Wejdź do kontenera
docker exec -it automation-vnc bash

# Zainstaluj (jako root)
sudo apt-get update
sudo apt-get install <package>

# Lub dodaj do Dockerfile i rebuild
```

---

## Performance

### Jak przyspieszyć testy?

1. **Użyj lżejszego modelu**
```bash
docker exec automation-ollama ollama pull moondream
```

2. **Zmniejsz rozdzielczość**
```yaml
VNC_GEOMETRY=1024x768
```

3. **Zwiększ zasoby Docker**
```
Settings → Resources
RAM: 8GB
CPU: 4 cores
```

4. **Reuse connections**
```python
# Nie disconnectuj między testami
controller.connect()
# test 1
# test 2
# test 3
controller.disconnect()
```

### Czy mogę uruchomić testy równolegle?

NIE w jednym kontenerze (VNC jest single-user).

TAK z wieloma kontenerami:
```bash
# Instance 1
COMPOSE_PROJECT_NAME=auto1 docker-compose up -d

# Instance 2 (zmień porty w docker-compose.yml)
COMPOSE_PROJECT_NAME=auto2 docker-compose up -d
```

### Ile RAM potrzebuje?

**Minimalne zużycie:**
- VNC Desktop: 1GB
- Ollama (moondream): 2GB
- Controller: 512MB
- **Total:** ~3.5-4GB

**Rekomendowane:**
- VNC Desktop: 2GB
- Ollama (llava:7b): 4GB
- Controller: 1GB
- **Total:** ~7-8GB

### Dysk zapełnia się - dlaczego?

```bash
# Sprawdź zużycie Docker
docker system df

# Obrazy: ~5GB (VNC + Ollama)
# Volumes: ~5GB (modele AI)
# Build cache: varies

# Wyczyść
make clean
docker system prune -a
```

---

## Troubleshooting

### "Cannot connect to Docker daemon"

```bash
# Linux: Start Docker
sudo systemctl start docker

# Mac/Windows: Uruchom Docker Desktop
# Sprawdź ikonę w system tray
```

### Kontenery się restartują

```bash
# Zobacz logi
make logs

# Najczęstsze przyczyny:
# 1. Za mało RAM → zwiększ w Docker Desktop
# 2. Port zajęty → zmień port lub zabij proces
# 3. Błąd w konfiguracji → sprawdź docker-compose.yml
```

### Test failed ale nie wiem dlaczego

```bash
# 1. Zobacz szczegółowe logi
docker-compose exec automation-controller \
  python3 automation_cli.py test.yaml --run test -v

# 2. Zapisz screenshot
# Dodaj do scenariusza:
- action: analyze
  question: "What do you see? Describe everything."
  save_to: debug_info

# 3. Sprawdź wyniki
cat results/test_results.json
```

### Ollama nie odpowiada

```bash
# Sprawdź status
docker ps | grep ollama

# Sprawdź logi
make logs-ollama

# Test API
curl http://localhost:11434/api/tags

# Restart
docker-compose restart ollama
```

### Port already in use

```bash
# Znajdź proces
sudo lsof -i :5901

# Zabij proces
sudo kill -9 <PID>

# Lub zmień port w docker-compose.yml
```

---

## Zaawansowane

### Czy mogę użyć z CI/CD?

TAK! Zobacz [EXAMPLES.md](EXAMPLES.md#cicd-integration) dla:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps

### Jak zintegrować z Slack/Discord?

Zobacz [EXAMPLES.md](EXAMPLES.md#slackdiscord-notifications)

```python
import requests

def send_slack(message):
    requests.post(WEBHOOK_URL, json={'text': message})

# W testach
if test_failed:
    send_slack(f"❌ Test {name} failed!")
```

### Czy mogę używać GPU?

TAK, dla Ollama:
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

Wymaga: nvidia-docker

### Jak zapisać stan kontenera?

```bash
# Commit container do image
docker commit automation-vnc my-custom-vnc:v1

# Użyj w docker-compose.yml
services:
  vnc-desktop:
    image: my-custom-vnc:v1
```

### Czy mogę deployować do cloud?

TAK:
- AWS ECS/Fargate
- Azure Container Instances
- Google Cloud Run
- DigitalOcean App Platform

**Uwaga:** Potrzebujesz ~8GB RAM instance

### Jak dodać własne protokoły (RDP/SPICE)?

1. Extend `RemoteController` class
2. Implement protocol-specific methods
3. Add to `_connect_rdp()` / `_connect_spice()`

Zobacz kod w `remote_automation.py` dla przykładu.

### Czy mogę użyć innych desktop environments?

TAK! Zmodyfikuj Dockerfile:
```dockerfile
# LXDE (lżejsze)
RUN apt-get install -y lxde

# KDE (bardziej feature-rich)
RUN apt-get install -y kde-plasma-desktop

# Openbox (minimalne)
RUN apt-get install -y openbox
```

### Jak zrobić backup całego środowiska?

```bash
# Backup volumes
make backup-results

# Backup containers
docker commit automation-vnc vnc-backup:latest
docker commit automation-ollama ollama-backup:latest

# Backup configuration
tar czf config-backup.tar.gz *.yml *.yaml .env
```

---

## Inne pytania?

**Dokumentacja:**
- [README.md](README.md) - Overview
- [QUICK_START.md](QUICK_START.md) - Getting started
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

**Community:**
- GitHub Issues - zgłoś bug
- GitHub Discussions - zadaj pytanie
- Discord - real-time chat

**Nie znalazłeś odpowiedzi?**
[Otwórz issue na GitHub](https://github.com/your-repo/issues/new)
