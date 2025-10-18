# 🔍 Debugging Guide - RemoteBot

## Rozszerzone logowanie i screenshoty

System teraz zawiera zaawansowane narzędzia debugowania, które ułatwiają diagnozowanie problemów podczas wykonywania scenariuszy.

## 📊 System logowania z timestampami

Wszystkie akcje są logowane z dokładnymi timestampami:

```
[19:04:33.142] ℹ️ Starting scenario: test_debug_screen
[19:04:33.145] 🔍 Debug mode ENABLED - saving screenshots
[19:04:33.148] ℹ️ Step 1: connect
[19:04:34.251] ✓ Connected to vnc-desktop:5901
[19:04:34.255] ℹ️ Step 2: wait
[19:04:34.257] ℹ️ Waiting 2s...
[19:04:36.512] ℹ️ Step 3: analyze
```

**Typy logów:**
- `ℹ️` - Informacja
- `✓` - Sukces
- `✗` - Błąd
- `🔍` - Debug

## 📸 Automatyczne screenshoty

### Tryb 1: Debug Mode (`--debug`)

Zapisuje screenshoty **przed i po każdej akcji** (oprócz `wait` i `disconnect`):

```bash
# Uruchom z debug mode
make test-debug
# lub
python run_scenario.py scenario.yaml test_name --debug --no-recording
```

**Efekt:** Około 2 screenshoty na krok (przed/po)

### Tryb 2: Manualne screenshoty

Dodaj akcję `screenshot` w scenariuszu:

```yaml
scenarios:
  my_test:
    - action: connect
    - action: screenshot
      name: "initial_state"
    - action: click_position
      position: "top-left"
    - action: screenshot
      name: "after_click"
    - action: disconnect
```

### Tryb 3: Test ze screenshotami co 1s

```bash
make test-debug-screenshots
```

Ten test zbiera screenshoty co sekundę przez 5 sekund - idealny do obserwowania zmian.

## 📂 Lokalizacja screenshotów

Wszystkie screenshoty są zapisywane w:
```
/app/results/screenshots/
```

W kontenerze, mapowane do:
```
./results/screenshots/
```

## 🎯 Format nazw screenshotów

```
20251018_190433_001_before_connect.png
│         │       │   │
│         │       │   └─ Nazwa akcji
│         │       └───── Numer kroku (001, 002, 003...)
│         └───────────── Timestamp: HHMMSS
└─────────────────────── Data: YYYYMMDD
```

## 🧪 Dostępne komendy debug

### Podstawowe testy debug

```bash
# Szybki test połączenia (bez AI, 5s)
make test-quick

# Debug - co widzi AI na ekranie
make test-debug

# Zbieranie screenshotów co 1s przez 5s
make test-debug-screenshots
```

### Testy z Firefox + debug

```bash
# Firefox bez AI (szybki)
make test-firefox-simple

# Firefox z AI + screenshoty debug
make test-firefox-ai-debug
```

## 📋 Śledzenie błędów

System zbiera wszystkie błędy i wyświetla je na końcu:

**Przed (stary):**
```
✅ Scenariusz zakończony pomyślnie!
```

**Teraz (nowy):**
```
⚠️  Scenariusz zakończony z błędami:
  - Element not found: Firefox browser icon on desktop
  - Verification failed: Firefox browser window is open
```

## 🔧 Typowe scenariusze debugowania

### 1. Firefox nie został znaleziony przez AI

```bash
# Krok 1: Zbierz screenshoty
make test-debug-screenshots

# Krok 2: Sprawdź co AI widzi
make test-debug

# Krok 3: Zobacz screenshoty w results/screenshots/

# Krok 4: Jeśli wiesz gdzie jest Firefox, użyj click_position zamiast AI
make test-firefox-simple
```

### 2. Test zawiesza się na AI analyze

```bash
# Sprawdź logi z timestampami - zobaczysz gdzie się zatrzymał
# Log pokaże:
[19:04:36.512] 🤖 Wysyłam zapytanie do Ollama (llava:7b)...
[19:04:36.514]    Timeout: 120s - to może chwilę potrwać...
# ... czekamy ...
[19:05:04.231]    ✓ Odpowiedź otrzymana po 27.7s
```

### 3. Nieoczekiwane zachowanie

```bash
# Uruchom test z pełnym debug
docker-compose exec automation-controller \
  python3 /app/run_scenario.py \
  /app/test_scenarios/test_firefox_simple.yaml \
  test_firefox_ai \
  --debug \
  --no-recording

# Przejrzyj screenshoty krok po kroku
ls -lh results/screenshots/
```

## 🎬 Porównanie: Recording vs Debug Screenshots

| Feature | Video Recording | Debug Screenshots |
|---------|----------------|-------------------|
| Format | MP4 (10 fps) | PNG (przed/po akcji) |
| Rozmiar | ~1-5 MB/min | ~0.5 MB/screenshot |
| Wymaga | OpenCV (cv2) | Tylko PIL |
| Precyzja | Ciągłe | Dyskretne (przed/po) |
| Cel | Prezentacja | Debugging |
| Opcja | `--no-recording` wyłącza | `--debug` włącza |

## 📖 Przykład pełnego debug workflow

```bash
# 1. Przebuduj kontener (jeśli zmieniałeś kod)
make build
make up

# 2. Sprawdź status usług
make status

# 3. Uruchom test debug ze screenshotami
make test-debug-screenshots

# 4. Zobacz co AI widzi
make test-debug

# 5. Sprawdź zebrane screenshoty
ls -lth results/screenshots/ | head -20

# 6. Jeśli potrzeba, uruchom test z pełnym debug
make test-firefox-ai-debug

# 7. Sprawdź logi w czasie rzeczywistym
docker-compose logs -f automation-controller
```

## 💡 Wskazówki

1. **Zawsze najpierw `test-quick`** - sprawdź czy połączenie działa
2. **Użyj `test-debug-screenshots`** - zobacz desktop bez AI
3. **Sprawdź timestampy** - znajdź gdzie test się zatrzymuje
4. **Porównaj screenshoty** - zobacz co się zmieniło między krokami
5. **Screenshoty są tańsze niż video** - użyj `--debug --no-recording` dla szybkiego debugowania

## 🚨 Troubleshooting

### Brak katalogu screenshots

```bash
# Utwórz ręcznie
docker-compose exec automation-controller mkdir -p /app/results/screenshots
```

### Za dużo screenshotów

```bash
# Wyczyść stare screenshoty
rm results/screenshots/*.png

# Lub zachowaj tylko ostatnie 50
ls -t results/screenshots/*.png | tail -n +51 | xargs rm
```

### Nie mogę zobaczyć screenshotów

```bash
# Skopiuj z kontenera
docker-compose cp automation-controller:/app/results/screenshots ./debug_screenshots

# Lub otwórz w przeglądarce (jeśli masz X server)
xdg-open results/screenshots/
```
