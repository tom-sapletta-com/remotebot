# 🎬 Live Monitor - Test Guide

## ✅ Quick Test - Sprawdź Czy Działa

### 1. Uruchom Live Monitor

```bash
cd /home/tom/github/tom-sapletta-com/remotebot
make live-monitor
```

**Oczekiwany output:**
```
Starting Live Automation Monitor...
📺 Open: http://localhost:5000

 * Running on http://0.0.0.0:5000
```

### 2. Otwórz w Przeglądarce

```
http://localhost:5000
```

**Powinieneś zobaczyć:**
- 📋 Po lewej: "Live Automation Monitor" header z przyciskami
- 📺 Po prawej: "Live VNC Preview"
- Dropdown: "Select Scenario"

### 3. Test Połączenia

**Krok 1:** Kliknij **"Connect VNC"**

**Oczekiwany rezultat:**
- Status zmieni się na: "Status: Connected ✓" (zielony)
- Po prawej pojawi się live screenshot z VNC desktop
- Screenshot będzie się odświeżał co 1 sekundę

### 4. Test Ładowania Scenariusza

**Krok 2:** Z dropdown wybierz scenariusz

Przykład: `quick_test.yaml → quick_connection_test`

**Oczekiwany rezultat:**
- Po lewej pojawi się lista kroków:
  ```
  Step 1
  connect
  [▶ Execute]
  
  Step 2
  wait
  seconds: 2
  [▶ Execute]
  
  Step 3
  disconnect
  [▶ Execute]
  ```
- Przycisk "▶ Run All" stanie się aktywny (zielony)

### 5. Test Wykonania Pojedynczego Kroku

**Krok 3:** Kliknij **"▶ Execute"** przy Step 1 (connect)

**Oczekiwany rezultat:**
- Step 1 podświetli się na pomarańczowo z animacją pulsowania
- W konsoli przeglądarki (F12): "Executed step 1"
- Screenshot na prawej stronie może się zmienić

### 6. Test "Run All"

**Krok 4:** Kliknij **"▶ Run All"** w headerze

**Oczekiwany rezultat:**
- Potwierdzenie: "Execute all steps in scenario?"
- Po potwierdzeniu:
  - Każdy krok będzie podświetlany kolejno (pomarańczowy)
  - Screenshot będzie się automatycznie odświeżał
  - Gdy skończy, wszystkie kroki wrócą do normalnego stanu

### 7. Test z CV Detection

**Krok 5:** Wybierz: `cv_speed_test.yaml → cv_fast_detection`

**Krok 6:** Kliknij "▶ Execute" przy Step 3 (cv_detect)

**Oczekiwany rezultat:**
- Step wykona się w kilka milisekund
- Konsola pokaże: "Executed step 3"
- Screenshot pokaże aktualny stan VNC

---

## ✅ Test Checklist

Sprawdź czy wszystkie funkcje działają:

- [ ] Live Monitor startuje (port 5000)
- [ ] Interface ładuje się w przeglądarce
- [ ] "Connect VNC" - łączy z VNC desktop
- [ ] Live screenshot aktualizuje się co 1s
- [ ] Dropdown ładuje wszystkie scenariusze
- [ ] Po wyborze scenariusza - lista kroków się pokazuje
- [ ] Każdy krok ma przycisk "▶ Execute"
- [ ] Przycisk "▶ Run All" jest widoczny
- [ ] Klikając "Execute" - krok się wykonuje
- [ ] Podczas wykonywania - krok podświetlony
- [ ] Klikając "Run All" - wszystkie kroki wykonują się
- [ ] Screenshot automatycznie odświeża się podczas wykonywania
- [ ] Po zakończeniu - kroki wracają do normalnego stanu

---

## 🐛 Troubleshooting

### Problem: Port 5000 zajęty

**Rozwiązanie:**
```bash
# Zabij proces na porcie 5000
lsof -ti:5000 | xargs kill -9

# Lub zmień port w docker-compose.yml
ports:
  - "5001:5000"
```

### Problem: "No VNC Connection"

**Rozwiązanie:**
```bash
# Sprawdź czy VNC działa
make test-quick

# Restart VNC
docker-compose restart vnc-desktop

# Poczekaj 10s i spróbuj ponownie
sleep 10
```

### Problem: Przyciski "Execute" nie działają

**Sprawdź:**
1. Czy jesteś połączony (Status: Connected)?
2. Czy scenariusz jest załadowany?
3. Otwórz konsolę przeglądarki (F12) - czy są błędy?

**Rozwiązanie:**
```bash
# Restart Live Monitor
docker-compose restart automation-controller
make live-monitor
```

### Problem: Screenshot nie odświeża się

**Rozwiązanie:**
```bash
# Check VNC connection
make vnc
# Open: http://localhost:6080/vnc.html

# Jeśli VNC działa ale screenshot nie:
# Odśwież stronę (F5)
```

---

## 📊 Oczekiwane Performance

| Operacja | Czas | Notes |
|----------|------|-------|
| Connect VNC | <3s | First connection |
| Load scenario | <1s | Fast |
| Execute single step | Variable | Depends on action |
| - connect | ~1s | Quick |
| - cv_detect | ~0.01s | Milisekundy! |
| - wait | 1-5s | As defined |
| - AI analyze | 20-60s | Slow (AI) |
| Run All (quick_test) | ~5s | 3 steps |
| Run All (cv_fast_detection) | ~6s | With CV |
| Screenshot update | 1s | 1 FPS |

---

## 🎉 Sukces!

Jeśli wszystkie testy przeszły, Live Monitor jest **gotowy do użycia**!

**Możesz teraz:**
- 🐛 Debugować scenariusze krok po kroku
- ▶️ Wykonywać pojedyncze kroki
- 🎬 Uruchamiać całe scenariusze z "Run All"
- 📺 Oglądać live automation w real-time
- 🎯 Tworzyć nowe scenariusze i testować je natychmiast

---

## 🔗 Next Steps

### Wypróbuj Różne Scenariusze:

```bash
# CV Detection (super fast!)
Select: cv_speed_test.yaml → cv_fast_detection
Click: ▶ Run All
Watch: Milisecond detection!

# Auto-Login (CV)
Select: auto_login.yaml → cv_fast_login  
Click: ▶ Run All
Watch: Auto unlock!

# Diagnostics
Select: diagnostics.yaml → screen_diagnostics
Click: ▶ Run All
Watch: Screen analysis!
```

### Stwórz Własny Scenariusz:

1. Edit `/test_scenarios/my_scenario.yaml`
2. Refresh browser (F5)
3. Select your scenario from dropdown
4. Test with "Execute" buttons
5. Run with "▶ Run All"

---

## 📚 Dokumentacja

- **[LIVE_MONITOR_GUIDE.md](LIVE_MONITOR_GUIDE.md)** - Pełny przewodnik
- **[CV_DETECTION_GUIDE.md](CV_DETECTION_GUIDE.md)** - CV detection
- **[DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md)** - Troubleshooting

---

**Data:** 2025-10-18  
**Feature:** Live Monitor with Step Execution  
**Status:** ✅ Ready to Test!
