# AI-Driven Tests Documentation

## 🤖 Overview

AI-Driven tests używają Ollama Vision (llava:7b) do inteligentnego analizowania ekranu i podejmowania decyzji w czasie rzeczywistym. W przeciwieństwie do tradycyjnych testów opartych na współrzędnych, te testy wykorzystują AI do:

- **Adaptacyjnej nawigacji** - AI znajduje elementy na ekranie i klika je
- **Inteligentnej walidacji** - AI weryfikuje czy testy przeszły pomyślnie
- **Ekstrakcji danych** - AI odczytuje tekst, liczby i strukturę z ekranu
- **Diagnozy problemów** - AI wykrywa błędy i sugeruje rozwiązania

## 📋 Dostępne Testy

### 1. Adaptacyjna Nawigacja Firefox
```bash
make test-ai-adaptive
```
**Czas:** ~2-3 minuty  
**Opis:** AI automatycznie znajduje ikonę Firefox, otwiera przeglądarkę, nawiguje do strony i analizuje jej zawartość.

**Co testuje:**
- Rozpoznawanie ikon aplikacji
- Znajdowanie i klikanie linków
- Ekstrakcja tekstu ze stron web
- Nawigacja między stronami

**Zebrane dane:**
- `firefox_visible` - czy Firefox jest widoczny
- `firefox_opened` - czy Firefox się otworzył
- `page_heading` - główny nagłówek strony
- `has_more_info_link` - czy jest link "More information"
- `current_url` - aktualny URL

### 2. Inteligentne Wyszukiwanie
```bash
make test-ai-search
```
**Czas:** ~3-4 minuty  
**Opis:** AI wyszukuje w Google, analizuje wyniki i wybiera najbardziej relevantny.

**Co testuje:**
- Interakcja z polami wyszukiwania
- Analiza wyników wyszukiwania
- Selekcja najbardziej odpowiedniego wyniku

**Zebrane dane:**
- `search_results` - tytuły pierwszych 3 wyników
- `relevant_result` - pozycja najbardziej relevantnego wyniku

### 3. Desktop Mapper
```bash
make test-ai-desktop-mapper
```
**Czas:** ~2 minuty  
**Opis:** AI tworzy pełną mapę pulpitu - wszystkie ikony, aplikacje, taskbar.

**Co testuje:**
- Rozpoznawanie layoutu pulpitu
- Identyfikacja środowiska graficznego
- Mapowanie elementów UI

**Zebrane dane:**
- `desktop_inventory` - lista wszystkich ikon z pozycjami
- `desktop_environment` - typ środowiska (XFCE, GNOME, etc.)
- `taskbar_contents` - zawartość paska zadań
- `context_menu` - opcje menu kontekstowego

### 4. Monitor Stanu Aplikacji
```bash
make test-ai-monitor
```
**Czas:** ~2-3 minuty  
**Opis:** AI śledzi zmiany na ekranie po otwarciu aplikacji i wykonaniu komend.

**Co testuje:**
- Detekcja zmian w czasie rzeczywistym
- Monitoring stanu aplikacji
- Analiza outputu programów (htop)

**Zebrane dane:**
- `state_1_windows` - okna w stanie początkowym
- `state_2_changes` - co się zmieniło po otwarciu terminala
- `state_3_htop` - top 3 procesy z htop
- `state_4_closed` - czy aplikacja została zamknięta

### 5. Inteligentna Edycja Tekstu
```bash
make test-ai-editor
```
**Czas:** ~2 minuty  
**Opis:** AI pisze kod Python w edytorze i weryfikuje jego poprawność.

**Co testuje:**
- Otwieranie edytorów tekstu
- Pisanie kodu
- Walidacja składni przez AI
- Rozumienie funkcjonalności kodu

**Zebrane dane:**
- `editor_ready` - czy edytor jest gotowy
- `code_validation` - czy składnia jest poprawna
- `code_functionality` - co robi kod

### 6. Nawigacja Plików
```bash
make test-ai-files
```
**Czas:** ~2 minuty  
**Opis:** AI eksploruje system plików i raportuje zawartość katalogów.

**Co testuje:**
- Otwieranie menedżera plików
- Rozpoznawanie struktury katalogów
- Identyfikacja folderów systemowych

**Zebrane dane:**
- `current_directory` - aktualny katalog
- `directory_contents` - lista plików i folderów
- `has_documents` - czy istnieje folder Documents
- `has_desktop` - czy istnieje folder Desktop

### 7. Rozpoznawanie Formularzy
```bash
make test-ai-forms
```
**Czas:** ~3 minuty  
**Opis:** AI analizuje formularze webowe i identyfikuje typy pól.

**Co testuje:**
- Rozpoznawanie elementów formularzy
- Liczenie pól input
- Identyfikacja przycisków submit

**Zebrane dane:**
- `form_field_count` - liczba pól formularza
- `form_field_types` - typy pól (text, checkbox, etc.)
- `submit_button` - tekst przycisku submit

