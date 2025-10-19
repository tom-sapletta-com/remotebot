# 📋 Live Monitor - System Logowania

## Opis

Dodano kompletny system logowania do Live Monitor, który pokazuje wszystkie zdarzenia i błędy podczas wykonywania scenariuszy w czasie rzeczywistym.

## Nowe Funkcje

### 1. **Panel Logów** (Prawy Panel)

```
┌────────────┬────────────────┬────────────────┐
│  Steps     │  VNC Preview   │   Logs Panel   │
│  (400px)   │  (flexible)    │   (350px)      │
└────────────┴────────────────┴────────────────┘
```

**Cechy:**
- ✅ Automatyczna aktualizacja co 1 sekundę
- ✅ Auto-scroll do najnowszych wpisów
- ✅ Kolorowe oznaczenia według poziomu (info/success/error/warning)
- ✅ Timestamp dla każdego wpisu
- ✅ Przycisk "Clear" do czyszczenia logów
- ✅ Monospace font dla lepszej czytelności
- ✅ Przechowuje ostatnie 100 wpisów

### 2. **Poziomy Logów**

| Poziom | Kolor | Kiedy używany |
|--------|-------|---------------|
| **info** | 🔵 Niebieski | Informacje o działaniu (połączenia, inicjalizacja) |
| **success** | 🟢 Zielony | Pomyślne wykonanie kroków |
| **error** | 🔴 Czerwony | Błędy wykonania, problemy z połączeniem |
| **warning** | 🟠 Pomarańczowy | Ostrzeżenia (przyszłe użycie) |

### 3. **Nowe API Endpoints**

#### `/api/logs` (GET)
Zwraca ostatnie logi.

**Odpowiedź:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "14:23:45",
      "level": "info",
      "message": "Connecting to VNC desktop..."
    },
    {
      "timestamp": "14:23:46",
      "level": "success",
      "message": "Connected to VNC successfully!"
    }
  ]
}
```

#### `/api/logs/clear` (GET)
Czyści bufor logów.

**Odpowiedź:**
```json
{
  "success": true
}
```

## Przykłady Logów

### 1. Połączenie do VNC

```
14:23:45  [INFO]    Connecting to VNC desktop...
14:23:46  [SUCCESS] Connected to VNC successfully!
```

### 2. Wykonywanie Scenariusza

```
14:24:10  [INFO]    Starting scenario: browser_test
14:24:11  [INFO]    Initializing automation engine...
14:24:12  [SUCCESS] Automation engine initialized
14:24:13  [INFO]    Step 1/5: open_browser
14:24:15  [SUCCESS] Step 1 completed: open_browser
14:24:16  [INFO]    Step 2/5: navigate_to
14:24:18  [SUCCESS] Step 2 completed: navigate_to
14:24:19  [INFO]    Step 3/5: click
14:24:20  [SUCCESS] Step 3 completed: click
14:24:21  [SUCCESS] Scenario completed! 5 steps executed
```

### 3. Błędy

```
14:25:30  [ERROR]   Connection failed: Connection refused
14:26:15  [ERROR]   Step 3 failed: Element not found
14:27:22  [ERROR]   Failed to initialize engine: Ollama not available
```

## Implementacja Backendu

### Python - Funkcja Logowania

```python
# Global
log_buffer = []
log_lock = Lock()
MAX_LOGS = 100

def add_log(level, message):
    """Add log entry to buffer"""
    global log_buffer
    with log_lock:
        timestamp = time.strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,  # info, success, error, warning
            'message': message
        }
        log_buffer.append(log_entry)
        if len(log_buffer) > MAX_LOGS:
            log_buffer.pop(0)
        print(f"[{timestamp}] [{level.upper()}] {message}")
```

### Użycie w Kodzie

```python
# Przykłady użycia
add_log('info', 'Connecting to VNC desktop...')
add_log('success', 'Connected to VNC successfully!')
add_log('error', f'Connection failed: {str(e)}')
add_log('info', f'Step {i + 1}/{total}: {action}')
add_log('success', f'Step {i + 1} completed')
```

## Implementacja Frontendu

### JavaScript - Automatyczna Aktualizacja

```javascript
// Poll logs every second
let logPollInterval = null;

function startLogPolling() {
    if (logPollInterval) return;
    
    updateLogs();  // Initial update
    logPollInterval = setInterval(updateLogs, 1000);
}

function updateLogs() {
    fetch('/api/logs')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.logs) {
                displayLogs(data.logs);
            }
        });
}

function displayLogs(logs) {
    const container = document.getElementById('logContent');
    container.innerHTML = logs.map(log => `
        <div class="log-entry ${log.level}">
            <span class="timestamp">${log.timestamp}</span>
            <span class="message">${escapeHtml(log.message)}</span>
        </div>
    `).join('');
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}
```

### CSS - Style Logów

```css
.log-entry {
    padding: 6px 10px;
    margin-bottom: 2px;
    border-left: 3px solid transparent;
    display: flex;
    gap: 10px;
}

.log-entry.info {
    border-left-color: #4fc3f7;
    background: #1a2832;
}

