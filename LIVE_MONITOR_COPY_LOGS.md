# 📋 Live Monitor - Kopiowanie i Eksport Logów

## Nowe Funkcje

### 1. **Kopiowanie do Schowka** 📋

Przycisk "📋 Copy" kopiuje wszystkie logi do schowka systemowego.

**Użycie:**
1. Kliknij przycisk "📋 Copy" w panelu logów
2. Logi są automatycznie skopiowane
3. Przycisk pokazuje "✓ Copied!" przez 2 sekundy
4. Wklej (Ctrl+V) gdzie chcesz

**Format:**
```
[14:52:21] [INFO] Connecting to VNC desktop...
[14:52:22] [SUCCESS] Connected to VNC successfully!
[14:52:25] [INFO] Executing step 1: open_browser
[14:52:27] [SUCCESS] Step 1 completed: open_browser
[14:52:28] [ERROR] Step 2 failed: Element not found
```

### 2. **Pobieranie jako Plik** 💾

Przycisk "💾 Save" pobiera logi jako plik tekstowy.

**Użycie:**
1. Kliknij przycisk "💾 Save"
2. Plik zostanie automatycznie pobrany
3. Nazwa pliku: `live_monitor_logs_YYYYMMDD_HHMMSS.txt`

**Przykład nazwy:**
```
live_monitor_logs_20251019_145210.txt
```

### 3. **Czyszczenie Logów** 🗑️

Przycisk "🗑️ Clear" usuwa wszystkie logi z bufora.

**Użycie:**
1. Kliknij przycisk "🗑️ Clear"
2. Wszystkie logi zostają usunięte
3. Dodawany jest wpis: "Logs cleared"

## API Endpoints

### `GET /api/logs`
Zwraca logi w formacie JSON.

**Odpowiedź:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "14:52:21",
      "level": "info",
      "message": "Connecting to VNC desktop..."
    }
  ]
}
```

### `GET /api/logs/clear`
Czyści wszystkie logi.

**Odpowiedź:**
```json
{
  "success": true
}
```

### `GET /api/logs/download`
Pobiera logi jako plik tekstowy.

**Odpowiedź:**
```
Content-Type: text/plain
Content-Disposition: attachment; filename=live_monitor_logs_20251019_145210.txt

[14:52:21] [INFO] Connecting to VNC desktop...
[14:52:22] [SUCCESS] Connected to VNC successfully!
...
```

## Implementacja

### Backend (Python)

```python
@app.route('/api/logs/download')
def download_logs():
    """Download logs as text file"""
    global log_buffer
    with log_lock:
        logs_text = '\n'.join([
            f"[{log['timestamp']}] [{log['level'].upper()}] {log['message']}"
            for log in log_buffer
        ])
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'live_monitor_logs_{timestamp}.txt'
    
    return Response(
        logs_text,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
```

### Frontend (JavaScript)

#### Kopiowanie do Schowka

```javascript
function copyLogs() {
    fetch('/api/logs')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.logs) {
                // Format logs as text
                const logsText = data.logs.map(log => 
                    `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`
                ).join('\n');
                
                // Copy to clipboard
                navigator.clipboard.writeText(logsText)
                    .then(() => {
                        // Show feedback
                        const btn = event.target;
                        btn.textContent = '✓ Copied!';
                        btn.style.background = '#4caf50';
                        
                        setTimeout(() => {
                            btn.textContent = '📋 Copy';
                            btn.style.background = '';
                        }, 2000);
                    });
            }
        });
}
```

#### Pobieranie Pliku

```javascript
function downloadLogs() {
    // Open download endpoint (triggers browser download)
    window.open('/api/logs/download', '_blank');
}
```

## Przykłady Użycia

### 1. Debug Scenariusza

```bash
# Uruchom scenariusz w Live Monitor
# Kliknij "📋 Copy" gdy wystąpi błąd
# Wklej logi do zgłoszenia błędu
```

**Skopiowane logi:**
```
[14:52:21] [INFO] Starting scenario: browser_test
[14:52:22] [INFO] Initializing automation engine...
[14:52:23] [SUCCESS] Automation engine initialized
[14:52:24] [INFO] Step 1/5: open_browser
[14:52:26] [SUCCESS] Step 1 completed: open_browser
[14:52:27] [INFO] Step 2/5: navigate_to
[14:52:28] [ERROR] Step 2 failed: Connection timeout
```

### 2. Archiwizacja Testów

```bash
# Wykonaj test
# Kliknij "💾 Save"
# Plik zostanie zapisany jako: live_monitor_logs_20251019_145210.txt
# Archiwizuj plik dla późniejszej analizy
```

### 3. Analiza Wydajności

```bash
# Uruchom scenariusz
# Pobierz logi
# Analiza czasów wykonania kroków
```

**Przykład analizy:**
```
[14:52:24] Step 1 started
[14:52:26] Step 1 completed  → 2 sekundy
[14:52:27] Step 2 started
[14:52:32] Step 2 completed  → 5 sekund (wolny!)
```

## UI - Panel Logów

```
┌────────────────────────────────────────┐
│ 📋 Execution Logs                      │
│ [📋 Copy] [💾 Save] [🗑️ Clear]         │
├────────────────────────────────────────┤
│ 14:52:21  [INFO]    Connecting...      │
│ 14:52:22  [SUCCESS] Connected!         │
│ 14:52:25  [INFO]    Executing step 1   │
│ 14:52:27  [SUCCESS] Step 1 completed   │
│ 14:52:28  [ERROR]   Step 2 failed      │
│                                        │
│                                        │
└────────────────────────────────────────┘
```

## Keyboard Shortcuts (Przyszłość)

Potencjalne skróty klawiszowe:
- `Ctrl+C` - Kopiuj logi
- `Ctrl+S` - Zapisz logi
- `Ctrl+L` - Wyczyść logi

```javascript
// Przykładowa implementacja
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'c') {
        e.preventDefault();
        copyLogs();
    }
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        downloadLogs();
    }
});
```

## Testowanie

### Test 1: Kopiowanie

```bash
# 1. Otwórz Live Monitor
# 2. Połącz się z VNC
# 3. Kliknij "📋 Copy"
# 4. Otwórz edytor tekstu
# 5. Wklej (Ctrl+V)
# Oczekiwane: Logi są wklejone
```

### Test 2: Pobieranie

```bash
# 1. Otwórz Live Monitor
# 2. Wykonaj kilka kroków
# 3. Kliknij "💾 Save"
# 4. Sprawdź folder Downloads
# Oczekiwane: Plik live_monitor_logs_*.txt został pobrany
```

### Test 3: Czyszczenie

```bash
# 1. Panel logów ma wpisy
# 2. Kliknij "🗑️ Clear"
# 3. Sprawdź panel logów
# Oczekiwane: Tylko wpis "Logs cleared"
```

### Test 4: API

```bash
# Test pobierania przez API
curl -O http://localhost:5000/api/logs/download