### 8. Detekcja i Diagnoza Błędów
```bash
make test-ai-errors
```
**Czas:** ~2 minuty  
**Opis:** AI celowo wywołuje błąd, rozpoznaje typ błędu i sugeruje rozwiązanie.

**Co testuje:**
- Wykrywanie komunikatów błędów
- Klasyfikacja typów błędów
- Diagnoza przyczyn
- Weryfikacja recovery

**Zebrane dane:**
- `error_type` - typ błędu (ImportError, SyntaxError, etc.)
- `error_message` - dokładny komunikat błędu
- `error_diagnosis` - przyczyna i sugerowane rozwiązanie
- `system_recovery` - czy system nadal działa

### 9. Zarządzanie Wieloma Oknami
```bash
make test-ai-windows
```
**Czas:** ~3 minuty  
**Opis:** AI śledzi otwarte okna i przełączanie między nimi.

**Co testuje:**
- Liczenie otwartych okien
- Identyfikacja aktywnego okna
- Przełączanie focus (Alt+Tab)

**Zebrane dane:**
- `initial_window_count` - początkowa liczba okien
- `after_terminal_windows` - stan po otwarciu terminala
- `multiple_windows_state` - stan z wieloma oknami
- `window_after_switch` - aktywne okno po Alt+Tab

### 10. Detekcja Zmian Wizualnych
```bash
make test-ai-visual
```
**Czas:** ~2 minuty  
**Opis:** AI porównuje screenshoty przed i po zmianach, wykrywa różnice.

**Co testuje:**
- Visual regression testing
- Porównywanie stanów UI
- Wykrywanie anomalii wizualnych

**Zebrane dane:**
- `baseline_state` - szczegółowy opis stanu początkowego
- `visual_diff` - różnice między stanami
- `anomaly_detection` - czy są problemy z renderowaniem

### 11. Monitoring Wydajności
```bash
make test-ai-performance
```
**Czas:** ~2 minuty  
**Opis:** AI uruchamia `top` i `df`, analizuje wykorzystanie zasobów.

**Co testuje:**
- Odczyt CPU usage
- Analiza pamięci RAM
- Monitoring dysku
- Wykrywanie anomalii w zasobach

**Zebrane dane:**
- `cpu_analysis` - użycie CPU i top proces
- `memory_analysis` - użycie i dostępność RAM
- `resource_anomalies` - procesy z wysokim zużyciem
- `disk_analysis` - użycie dysku

### 12. Walidacja UI
```bash
make test-ai-ui
```
**Czas:** ~2-3 minuty  
**Opis:** AI analizuje jakość UI strony web - accessibility, kontrast, czytelność.

**Co testuje:**
- Hierarchia wizualna
- Kontrast kolorów (accessibility)
- Czytelność tekstu
- Poprawność layoutu

**Zebrane dane:**
- `layout_quality` - jakość hierarchii wizualnej
- `color_analysis` - analiza kolorów i kontrastu
- `readability_check` - czytelność tekstu
- `ui_issues` - wykryte problemy UI

### 13. Analiza Wyników Komend
```bash
make test-ai-commands
```
**Czas:** ~2 minuty  
**Opis:** AI uruchamia komendy systemowe i parsuje ich output.

**Co testuje:**
- Ekstrakcja adresów IP
- Odczyt wersji systemu
- Analiza uptime i load average

**Zebrane dane:**
- `ip_addresses` - lista adresów IPv4
- `os_version` - system i kernel
- `uptime_info` - czas działania i obciążenie

## 🚀 Uruchamianie Testów

### Pojedynczy test
```bash
make test-ai-desktop-mapper
```

### Lista wszystkich testów AI
```bash
make list-ai-tests
```

### Wszystkie testy AI (ostrzeżenie: 10-30 minut!)
```bash
make test-ai-all
```

### Z poziomu Python
```bash
docker-compose exec automation-controller python3 /app/run_scenario.py \
  /app/test_scenarios/ai_driven_tests.yaml \
  adaptive_firefox_navigation \
  --no-recording
```

## 📊 Wyniki Testów

### Zebrane dane
Po każdym teście dane są zapisywane w zmiennych i wyświetlane w sekcji `📊 Zebrane dane`.

Przykład:
```
📊 Zebrane dane:
  firefox_visible: YES
  firefox_opened: YES
  page_heading: Example Domain
  has_more_info_link: YES
  current_url: https://www.iana.org/domains/reserved
```

### Screenshoty
Testy zapisują screenshoty w:
```
results/screenshots/
```

Format: `YYYYMMDD_HHMMSS_NNN_nazwa.png`

## 🎯 Kiedy Używać AI-Driven Tests

