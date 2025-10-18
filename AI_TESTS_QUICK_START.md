# 🚀 AI Tests - Quick Start Guide

## ✅ Co zostało dodane

Utworzono **13 zaawansowanych testów AI**, które używają vision AI (Ollama llava:7b) do inteligentnego sterowania i analizy komputera.

## 📁 Nowe Pliki

```
test_scenarios/
  └── ai_driven_tests.yaml        # 13 scenariuszy AI-driven
  
docs/
  └── AI_TESTS.md                 # Pełna dokumentacja
  
Makefile                          # 14 nowych komend (test-ai-*)
```

## 🎯 Najszybszy Start

### 1. Zobacz listę testów AI
```bash
make list-ai-tests
```

### 2. Uruchom prosty test (Desktop Mapper)
```bash
make test-ai-desktop-mapper
```

**Czas:** ~2 minuty  
**Co robi:** AI mapuje pulpit i raportuje wszystkie ikony, taskbar, i środowisko graficzne.

### 3. Uruchom test detekcji błędów
```bash
make test-ai-errors
```

**Czas:** ~2 minuty  
**Co robi:** AI wywołuje błąd Python, rozpoznaje typ błędu, diagnozuje przyczynę i sugeruje rozwiązanie.

### 4. Monitor wydajności
```bash
make test-ai-performance
```

**Czas:** ~2 minuty  
**Co robi:** AI uruchamia `top` i `df`, analizuje CPU, RAM, disk usage i wykrywa anomalie.

## 📋 Wszystkie Dostępne Testy

| Komenda | Czas | Opis |
|---------|------|------|
| `make test-ai-adaptive` | 2-3min | Adaptacyjna nawigacja Firefox |
| `make test-ai-search` | 3-4min | Inteligentne wyszukiwanie Google |
| `make test-ai-desktop-mapper` | 2min | Mapowanie pulpitu |
| `make test-ai-monitor` | 2-3min | Monitor stanu aplikacji |
| `make test-ai-editor` | 2min | Edycja i walidacja kodu |
| `make test-ai-files` | 2min | Nawigacja systemu plików |
| `make test-ai-forms` | 3min | Rozpoznawanie formularzy web |
| `make test-ai-errors` | 2min | Detekcja i diagnoza błędów |
| `make test-ai-windows` | 3min | Zarządzanie wieloma oknami |
| `make test-ai-visual` | 2min | Visual regression testing |
| `make test-ai-performance` | 2min | Monitoring wydajności |
| `make test-ai-ui` | 2-3min | Walidacja UI i accessibility |
| `make test-ai-commands` | 2min | Analiza outputu komend |

### Uruchom wszystkie (10-30 minut!)
```bash
make test-ai-all
```

## 🎓 Przykładowy Output

```bash
$ make test-ai-desktop-mapper

AI Test: Desktop mapper...
📄 Wczytuję scenariusz: /app/test_scenarios/ai_driven_tests.yaml

🚀 Uruchamiam scenariusz: desktop_mapper
📹 Nagrywanie: WYŁĄCZONE

[18:09:17] ℹ️ Starting scenario: desktop_mapper
[18:09:17] ℹ️ Step 1: connect
✓ Connected to VNC: vnc-desktop:5901
[18:09:20] 🔍 Screenshot saved: desktop_full.png
[18:09:21] ℹ️ Step 4: analyze
🤖 Wysyłam zapytanie do Ollama (llava:7b)...
   ✓ Odpowiedź otrzymana po 34.4s
  Analysis: The image shows a Linux desktop with a custom 
  desktop environment that appears to be a modified version 
  of XFCE...

✅ Scenariusz zakończony pomyślnie!

📊 Zebrane dane:
  desktop_inventory: Based on the image provided, it appears 
    to be a screenshot of a computer desktop interface...
  desktop_environment: The image shows a Linux desktop with 
    a custom desktop environment...
  taskbar_contents: In the image you've provided, it appears 
    to be a screenshot showing several icons...
```

## 💡 Co Te Testy Robią Inaczej?

### Tradycyjne Testy
```yaml
- action: click
  x: 100
  y: 200  # Stałe współrzędne - kruche!
```

### AI-Driven Testy
```yaml
- action: find_and_click
  element: "Firefox browser icon"  # AI znajduje!

- action: analyze
  question: "Is Firefox open? Answer YES or NO."
  save_to: firefox_status  # AI weryfikuje!
```

## 🔥 Kluczowe Możliwości