# Sprawdź zawartość
cat live_monitor_logs_*.txt
```

## Kompatybilność

### Clipboard API
- ✅ Chrome 63+
- ✅ Firefox 53+
- ✅ Edge 79+
- ✅ Safari 13.1+

### File Download
- ✅ Wszystkie nowoczesne przeglądarki
- ✅ Działa również na urządzeniach mobilnych

## Rozwiązywanie Problemów

### Problem: Copy nie działa

**Przyczyna:** Brak uprawnień do schowka

**Rozwiązanie:**
1. Strona musi być na HTTPS lub localhost
2. Użytkownik musi zezwolić na dostęp do schowka
3. Fallback: Użyj "💾 Save" zamiast tego

### Problem: Plik się nie pobiera

**Przyczyna:** Blokada wyskakujących okien

**Rozwiązanie:**
1. Zezwól na wyskakujące okna dla localhost:5000
2. Lub kliknij prawym i wybierz "Save link as..."

### Problem: Brak logów w pliku

**Przyczyna:** Buffer logów jest pusty

**Rozwiązanie:**
- Połącz się z VNC
- Wykonaj kilka kroków
- Spróbuj ponownie

## Przyszłe Rozszerzenia

### 1. Filtry przy Kopiowaniu

```javascript
function copyErrorsOnly() {
    const errors = logs.filter(log => log.level === 'error');
    // Copy only errors...
}
```

### 2. Format Markdown

```javascript
function copyLogsAsMarkdown() {
    const markdown = logs.map(log => 
        `- **${log.timestamp}** [${log.level}] ${log.message}`
    ).join('\n');
    // Copy as markdown...
}
```

### 3. Eksport do JSON

```javascript
function downloadLogsAsJson() {
    const json = JSON.stringify(logs, null, 2);
    // Download as JSON...
}
```

### 4. Email Logs

```javascript
function emailLogs() {
    const subject = 'Live Monitor Logs';
    const body = logs.map(log => 
        `[${log.timestamp}] [${log.level}] ${log.message}`
    ).join('\n');
    
    window.location.href = `mailto:?subject=${subject}&body=${encodeURIComponent(body)}`;
}
```

## Podsumowanie

✅ **Dodano:**
- Przycisk "📋 Copy" - kopiuje do schowka
- Przycisk "💾 Save" - pobiera jako plik
- Przycisk "🗑️ Clear" - czyści logi
- Endpoint `/api/logs/download`
- Visual feedback dla kopiowania
- Automatyczne nazewnictwo plików

✅ **Korzyści:**
- Łatwe udostępnianie logów
- Archiwizacja wykonań
- Debug i analiza
- Profesjonalny wygląd
- Intuicyjna obsługa

---

**Status:** ✅ GOTOWE  
**Wersja:** 1.0  
**Data:** 2025-10-19