### ✅ Dobre zastosowania:
- **Testy eksploracyjne** - gdy nie znasz dokładnej struktury UI
- **Cross-platform testing** - gdy UI różni się między platformami
- **Regression testing** - wykrywanie nieoczekiwanych zmian wizualnych
- **Accessibility testing** - AI może ocenić kontrast i czytelność
- **Dynamic content** - gdy pozycje elementów się zmieniają
- **Error monitoring** - AI rozumie komunikaty błędów w kontekście

### ❌ Kiedy NIE używać:
- **Testy wydajnościowe** - AI jest wolniejszy (20-60s na analizę)
- **Testy jednostkowe** - za duży overhead
- **Proste testy funkcjonalne** - jeśli masz stałe współrzędne, użyj ich
- **CI/CD z limitem czasu** - AI może być zbyt wolny
- **Testy bez połączenia** - wymaga Ollama

## ⚡ Optymalizacja Wydajności

### Model Selection
```yaml
ollama:
  model: llava:7b      # Standardowy (wolniejszy, dokładniejszy)
  # model: moondream  # Szybszy (mniej dokładny)
```

### Parallel Execution
AI testy mogą być uruchamiane równolegle jeśli masz wystarczającą moc GPU:
```bash
# Terminal 1
make test-ai-desktop-mapper

# Terminal 2  
make test-ai-performance

# Terminal 3
make test-ai-errors
```

### Cache Warming
Pierwszy request do Ollama jest wolniejszy. Rozgrzej cache:
```bash
make test-quick  # Uruchom prosty test najpierw
make test-ai-adaptive  # Potem AI test będzie szybszy
```

## 🔧 Troubleshooting

### Test timeout
```
Błąd: Ollama timeout po 120s
```
**Rozwiązanie:** Model nie jest pobrany:
```bash
make pull-model
```

### Niepoprawne wyniki AI
```
AI nie znajdzie elementu / zwraca złe dane
```
**Rozwiązanie:**
1. Sprawdź screenshot w `results/screenshots/`
2. Użyj `--debug` flag do zapisania wszystkich kroków
3. Dostosuj prompt w YAML
4. Użyj większego modelu (llava:13b)

### Wolne wykonanie
```
Test trwa bardzo długo
```
**Rozwiązanie:**
1. Sprawdź czy Ollama używa GPU (`docker stats`)
2. Użyj mniejszego modelu (moondream)
3. Ogranicz liczbę analiz w scenariuszu
4. Zwiększ timeout jeśli masz wolniejszy sprzęt

## 📝 Tworzenie Własnych Testów AI

### Szablon scenariusza
```yaml
scenarios:
  my_custom_ai_test:
    - action: connect
    - action: wait
      seconds: 2
    
    # AI znajduje i klika element
    - action: find_and_click
      element: "description of UI element to find"
    
    - action: wait
      seconds: 2
    
    # AI analizuje ekran
    - action: analyze
      question: "What do you see on screen? Be specific."
      save_to: screen_analysis
    
    # AI weryfikuje warunek
    - action: verify
      expected: "the application is working correctly"
    
    - action: disconnect
```

### Best Practices dla Promptów

**✅ Dobre prompty:**
```yaml
question: "List all visible desktop icons with their positions."
question: "Is the Firefox browser window open? Answer YES or NO."
question: "What is the exact error message shown? Copy the text."
```

**❌ Złe prompty:**
```yaml
question: "What's happening?"  # Zbyt ogólne
question: "Tell me everything"  # Zbyt długa odpowiedź
question: "Is it working?"  # Niejasne
```

## 🎓 Przykłady Użycia

### Przykład 1: Custom Error Detection
```yaml
error_detection_custom:
  - action: connect
  - action: find_and_click
    element: "Terminal"
  - action: wait
    seconds: 2
  - action: type
    text: "rm -rf /important_dir"
  - action: key
    key: enter
  - action: wait
    seconds: 2
  - action: analyze
    question: "Did an error occur? What type? Is it a permission error?"
    save_to: custom_error
  - action: disconnect
```

### Przykład 2: Form Auto-Fill
```yaml
smart_form_fill:
  - action: connect
  - action: find_and_click
    element: "Firefox"
  - action: wait
    seconds: 3
  - action: key
    key: ctrl+l
  - action: type
    text: "https://myform.com"
  - action: key
    key: enter
  - action: wait
    seconds: 3
  - action: analyze
    question: "How many text input fields are visible on this form?"
    save_to: field_count
  - action: find_and_click
    element: "first name field"
  - action: type
    text: "John"
  - action: key
    key: tab
  - action: type
    text: "Doe"
  - action: verify
    expected: "form contains entered name data"
  - action: disconnect
```

## 📖 Więcej Informacji

- [Remote Automation README](../README.md)
- [Architecture Documentation](architecture.md)
- [Contributing Guide](contributing.md)
- [Ollama Documentation](https://ollama.ai/docs)

## 🤝 Contributing

Masz pomysł na nowy AI-driven test? Zobacz [CONTRIBUTING.md](contributing.md)!