.log-entry.success {
    border-left-color: #4caf50;
    background: #1a2819;
    color: #81c784;
}

.log-entry.error {
    border-left-color: #f44336;
    background: #321a1a;
    color: #ef5350;
}
```

## Miejsca z Logowaniem

### 1. **Połączenia**
- `connect_vnc()` - Loguje połączenie/błędy
- `disconnect_vnc()` - Loguje rozłączenie

### 2. **Wykonywanie Kroków**
- `execute_step()` - Loguje inicjalizację, wykonanie, sukces/błędy
- `execute_all()` - Loguje start scenariusza, każdy krok, zakończenie

### 3. **Inicjalizacja**
- `__main__` - Loguje start Live Monitor

### 4. **Przyszłe Rozszerzenia**
- Screenshot capture failures
- Ollama vision requests/responses
- Network issues
- Resource warnings

## Testowanie

### 1. Test Podstawowy

```bash
# Start Live Monitor
docker-compose exec -d automation-controller python3 /app/live_monitor.py

# Sprawdź logi przez API
curl http://localhost:5000/api/logs | jq

# Otwórz w przeglądarce
http://localhost:5000
```

### 2. Test Połączenia

1. Kliknij "Connect VNC"
2. Sprawdź panel logów:
   - Powinien pokazać: "Connecting to VNC desktop..."
   - Następnie: "Connected to VNC successfully!"

### 3. Test Wykonywania

1. Wybierz scenariusz
2. Kliknij "▶ Execute" na kroku
3. Sprawdź panel logów:
   - "Initializing automation engine..."
   - "Automation engine initialized"
   - "Executing step 1: [action]"
   - "Step 1 completed: [action]"

### 4. Test Błędów

1. Rozłącz VNC
2. Spróbuj wykonać krok
3. Sprawdź logi błędów w czerwonym kolorze

### 5. Test "Run All"

1. Kliknij "▶ Run All"
2. Obserwuj logi dla każdego kroku:
   ```
   Starting scenario: test_scenario
   Step 1/10: open_browser
   Step 1 completed
   Step 2/10: navigate
   Step 2 completed
   ...
   Scenario completed! 10 steps executed
   ```

## Optymalizacje

### 1. **Buffer Size**
```python
MAX_LOGS = 100  # Przechowuje ostatnie 100 wpisów
```

### 2. **Polling Rate**
```javascript
setInterval(updateLogs, 1000);  // Co 1 sekundę
```

### 3. **Auto-scroll**
```javascript
container.scrollTop = container.scrollHeight;  // Zawsze na dole
```

## Przyszłe Rozszerzenia

### 1. **Filtry Logów**
```javascript
// Przycisk do filtrowania po poziomie
<button onclick="filterLogs('error')">Show Errors Only</button>
```

### 2. **Eksport Logów**
```javascript
// Zapisz logi do pliku
function exportLogs() {
    const logsText = logs.map(l => 
        `${l.timestamp} [${l.level.toUpperCase()}] ${l.message}`
    ).join('\n');
    
    download('logs.txt', logsText);
}
```

### 3. **Szczegółowe Logi**
```python
# Logowanie szczegółów kroków
add_log('info', f'Step details: {json.dumps(step, indent=2)}')

# Logowanie czasu wykonania
add_log('info', f'Step executed in {duration:.2f}s')
```

### 4. **Poziomy Werbozności**
```python
LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR

def add_log(level, message, verbose_level='INFO'):
    if SHOULD_LOG(verbose_level):
        # ... existing code
```

## Debugging

### Problem: Logi nie aktualizują się

**Rozwiązanie:**
```javascript
// Sprawdź console
console.log('Log polling active:', logPollInterval !== null);

// Sprawdź API
fetch('/api/logs').then(r => r.json()).then(console.log);
```

### Problem: Zbyt wiele logów

**Rozwiązanie:**
```python
# Zwiększ MAX_LOGS
MAX_LOGS = 200

# Lub dodaj czyszczenie automatyczne
if len(log_buffer) > MAX_LOGS * 2:
    log_buffer = log_buffer[-MAX_LOGS:]
```

### Problem: Logi nie są kolorowe

**Rozwiązanie:**
- Sprawdź czy level jest poprawny: 'info', 'success', 'error', 'warning'
- Clear browser cache (Ctrl+Shift+R)

## Podsumowanie

✅ **Dodano:**
- Panel logów (350px szerokości)
- API endpoints: `/api/logs` i `/api/logs/clear`
- Automatyczne odświeżanie co 1s
- 4 poziomy logów z kolorami
- Auto-scroll do najnowszych
- Przycisk "Clear"
- Logowanie we wszystkich kluczowych miejscach

✅ **Korzyści:**
- Natychmiastowa widoczność błędów
- Łatwe debugowanie scenariuszy
- Historia ostatnich 100 akcji
- Profesjonalny wygląd
- Nie wymaga sprawdzania console/terminala

---

**Status:** ✅ GOTOWE  
**Wersja:** 1.0  
**Data:** 2025-10-19