### 1. Adaptacyjna Nawigacja
AI **automatycznie** znajduje elementy na ekranie:
```yaml
- action: find_and_click
  element: "search box or search field"
```

### 2. Inteligentna Walidacja
AI **rozumie** kontekst i weryfikuje:
```yaml
- action: verify
  expected: "Firefox browser window is open"
```

### 3. Ekstrakcja Danych
AI **odczytuje** i **parsuje** tekst z ekranu:
```yaml
- action: analyze
  question: "What is the CPU usage percentage?"
  save_to: cpu_usage
```

### 4. Diagnoza Błędów
AI **rozpoznaje** typy błędów i **sugeruje** rozwiązania:
```yaml
- action: analyze
  question: "What type of error is this and how to fix it?"
  save_to: error_diagnosis
```

## 🎯 Przypadki Użycia

### ✅ Kiedy używać AI-Driven Tests:

1. **Testy eksploracyjne** - nie znasz dokładnej struktury UI
2. **Cross-platform testing** - UI różni się między platformami
3. **Dynamic content** - pozycje elementów się zmieniają
4. **Accessibility testing** - AI ocenia kontrast i czytelność
5. **Error monitoring** - AI rozumie błędy w kontekście
6. **Visual regression** - wykrywa nieoczekiwane zmiany

### ❌ Kiedy NIE używać:

1. **Testy wydajnościowe** - AI jest wolniejszy (20-60s)
2. **Testy jednostkowe** - za duży overhead
3. **CI/CD z limitem czasu** - może być zbyt wolny
4. **Proste testy** - jeśli masz stałe współrzędne, użyj ich

## 📖 Pełna Dokumentacja

Zobacz [docs/AI_TESTS.md](docs/AI_TESTS.md) dla:
- Szczegółowy opis każdego testu
- Troubleshooting
- Best practices dla promptów
- Przykłady tworzenia własnych testów
- Optymalizacja wydajności

## 🛠️ Konfiguracja

### Zmiana Modelu AI
W pliku `test_scenarios/ai_driven_tests.yaml`:
```yaml
ollama:
  url: http://ollama:11434
  model: llava:7b      # Standardowy (dokładniejszy)
  # model: moondream  # Szybszy (mniej dokładny)
```

### Timeout AI
W `automation/remote_automation.py` (linia 63):
```python
timeout=120  # Zwiększ dla wolniejszego sprzętu
```

## 🚀 Następne Kroki

1. **Wypróbuj testy:**
   ```bash
   make test-ai-desktop-mapper
   make test-ai-performance
   make test-ai-errors
   ```

2. **Zobacz screenshoty:**
   ```bash
   ls -la results/screenshots/
   ```

3. **Stwórz własny test:**
   - Edytuj `test_scenarios/ai_driven_tests.yaml`
   - Dodaj nowy scenariusz
   - Uruchom: `make test-ai-custom`

4. **Przeczytaj dokumentację:**
   ```bash
   cat docs/AI_TESTS.md
   ```

## 📊 Statystyki

- **13 testów AI** - gotowych do użycia
- **~650 linii YAML** - scenariusze testowe
- **~500 linii dokumentacji** - pełne opisy
- **14 komend Makefile** - łatwe uruchamianie
- **2-4 minuty** - średni czas pojedynczego testu

## ✨ Przykłady Wyników

### Desktop Mapper
```
desktop_environment: XFCE custom environment
desktop_inventory: 
  - Firefox icon (top-left)
  - Terminal icon (top-left)
  - File Manager icon (top-left)
taskbar_contents: Clock showing 4:35, notification area, 
  browser icons, system widgets
```

### Performance Monitor
```
cpu_analysis: CPU usage 15%, top process: firefox (8%)
memory_analysis: 2.1GB used / 4GB total (52%)
disk_analysis: Root filesystem 45% used, safe
resource_anomalies: No unusual resource consumption detected
```

### Error Detection
```
error_type: ImportError (module not found)
error_message: No module named 'nonexistent_module'
error_diagnosis: Module doesn't exist or not installed. 
  Fix: pip install nonexistent_module or check spelling
system_recovery: YES - terminal functional after error
```

## 🎉 Gotowe!

Masz teraz pełny zestaw AI-driven testów. Eksperymentuj i twórz własne!

**Wskazówka:** Zacznij od `make test-ai-desktop-mapper` - to najprostszy test.

---

📚 **Więcej info:** [docs/AI_TESTS.md](docs/AI_TESTS.md)  
🐛 **Issues:** [GitHub Issues](https://github.com)  
💬 **Help:** `make help`
