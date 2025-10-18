# ⚡ Performance Optimization Guide

Przewodnik optymalizacji wydajności Remote Automation Environment.

## 📑 Spis treści

- [Quick Wins](#quick-wins)
- [Optymalizacja Docker](#optymalizacja-docker)
- [Optymalizacja VNC](#optymalizacja-vnc)
- [Optymalizacja Ollama](#optymalizacja-ollama)
- [Optymalizacja testów](#optymalizacja-testów)
- [Monitoring wydajności](#monitoring-wydajności)
- [Benchmarki](#benchmarki)

---

## Quick Wins

### Top 5 najszybszych ulepszeń

```bash
# 1. Użyj lżejszego modelu AI (największy wpływ)
docker exec automation-ollama ollama pull moondream
# llava:7b (4.5GB) → moondream (1.7GB)
# Czas odpowiedzi: -60%

# 2. Zmniejsz rozdzielczość VNC
# W docker-compose.yml:
VNC_GEOMETRY=1024x768  # zamiast 1280x800
# Użycie CPU: -30%, responsywność: +40%

# 3. Ogranicz równoczesne procesy Ollama
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
# Użycie RAM: -50%

# 4. Zwiększ zasoby Docker Desktop
# RAM: 8GB, CPU: 4 cores
# Ogólna szybkość: +100%

# 5. Użyj SSD zamiast HDD
# Czas buildu: -70%, I/O: +400%
```

### Szybki benchmark

```bash
# Przed optymalizacją
time make test

# Po optymalizacji
time make test

# Porównaj wyniki
```

---

## Optymalizacja Docker

### Zasoby Docker Desktop

**Minimum dla płynnej pracy:**
```
Memory: 8GB
CPUs: 4
Disk: 30GB SSD
Swap: 2GB
```

**Konfiguracja:**
1. Docker Desktop → Settings → Resources → Advanced
2. Ustaw wartości
3. Apply & Restart

### Docker Build Cache

```bash
# Wykorzystaj BuildKit (szybsze buildy)
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build z cache
docker-compose build

# Force rebuild bez cache (rzadko)
docker-compose build --no-cache
```

### Optymalizacja obrazów

**W Dockerfile:**

```dockerfile
# ✅ DOBRE: Layer caching
FROM ubuntu:22.04

# Zainstaluj pakiety w jednym layerze
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ❌ ZŁE: Wiele layerów
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
```

### Limity zasobów

**docker-compose.yml:**

```yaml
services:
  vnc-desktop:
    mem_limit: 2g
    mem_reservation: 1g
    cpus: 2
    
  ollama:
    mem_limit: 4g
    mem_reservation: 2g
    cpus: 4
```

### Volumes Performance

```yaml
# ✅ DOBRE: Delegated dla lepszej wydajności (Mac/Windows)
volumes:
  - ./automation:/app:delegated

# ✅ DOBRE: Cached dla read-only
volumes:
  - ./test_scenarios:/app/scenarios:cached
```

---

## Optymalizacja VNC

### Rozdzielczość i kolory

**Najszybsze ustawienia:**

```yaml
environment:
  - VNC_GEOMETRY=1024x768    # Najmniejsza użyteczna
  - VNC_DEPTH=16             # 16-bit color (vs 24-bit)
```

**Porównanie:**

| Ustawienie | CPU | Bandwidth | Latencja |
|------------|-----|-----------|----------|
| 1920x1080@24bit | 100% | 100% | Wysoka |
| 1280x800@24bit | 55% | 55% | Średnia |
| 1024x768@16bit | 30% | 30% | Niska |

### Kompresja VNC

**W xstartup:**

```bash
# ~/.vnc/xstartup
vncconfig -iconic &
xcompmgr -c &  # Wyłącz compositioning dla szybszości
exec startxfce4
```

### Desktop Environment

**Lżejsze alternatywy:**

```dockerfile
# XFCE (obecnie używane) - balans
RUN apt-get install -y xfce4

# LXDE (najlżejsze) - najszybsze
RUN apt-get install -y lxde

# Openbox (minimalne) - dla zaawansowanych
RUN apt-get install -y openbox
```

**Porównanie RAM:**
- XFCE: ~300MB
- LXDE: ~150MB
- Openbox: ~50MB

### VNC vs noVNC

```
Native VNC client:
- Latencja: ~10-20ms
- CPU: 5-10%
- Smooth

noVNC (browser):
- Latencja: ~50-100ms
- CPU: 15-25%
- Więcej stuttering
```

**Rekomendacja:** Dla codziennej pracy użyj natywnego VNC client.

---

## Optymalizacja Ollama

### Wybór modelu

**Porównanie modeli:**

| Model | Rozmiar | RAM | Szybkość | Jakość |
|-------|---------|-----|----------|---------|
| moondream | 1.7GB | 3GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ |
| llava:7b | 4.5GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| bakllava | 5GB | 8GB | ⚡⚡⭐ | ⭐⭐⭐⭐ |
| llava:13b | 8GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |

**Rekomendacje:**
- **Development:** moondream
- **Production:** llava:7b
- **Accuracy-critical:** llava:13b (jeśli masz RAM)

### Ollama Configuration

**docker-compose.yml:**

```yaml
ollama:
  environment:
    # Podstawowa optymalizacja
    - OLLAMA_NUM_PARALLEL=1          # Jeden request na raz
    - OLLAMA_MAX_LOADED_MODELS=1     # Jeden model w RAM
    - OLLAMA_NUM_CTX=2048            # Mniejszy context (vs 4096)
    
    # Zaawansowana
    - OLLAMA_NUM_GPU=0               # Wyłącz GPU jeśli wolne
    - OLLAMA_FLASH_ATTENTION=1       # Szybsze attention (jeśli działa)
    
  mem_limit: 4g
  memswap_limit: 4g
```

### Prompt Optimization

```python
# ❌ ZŁE: Długi prompt
prompt = """
Please carefully analyze this screenshot and provide 
a detailed description of every element you can see, 
including colors, positions, text content, and any 
other relevant information. Be as thorough as possible.
"""

# ✅ DOBRE: Krótki, precyzyjny
prompt = "Describe the main heading and primary button on screen."

# Czas odpowiedzi: 10s → 2s
```

### Image Optimization

```python
# Zmniejsz rozmiar obrazu przed wysłaniem do Ollama
screen = controller.capture_screen()

# ✅ Resize dla szybszości
screen = screen.resize((800, 600))  # z 1280x800

# ✅ Compress
screen.save('temp.jpg', quality=85)  # zamiast PNG

# Czas procesowania: -60%
```

### Batch Processing

```python
# ❌ ZŁE: Wiele requestów
for element in elements:
    result = vision.find_element(screen, element)

# ✅ DOBRE: Jeden request
prompt = f"Find these elements: {', '.join(elements)}"
result = vision.analyze_screen(screen, prompt)

# Czas: 5 requestów * 3s = 15s → 1 request * 5s = 5s
```

---

## Optymalizacja testów

### Parallel Testing

```python
# test_runner.py
from concurrent.futures import ThreadPoolExecutor

def run_tests_parallel(scenarios, max_workers=3):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_scenario, s) for s in scenarios]
        results = [f.result() for f in futures]
    return results

# Czas: 10 testów * 30s = 300s → 100s (3 workers)
```

### Inteligentne czekanie

```yaml
# ❌ ZŁE: Fixed waits
- action: wait
  seconds: 5  # Zawsze czeka 5s

# ✅ DOBRE: Wait until ready
- action: wait_until
  condition: "element is visible"
  timeout: 10
  poll_interval: 0.5
```

### Reuse connections

```python
# ❌ ZŁE: Nowe połączenie dla każdego testu
def test_scenario_1():
    controller = RemoteController(...)
    controller.connect()
    # test
    controller.disconnect()

# ✅ DOBRE: Reuse connection
@pytest.fixture(scope="session")
def controller():
    c = RemoteController(...)
    c.connect()
    yield c
    c.disconnect()
```

### Checkpoint system

```python
# Zapisz stan po długich operacjach
checkpoints = {
    'firefox_opened': False,
    'logged_in': False,
}

if not checkpoints['firefox_opened']:
    # Otwórz Firefox (wolne)
    checkpoints['firefox_opened'] = True
else:
    # Skip (szybko)
    pass
```

---

## Monitoring wydajności

### Real-time monitoring

```bash
# CPU i RAM per kontener
docker stats

# Monitoring dashboard
python3 monitor.py

# System resources
htop
```

### Profiling

```python
# Profile Python code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
engine.execute_dsl(script)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Metrics collection

```python
# metrics.py
import time
from datetime import datetime

class Metrics:
    def __init__(self):
        self.timings = []
    
    def record(self, action, duration):
        self.timings.append({
            'action': action,
            'duration': duration,
            'timestamp': datetime.now()
        })
    
    def report(self):
        avg_by_action = {}
        for t in self.timings:
            action = t['action']
            if action not in avg_by_action:
                avg_by_action[action] = []
            avg_by_action[action].append(t['duration'])
        
        for action, durations in avg_by_action.items():
            avg = sum(durations) / len(durations)
            print(f"{action}: avg {avg:.2f}s")

# Usage
metrics = Metrics()

start = time.time()
action()
metrics.record('action_name', time.time() - start)
```

---

## Benchmarki

### Baseline Performance

**Test system:**
- CPU: 4 cores @ 3.0GHz
- RAM: 16GB
- Disk: SSD
- Docker: 8GB RAM, 4 CPUs

**Results:**

```
Operation                  | Time    | Notes
---------------------------|---------|------------------
Docker compose up          | 45s     | First time: 5min
VNC connection             | 2s      |
Ollama model load (llava)  | 8s      |
Ollama inference (simple)  | 3s      | "What do you see?"
Ollama inference (complex) | 12s     | Detailed analysis
Screenshot capture         | 0.5s    |
Find element (AI)          | 5s      | Including inference
Click action               | 0.2s    |
Type text (10 chars)       | 0.5s    |
Full test scenario         | 30s     | 10 actions
```

### Optimization Targets

**Achievable improvements:**

```
Configuration            | Time savings
-------------------------|------------------
Use moondream           | -60% AI time
Reduce VNC resolution   | -30% VNC lag
Batch AI requests       | -70% multi-query
Parallel tests (3x)     | -66% total time
SSD vs HDD             | -70% I/O time
```

### Stress test

```bash
# Test concurrent tests
for i in {1..5}; do
    docker-compose exec automation-controller \
        python3 automation_cli.py test.yaml --run test &
done
wait

# Measure system load
docker stats --no-stream
```

---

## Production Recommendations

### Minimal Setup (Budget)

```yaml
# Low-end laptop (8GB RAM, 2 cores)
VNC_GEOMETRY=1024x768
VNC_DEPTH=16
OLLAMA_MODEL=moondream
OLLAMA_NUM_CTX=2048

mem_limits:
  vnc: 1.5g
  ollama: 3g
  controller: 512m
```

**Expected:** 3-5 tests/minute

### Balanced Setup (Recommended)

```yaml
# Desktop (16GB RAM, 4 cores)
VNC_GEOMETRY=1280x800
VNC_DEPTH=24
OLLAMA_MODEL=llava:7b
OLLAMA_NUM_CTX=2048

mem_limits:
  vnc: 2g
  ollama: 4g
  controller: 1g
```

**Expected:** 5-10 tests/minute

### High-Performance Setup

```yaml
# Workstation (32GB RAM, 8 cores, GPU)
VNC_GEOMETRY=1920x1080
VNC_DEPTH=24
OLLAMA_MODEL=llava:13b
OLLAMA_NUM_CTX=4096
ENABLE_GPU=true

mem_limits:
  vnc: 4g
  ollama: 8g
  controller: 2g
```

**Expected:** 10-15 tests/minute

---

## Checklist optymalizacji

```
□ Docker Desktop: 8GB RAM, 4 CPUs
□ Ollama: model moondream/llava:7b
□ VNC: rozdzielczość 1024x768
□ Tests: parallel execution
□ Images: resize przed wysłaniem do AI
□ Prompts: krótkie i precyzyjne
□ Connections: reuse zamiast reconnect
□ Monitoring: python3 monitor.py
□ Profiling: zidentyfikuj bottlenecki
□ Cache: Docker BuildKit enabled
```

---

**Pytania?** Zobacz [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
