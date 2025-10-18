# 🏗️ Architecture Documentation

Szczegółowa dokumentacja architektury Remote Automation Environment.

## 📑 Spis treści

- [Przegląd](#przegląd)
- [Komponenty systemu](#komponenty-systemu)
- [Przepływ danych](#przepływ-danych)
- [Protokoły komunikacji](#protokoły-komunikacji)
- [Decyzje architektoniczne](#decyzje-architektoniczne)

---

## Przegląd

Remote Automation Environment to system do automatyzacji kontroli aplikacji desktop przez zdalne połączenia z wykorzystaniem AI vision.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Host Machine                         │
│                                                               │
│  ┌────────────┐      ┌──────────────┐      ┌─────────────┐ │
│  │   User     │─────▶│  Make/CLI    │─────▶│   Docker    │ │
│  │ Interface  │      │   Commands   │      │  Compose    │ │
│  └────────────┘      └──────────────┘      └──────┬──────┘ │
│                                                     │         │
└─────────────────────────────────────────────────────┼─────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────┐
                    │         Docker Network          │         │
                    │                                 ▼         │
                    │  ┌──────────────────────────────────────┐ │
                    │  │      VNC Desktop Container            │ │
                    │  │  ┌─────────────────────────────────┐ │ │
                    │  │  │  Ubuntu 22.04 + XFCE Desktop    │ │ │
                    │  │  │  - TigerVNC Server (:5901)      │ │ │
                    │  │  │  - noVNC WebSocket (:6080)      │ │ │
                    │  │  │  - Firefox, Terminal, etc.      │ │ │
                    │  │  └─────────────────────────────────┘ │ │
                    │  └──────────────┬───────────────────────┘ │
                    │                 │ VNC Protocol             │
                    │                 ▼                          │
                    │  ┌──────────────────────────────────────┐ │
                    │  │    Automation Controller Container    │ │
                    │  │  ┌─────────────────────────────────┐ │ │
                    │  │  │  - Python Runtime               │ │ │
                    │  │  │  - remote_automation.py         │ │ │
                    │  │  │  - automation_cli.py            │ │ │
                    │  │  │  - Test Scenarios (YAML)        │ │ │
                    │  │  └─────────────────────────────────┘ │ │
                    │  └──────────────┬───────────────────────┘ │
                    │                 │ HTTP API                 │
                    │                 ▼                          │
                    │  ┌──────────────────────────────────────┐ │
                    │  │       Ollama Container                │ │
                    │  │  ┌─────────────────────────────────┐ │ │
                    │  │  │  - Ollama Server (:11434)       │ │ │
                    │  │  │  - AI Vision Models             │ │ │
                    │  │  │    (llava, moondream, etc.)     │ │ │
                    │  │  └─────────────────────────────────┘ │ │
                    │  └──────────────────────────────────────┘ │
                    │                                            │
                    └────────────────────────────────────────────┘
```

---

## Komponenty systemu

### 1. VNC Desktop Container

**Technologie:**
- Base: Ubuntu 22.04
- Desktop: XFCE4
- VNC Server: TigerVNC
- WebSocket Proxy: noVNC

**Odpowiedzialności:**
- Dostarczanie środowiska desktop w kontenerze
- Obsługa połączeń VNC (natywnych i WebSocket)
- Uruchamianie aplikacji (Firefox, Terminal, etc.)
- Rendering interfejsu graficznego

**Porty:**
- `5901` - TigerVNC Server (native protocol)
- `6080` - noVNC WebSocket proxy

**Volumes:**
```yaml
volumes:
  - ./shared:/home/automation/shared  # Pliki współdzielone
```

**Konfiguracja:**
```
Display: :1
Resolution: 1280x800 (configurable)
Color Depth: 24-bit (configurable)
User: automation (UID 1000)
```

### 2. Automation Controller Container

**Technologie:**
- Base: Python 3.11-slim
- Libraries: Pillow, requests, pynput, vncdotool, PyYAML

**Odpowiedzialności:**
- Wykonywanie scenariuszy automatyzacji
- Kontrola VNC Desktop (klawiatura, mysz)
- Przechwytywanie screenshotów
- Komunikacja z Ollama API
- Zarządzanie testami

**Główne moduły:**

```python
RemoteController
├── connect()              # Nawiązuje połączenie VNC/RDP/SPICE
├── click(x, y)           # Symuluje kliknięcie myszy
├── type_text(text)       # Symuluje pisanie na klawiaturze
├── key_press(key)        # Symuluje naciśnięcie klawisza
├── capture_screen()      # Przechwytuje screenshot
└── disconnect()          # Zamyka połączenie

OllamaVision
├── analyze_screen(image, prompt)  # Analizuje screenshot
├── find_element(image, desc)      # Znajduje element na ekranie
└── encode_image(image)            # Konwertuje obraz do base64

AutomationEngine
├── execute_dsl(script)   # Wykonuje scenariusz DSL
└── variables             # Przechowuje wyniki
```

**DSL Actions:**
```yaml
- connect         # Nawiąż połączenie
- disconnect      # Zamknij połączenie
- wait            # Czekaj N sekund
- click           # Kliknij na współrzędnych
- find_and_click  # Znajdź element (AI) i kliknij
- type            # Wpisz tekst
- key             # Naciśnij klawisz
- verify          # Zweryfikuj stan (AI)
- analyze         # Analizuj ekran (AI)
```

### 3. Ollama Container

**Technologie:**
- Ollama Server
- AI Vision Models (GGUF format)

**Odpowiedzialności:**
- Hostowanie modeli AI vision
- Przetwarzanie requestów inference
- Zarządzanie modelem w pamięci

**API Endpoints:**
```
POST /api/generate      # Generate completion
GET  /api/tags          # List models
POST /api/pull          # Pull model
POST /api/show          # Model info
```

**Modele:**
```
llava:7b    - 4.5GB - Balanced
llava:13b   - 8GB   - High accuracy
moondream   - 1.7GB - Fast
bakllava    - 5GB   - Alternative
```

**Model Loading:**
```
1. Request arrives
2. Check if model in memory
3. Load model if needed (8-10s)
4. Process inference (2-15s depending on complexity)
5. Return response
```

### 4. Portainer Container (Optional)

**Technologie:**
- Portainer CE

**Odpowiedzialności:**
- Web UI do zarządzania Docker
- Monitoring kontenerów
- Zarządzanie volumami i sieciami

**Port:** `9000`

---

## Przepływ danych

### Scenario Execution Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     │ 1. Run scenario command
     ▼
┌─────────────────────┐
│ automation_cli.py   │
│ - Load YAML         │
│ - Parse scenario    │
└──────┬──────────────┘
       │
       │ 2. Execute DSL
       ▼
┌─────────────────────────────┐
│  AutomationEngine           │
│  - Iterate through actions  │
│  - Call appropriate methods │
└──────┬──────────────────────┘
       │
       │ 3. VNC commands
       ▼
┌─────────────────────────┐        ┌──────────────┐
│  RemoteController       │◀──────▶│  VNC Desktop │
│  - Send mouse/keyboard  │  VNC   │  Container   │
│  - Capture screenshots  │        └──────────────┘
└──────┬──────────────────┘
       │
       │ 4. AI analysis requests
       ▼
┌─────────────────────┐          ┌──────────────┐
│  OllamaVision       │◀────────▶│   Ollama     │
│  - Encode image     │   HTTP   │  Container   │
│  - Send prompt      │          └──────────────┘
│  - Parse response   │
└──────┬──────────────┘
       │
       │ 5. Results
       ▼
┌─────────────────────┐
│  Test Results       │
│  - JSON output      │
│  - Variables stored │
└─────────────────────┘
```

### Screenshot Analysis Flow

```
1. Controller captures screenshot
   └─▶ PIL Image object (1280x800)

2. Image preprocessing (optional)
   ├─▶ Resize to 800x600 (for performance)
   └─▶ Convert to JPEG (compression)

3. Image encoding
   └─▶ Base64 string

4. Send to Ollama
   ├─▶ HTTP POST /api/generate
   ├─▶ JSON payload with image and prompt
   └─▶ Model: llava:7b

5. Ollama processing
   ├─▶ Decode image
   ├─▶ Vision model inference
   └─▶ Generate text response

6. Response parsing
   ├─▶ Extract text from JSON
   ├─▶ Parse coordinates (if finding element)
   └─▶ Store in variables

7. Action based on response
   ├─▶ Click if element found
   ├─▶ Verify if checking state
   └─▶ Store if analyzing
```

---

## Protokoły komunikacji

### VNC Protocol

```
Client (Controller) ◀──────▶ Server (Desktop)
                    RFB Protocol
                    Port 5901

Handshake:
1. Protocol version exchange
2. Security handshaking (password)
3. Client initialization
4. Server initialization

Messages:
- FramebufferUpdate (server → client)
- PointerEvent (client → server)
- KeyEvent (client → server)
- ClientCutText (clipboard)
```

### Ollama API

```
Controller ◀─────────▶ Ollama
           HTTP/REST
           Port 11434

Request:
POST /api/generate
{
  "model": "llava:7b",
  "prompt": "What do you see?",
  "images": ["base64_encoded_image"],
  "stream": false
}

Response:
{
  "model": "llava:7b",
  "created_at": "2025-01-01T00:00:00Z",
  "response": "I see a desktop with...",
  "done": true
}
```

### Docker Network

```
Bridge Network: automation-net
Subnet: 172.20.0.0/16

Service Discovery:
- vnc-desktop     → 172.20.0.2
- ollama          → 172.20.0.3
- controller      → 172.20.0.4

DNS Resolution:
controller can reach: vnc-desktop:5901
controller can reach: ollama:11434
```

---

## Decyzje architektoniczne

### ADR-001: Docker Compose vs Kubernetes

**Decyzja:** Użyj Docker Compose

**Kontekst:**
- Prosta instalacja dla użytkowników końcowych
- Większość use cases to single-host
- Lokalne środowisko testowe

**Konsekwencje:**
- ✅ Łatwa instalacja (make up)
- ✅ Mniejsze wymagania zasobowe
- ❌ Brak auto-scaling
- ❌ Brak high-availability

**Status:** Accepted

### ADR-002: VNC vs X11 forwarding

**Decyzja:** Użyj VNC

**Kontekst:**
- Potrzeba pełnego desktop environment
- Dostęp przez przeglądarkę (noVNC)
- Cross-platform compatibility

**Alternatywy:**
- X11 forwarding - wymaga X server na hoście
- RDP - lepsze dla Windows, nie Linux

**Konsekwencje:**
- ✅ Działa na każdym systemie
- ✅ Web access
- ✅ Pełny desktop
- ❌ Większe zużycie zasobów niż X11

**Status:** Accepted

### ADR-003: Ollama vs OpenAI API

**Decyzja:** Użyj Ollama (local models)

**Kontekst:**
- Privacy concerns (screenshots mogą zawierać wrażliwe dane)
- Koszt (API calls vs local inference)
- Offline capability

**Konsekwencje:**
- ✅ Privacy - dane nie opuszczają hosta
- ✅ Bez kosztów API
- ✅ Działa offline
- ❌ Wymaga więcej RAM
- ❌ Wolniejsze niż cloud API

**Status:** Accepted (z opcją integracji cloud w przyszłości)

### ADR-004: YAML DSL vs Python Scripts

**Decyzja:** YAML DSL jako primary, Python jako advanced

**Kontekst:**
- Prostota dla non-programistów
- Deklaratywny opis zadań
- Łatwość wersjonowania

**Konsekwencje:**
- ✅ Łatwe dla beginners
- ✅ Czytelne scenariusze
- ✅ Łatwe do sharowania
- ❌ Ograniczona elastyczność (ale można Python)

**Status:** Accepted

### ADR-005: Synchronous vs Asynchronous Execution

**Decyzja:** Synchronous execution

**Kontekst:**
- UI automation jest inherently sekwencyjna
- Prostszy kod i debugging
- Mniejsza złożoność

**Konsekwencje:**
- ✅ Prostsza implementacja
- ✅ Łatwiejszy debugging
- ✅ Przewidywalne zachowanie
- ❌ Nie można równoległych testów (ale można multiple containers)

**Status:** Accepted

---

## Skalowanie i wydajność

### Vertical Scaling

```yaml
# Zwiększ zasoby kontenerów
services:
  vnc-desktop:
    mem_limit: 4g
    cpus: 4
  
  ollama:
    mem_limit: 16g
    cpus: 8
    # GPU support
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
```

### Horizontal Scaling

```bash
# Uruchom wiele instancji
docker-compose -p automation1 up -d
docker-compose -p automation2 up -d

# Lub Kubernetes deployment (future)
```

### Performance Optimizations

1. **Model Selection**
   - moondream: 3s per inference
   - llava:7b: 5s per inference
   - llava:13b: 12s per inference

2. **Image Preprocessing**
   - Resize: 1280x800 → 800x600 (-40% time)
   - Compress: PNG → JPEG 85% (-30% bandwidth)

3. **Connection Pooling**
   - Reuse VNC connections
   - Keep Ollama model loaded

---

## Security Considerations

### Container Isolation

```yaml
# Limity zasobów
mem_limit: 4g
cpus: 2

# Read-only filesystem gdzie możliwe
read_only: true

# Drop capabilities
cap_drop:
  - ALL
```

### Network Security

```yaml
# Izolacja sieci
networks:
  automation-net:
    internal: true  # No external access
```

### Credentials

```bash
# Nigdy nie commituj haseł
.env file (gitignored)
VNC_PASSWORD=secure_password

# Używaj Docker secrets (production)
docker secret create vnc_password password.txt
```

---

## Monitoring i Observability

### Metrics

```python
# Zbieraj metryki
- Test execution time
- Screenshot capture time
- AI inference time
- Error rates
- Resource usage (CPU, RAM, Network)
```

### Logging

```python
# Structured logging
{
  "timestamp": "2025-01-01T00:00:00Z",
  "level": "INFO",
  "component": "RemoteController",
  "action": "click",
  "coordinates": [100, 200],
  "duration_ms": 50
}
```

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "pgrep", "Xvnc"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Future Enhancements

### Roadmap Items

1. **Multi-protocol Support**
   - RDP dla Windows
   - SPICE dla QEMU/KVM
   - X2Go dla enterprise

2. **Cloud Integration**
   - AWS Lambda dla scheduled tasks
   - Azure Container Instances
   - GCP Cloud Run

3. **Advanced AI**
   - Multiple AI providers (OpenAI, Anthropic)
   - Fine-tuned models dla specific domains
   - Visual regression testing

4. **Scalability**
   - Kubernetes Helm charts
   - Distributed test execution
   - Central result aggregation

---

## References

- [Docker Compose Spec](https://docs.docker.com/compose/compose-file/)
- [VNC Protocol](https://www.rfc-editor.org/rfc/rfc6143)
- [Ollama Documentation](https://ollama.ai/docs)
- [XFCE Desktop](https://docs.xfce.org/)

---

**Questions?** Open an issue or discussion on GitHub.
