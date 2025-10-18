# 🔧 Troubleshooting Guide

Kompleksowy przewodnik rozwiązywania problemów z Remote Automation.

## 📑 Spis treści

- [Szybka diagnostyka](#szybka-diagnostyka)
- [Problemy z Docker](#problemy-z-docker)
- [Problemy z VNC](#problemy-z-vnc)
- [Problemy z Ollama](#problemy-z-ollama)
- [Problemy z testami](#problemy-z-testami)
- [Problemy z wydajnością](#problemy-z-wydajnością)
- [Problemy sieciowe](#problemy-sieciowe)
- [FAQ](#faq)

---

## Szybka diagnostyka

### Uruchom automatyczną diagnostykę

```bash
# Sprawdź wszystko
make check-docker
make status
python3 run_tests.py --wait

# Monitoring w czasie rzeczywistym
python3 monitor.py
```

### Sprawdź logi

```bash
# Wszystkie logi
make logs

# Konkretny serwis
make logs-vnc
make logs-ollama
make logs-controller

# Ostatnie 50 linii
docker-compose logs --tail=50 vnc-desktop
```

---

## Problemy z Docker

### Problem: "Cannot connect to Docker daemon"

**Objawy:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Rozwiązania:**

```bash
# Linux: Sprawdź czy Docker działa
sudo systemctl status docker

# Jeśli nie działa, uruchom
sudo systemctl start docker
sudo systemctl enable docker

# Sprawdź uprawnienia
sudo usermod -aG docker $USER
newgrp docker

# macOS/Windows: Uruchom Docker Desktop
# Sprawdź czy ikona Docker jest aktywna w system tray
```

### Problem: "No space left on device"

**Objawy:**
```
ERROR: failed to solve: write /var/lib/docker/tmp/...: no space left on device
```

**Rozwiązania:**

```bash
# Sprawdź zużycie
docker system df

# Wyczyść nieużywane zasoby
docker system prune -a -f

# Usuń tylko kontenery
docker container prune -f

# Usuń tylko obrazy
docker image prune -a -f

# Wyczyść volumes (UWAGA: usuwa dane!)
docker volume prune -f

# Sprawdź miejsce na dysku
df -h
```

### Problem: "Port already in use"

**Objawy:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:5901: bind: address already in use
```

**Rozwiązania:**

```bash
# Znajdź proces używający portu (Linux/Mac)
sudo lsof -i :5901
sudo lsof -i :6080
sudo lsof -i :11434

# Zabij proces
sudo kill -9 <PID>

# Lub zmień port w docker-compose.yml
ports:
  - "5902:5901"  # Zmień 5901 na 5902
```

### Problem: Kontenery się restartują

**Objawy:**
```
docker-compose ps
# Container status: Restarting
```

**Rozwiązania:**

```bash
# Zobacz logi aby zrozumieć dlaczego
docker-compose logs <container-name>

# Najczęstsze przyczyny:
# 1. Za mało RAM
# 2. Błąd w konfiguracji
# 3. Brakujący wolumen

# Zwiększ limity w docker-compose.yml:
services:
  vnc-desktop:
    mem_limit: 4g
```

---

## Problemy z VNC

### Problem: VNC nie odpowiada na porcie 5901

**Objawy:**
```bash
nc -zv localhost 5901
# Connection refused
```

**Rozwiązania:**

```bash
# 1. Sprawdź czy kontener działa
docker ps | grep vnc

# 2. Zobacz logi VNC
make logs-vnc

# 3. Sprawdź proces VNC w kontenerze
docker exec automation-vnc pgrep Xvnc

# 4. Restart kontenera
docker-compose restart vnc-desktop

# 5. Jeśli nadal nie działa, rebuild
make down
make build
make up
```

### Problem: noVNC pokazuje czarny ekran

**Rozwiązania:**

```bash
# 1. Poczekaj 30 sekund (może się jeszcze uruchamiać)

# 2. Sprawdź logi
docker-compose logs vnc-desktop | grep -i error

# 3. Połącz się bezpośrednio przez VNC client
vncviewer localhost:5901
# Hasło: automation

# 4. Sprawdź czy X server działa
docker exec automation-vnc ps aux | grep X

# 5. Restart X server
docker exec automation-vnc vncserver -kill :1
docker exec automation-vnc vncserver :1
```

### Problem: Błędne hasło VNC

**Rozwiązania:**

```bash
# 1. Sprawdź hasło w docker-compose.yml
grep VNC_PASSWORD docker-compose.yml

# 2. Resetuj hasło w kontenerze
docker exec -it automation-vnc bash
echo "automation" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd
exit

# 3. Restart VNC
docker-compose restart vnc-desktop
```

### Problem: VNC laguje lub jest wolne

**Rozwiązania:**

```bash
# 1. Zmniejsz rozdzielczość w docker-compose.yml
VNC_GEOMETRY=1024x768  # zamiast 1280x800

# 2. Zmniejsz głębię kolorów
VNC_DEPTH=16  # zamiast 24

# 3. Zwiększ RAM dla kontenera
mem_limit: 4g

# 4. Użyj natywnego VNC client zamiast noVNC
vncviewer localhost:5901
```

---

## Problemy z Ollama

### Problem: Ollama nie pobiera modelu

**Objawy:**
```
Error: failed to pull model
```

**Rozwiązania:**

```bash
# 1. Sprawdź logi
make logs-ollama

# 2. Sprawdź połączenie internetowe
docker exec automation-ollama ping -c 3 ollama.ai

# 3. Ręcznie pobierz model
docker exec automation-ollama ollama pull llava:7b

# 4. Sprawdź miejsce na dysku
docker exec automation-ollama df -h

# 5. Jeśli brak miejsca, wyczyść stare modele
docker exec automation-ollama ollama rm <stary-model>

# 6. Lista modeli
docker exec automation-ollama ollama list
```

### Problem: Ollama API nie odpowiada

**Objawy:**
```bash
curl http://localhost:11434/api/tags
# Connection refused
```

**Rozwiązania:**

```bash
# 1. Sprawdź czy kontener działa
docker ps | grep ollama

# 2. Sprawdź logi
make logs-ollama

# 3. Sprawdź proces w kontenerze
docker exec automation-ollama pgrep ollama

# 4. Restart usługi
docker-compose restart ollama

# 5. Sprawdź czy Ollama się uruchomił
docker exec automation-ollama curl http://localhost:11434/api/tags
```

### Problem: Ollama timeout przy dużych promptach

**Objawy:**
```
timeout: no read activity in 120s
```

**Rozwiązania:**

```python
# W remote_automation.py zwiększ timeout:
response = requests.post(
    f"{self.base_url}/api/generate",
    json=payload,
    timeout=300  # Zwiększ z 120 do 300
)
```

Lub użyj mniejszego modelu:
```bash
docker exec automation-ollama ollama pull moondream
```

### Problem: Ollama zużywa za dużo RAM

**Rozwiązania:**

```bash
# 1. Użyj mniejszego modelu
# llava:7b (4.5GB) → moondream (1.7GB)
docker exec automation-ollama ollama pull moondream

# 2. Ogranicz liczbę równoczesnych requestów
# W docker-compose.yml:
environment:
  - OLLAMA_NUM_PARALLEL=1
  - OLLAMA_MAX_LOADED_MODELS=1

# 3. Zmniejsz context window
environment:
  - OLLAMA_NUM_CTX=2048  # zamiast 4096
```

---

## Problemy z testami

### Problem: Testy nie mogą połączyć się z VNC

**Objawy:**
```
Error: Could not connect to vnc-desktop:5901
```

**Rozwiązania:**

```bash
# 1. Upewnij się że kontenery są w tej samej sieci
docker network ls
docker network inspect automation-net

# 2. Sprawdź czy VNC działa
make status

# 3. Poczekaj dłużej po starcie
sleep 60 && make test

# 4. Test połączenia z kontenera controller
docker exec automation-controller nc -zv vnc-desktop 5901
```

### Problem: AI nie znajduje elementów na ekranie

**Objawy:**
```
Element not found: Firefox icon
```

**Rozwiązania:**

```bash
# 1. Sprawdź czy desktop się w pełni załadował
# Otwórz http://localhost:6080 i zobacz czy widać pulpit

# 2. Zwiększ czas oczekiwania w scenariuszu
- action: wait
  seconds: 5  # zamiast 2

# 3. Użyj dokładniejszego opisu
element: "Firefox web browser icon on the desktop with orange fox logo"

# 4. Zapisz screenshot do debugowania
python3 -c "
from remote_automation import RemoteController
c = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
c.connect()
screen = c.capture_screen()
screen.save('debug.png')
c.disconnect()
"
```

### Problem: Testy są niestabilne

**Rozwiązania:**

```yaml
# Dodaj więcej waits i verify:
- action: wait
  seconds: 2

- action: verify
  expected: "element is visible"

- action: wait
  seconds: 1

- action: find_and_click
  element: "button"
```

---

## Problemy z wydajnością

### Problem: Środowisko działa bardzo wolno

**Diagnostyka:**

```bash
# Sprawdź zasoby
docker stats

# Sprawdź obciążenie hosta
top
htop
```

**Rozwiązania:**

```bash
# 1. Zwiększ zasoby Docker Desktop
# Settings → Resources:
# - RAM: 8GB
# - CPUs: 4
# - Disk: 30GB

# 2. Zamknij inne aplikacje

# 3. Użyj lżejszego modelu
make pull-model-small

# 4. Zmniejsz rozdzielczość VNC
VNC_GEOMETRY=1024x768

# 5. Ogranicz równoczesne procesy
OLLAMA_NUM_PARALLEL=1
```

### Problem: Długi czas buildowania

**Rozwiązania:**

```bash
# 1. Użyj cache podczas buildu
docker-compose build --no-cache  # tylko gdy koniecznie

# 2. Zwiększ Docker build memory
# Docker Desktop → Settings → Resources

# 3. Sprawdź połączenie internetowe (download apt packages)
```

---

## Problemy sieciowe

### Problem: Nie można połączyć się z localhost

**Windows/WSL2 specyficzny problem:**

```bash
# Z WSL2 użyj:
http://localhost:6080

# Z Windows użyj IP WSL2:
wsl hostname -I
# Następnie: http://<WSL2-IP>:6080
```

### Problem: Kontenery nie widzą się nawzajem

**Rozwiązania:**

```bash
# 1. Sprawdź network
docker network ls
docker network inspect automation-net

# 2. Ping test
docker exec automation-controller ping vnc-desktop
docker exec automation-controller ping ollama

# 3. Recreate network
docker-compose down
docker network rm automation-net
docker-compose up -d
```

---

## FAQ

### Q: Czy mogę użyć GPU dla Ollama?

**A:** Tak, jeśli masz nvidia-docker:

```yaml
# docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Q: Jak zmienić keyboard layout w VNC?

**A:** W kontenerze VNC:

```bash
docker exec -it automation-vnc bash
setxkbmap pl  # dla polskiego
setxkbmap us  # dla amerykańskiego
```

### Q: Czy mogę uruchomić wiele instancji?

**A:** Tak, użyj różnych portów:

```bash
# Skopiuj projekt
cp -r remote-automation remote-automation-2

# Zmień porty w docker-compose.yml
ports:
  - "5902:5901"  # VNC
  - "6081:6080"  # noVNC
  - "11435:11434"  # Ollama

# Zmień project name
COMPOSE_PROJECT_NAME=automation-2 docker-compose up -d
```

### Q: Jak zapisać stan środowiska?

**A:** Użyj Docker commit lub volumes:

```bash
# Commit kontenera
docker commit automation-vnc my-custom-vnc:v1

# Backup volumes
docker run --rm -v ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz /data
```

### Q: Czy mogę użyć innego Desktop Environment?

**A:** Tak, zmodyfikuj Dockerfile:

```dockerfile
# Zamiast XFCE, użyj LXDE (lżejsze)
RUN apt-get install -y lxde
```

---

## Zgłaszanie błędów

Jeśli problem nie został rozwiązany:

1. **Zbierz informacje:**
```bash
# System info
uname -a
docker --version
docker-compose --version

# Logi
make logs > logs.txt

# Stats
docker stats --no-stream > stats.txt

# Config
docker-compose config > config.txt
```

2. **Uruchom diagnostykę:**
```bash
python3 run_tests.py > test-results.txt
```

3. **Dołącz pliki** i opis problemu

---

## Przydatne komendy diagnostyczne

```bash
# Pełna diagnostyka
make check-docker
make status
python3 monitor.py --once

# Restart wszystkiego
make restart

# Pełny reset
make clean-all
make build
make up

# Debug konkretnego kontenera
docker exec -it <container> /bin/bash
```

---

**Ciągle masz problemy?** Sprawdź [INSTALL.md](INSTALL.md) i [QUICK_START.md](QUICK_START.md)
