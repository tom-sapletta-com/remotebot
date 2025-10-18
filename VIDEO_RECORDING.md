# 🎬 Nagrywanie Testów Wideo

Wszystkie testy automatyzacji mogą być nagrywane do plików MP4 w celu archiwizacji i późniejszej analizy.

## 📹 Funkcjonalność

- **Automatyczne nagrywanie**: Każdy test scenariusza jest nagrywany do osobnego pliku MP4
- **Kompresja**: Używamy kodeka `mp4v` z optymalizacją rozmiaru
- **10 FPS**: Standardowa częstotliwość klatek dla oszczędności miejsca
- **Rozdzielczość**: 1280x720 (HD Ready)
- **Lokalizacja**: `results/videos/`

## 🚀 Użycie

### Podstawowe testy z nagrywaniem

```bash
# Test podstawowy z nagrywaniem
make test-basic

# Test Firefox z nagrywaniem
make test-firefox

# Test terminala z nagrywaniem
make test-terminal
```

### Testy bez nagrywania (szybsze)

```bash
# Bez nagrywania - dla szybszego uruchomienia
make test-no-recording
```

### Ręczne uruchomienie scenariusza

```bash
# Z nagrywaniem (domyślnie)
docker-compose exec automation-controller python3 run_scenario.py test_scenarios/test_basic.yaml test_connection

# Bez nagrywania
docker-compose exec automation-controller python3 run_scenario.py test_scenarios/test_basic.yaml test_connection --no-recording

# Lista dostępnych scenariuszy
make list-scenarios
```

## 📊 Statystyki Nagrania

Po zakończeniu testu wyświetlane są statystyki:

```
✅ Nagrywanie zakończone:
   📁 Plik: results/videos/test_connection_20251018_183045.mp4
   🎬 Klatki: 120
   ⏱️  Czas: 12.34s
   💾 Rozmiar: 2.45 MB
```

## 🔧 Konfiguracja

Parametry nagrywania można dostosować w `automation/screen_recorder.py`:

```python
recorder = ScreenRecorder(
    output_dir="results/videos",  # Katalog wyjściowy
    fps=10,                        # Klatki na sekundę (5-30)
    codec="mp4v",                  # Kodek ('mp4v', 'avc1', 'h264')
    quality=80                     # Jakość 0-100
)
```

### Dostosowanie rozdzielczości

W `run_scenario.py` lub bezpośrednio w kodzie:

```python
recorder.start_recording(
    scenario_name="my_test",
    capture_func=controller.capture_screen,
    resolution=(1920, 1080)  # Full HD
)
```

## 📦 Zależności

Wymagane pakiety (już zawarte w `requirements.txt`):

- `opencv-python>=4.8.0` - Przetwarzanie i kodowanie wideo
- `numpy>=1.21.0` - Operacje na macierzach (wymagane przez OpenCV)
- `pillow>=10.0.0` - Obsługa obrazów

## 🎯 Przykłady

### Context Manager (programowe użycie)

```python
from screen_recorder import record_test

# Automatyczne rozpoczęcie i zakończenie nagrywania
with record_test("my_scenario", controller.capture_screen):
    controller.connect()
    controller.click(100, 100)
    controller.type_text("hello")
    controller.disconnect()
```

### Ręczna kontrola

```python
from screen_recorder import ScreenRecorder

recorder = ScreenRecorder()

# Rozpocznij
recorder.start_recording("test_name", controller.capture_screen)

# Wykonaj akcje...
controller.connect()
# ...

# Zatrzymaj i pobierz statystyki
stats = recorder.stop_recording()
print(f"Nagranie zapisane: {stats['file']}")
```

## 📁 Struktura Plików

```
results/
└── videos/
    ├── test_connection_20251018_183045.mp4
    ├── test_firefox_20251018_183102.mp4
    └── test_terminal_20251018_183156.mp4
```

Format nazwy: `{scenario_name}_{YYYYMMDD_HHMMSS}.mp4`

## 🗑️ Zarządzanie Nagraniami

### Usuwanie starych nagrań

```bash
# Usuń nagrania starsze niż 7 dni
find results/videos -name "*.mp4" -mtime +7 -delete

# Usuń wszystkie nagrania
rm -rf results/videos/*.mp4
```

### Archiwizacja

```bash
# Utwórz archiwum z nagraniami
tar -czf test_videos_$(date +%Y%m%d).tar.gz results/videos/

# Przenieś do backups
mv test_videos_*.tar.gz backups/
```

## ⚡ Optymalizacja

### Zmniejszenie rozmiaru plików

1. **Niższa częstotliwość klatek**: `fps=5` (mniejsze pliki)
2. **Niższa rozdzielczość**: `resolution=(800, 600)`
3. **Lepszy kodek**: `codec='h264'` (jeśli dostępny)

### Zwiększenie jakości

1. **Wyższa częstotliwość**: `fps=30` (płynniejsze wideo)
2. **Wyższa rozdzielczość**: `resolution=(1920, 1080)`
3. **Wyższa jakość**: `quality=95`

## 🐛 Troubleshooting

### Problem: "screen_recorder nie jest dostępny"

Przebuduj kontenery z nowymi zależnościami:

```bash
make rebuild
```

### Problem: Brak miejsca na dysku

Sprawdź rozmiar katalogu:

```bash
du -sh results/videos/
```

Usuń stare nagrania lub zmniejsz `fps` i `quality`.

### Problem: Wideo jest puste lub uszkodzone

- Sprawdź czy VNC działa: `make status`
- Upewnij się że `controller.capture_screen()` zwraca prawidłowy obraz
- Sprawdź logi podczas nagrywania

## 📈 Przykładowe Rozmiary

| Czas testu | FPS | Rozdzielczość | Rozmiar |
|-----------|-----|---------------|---------|
| 10s       | 10  | 1280x720      | ~2 MB   |
| 30s       | 10  | 1280x720      | ~6 MB   |
| 60s       | 10  | 1280x720      | ~12 MB  |
| 60s       | 30  | 1920x1080     | ~40 MB  |

## 🔗 Powiązane

- [README.md](README.md) - Główna dokumentacja
- [CACHING.md](CACHING.md) - Optymalizacja Docker
- [test_scenarios/](test_scenarios/) - Scenariusze testowe
