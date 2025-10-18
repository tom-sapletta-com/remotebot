# 🔍 Diagnostics Guide - Rozwiązywanie Problemów

## 🎯 Kiedy Użyć Diagnostyki?

### Objawy Problemów:

1. **Ekran jest pusty/czarny**
   ```
   CV Detection wynik:
   Dialog: False
   Buttons: 0
   Windows: 0
   ```

2. **VNC połączenie niepewne**
   - Łączy się ale nic nie widać
   - Timeout podczas operacji
   
3. **Lock screen nie wykryty**
   - AI nie znajduje okna logowania
   - CV nie znajduje text field

4. **Desktop wydaje się nie być gotowy**
   - Brak ikon
   - Pusty ekran po połączeniu

---

## 🚀 Quick Diagnostics

### 1. Screen Check (Najszybszy)

```bash
make test-diag-screen
```

**Output:**
```
🔍 CV Detection (fast)...
✓ Analysis done in 3.8ms

⚠️  Screen Issue Detected:
  Brightness: 15.3/255          # Bardzo ciemny!
  Edge count: 234               # Mało krawędzi
  Is blank: True                # Ekran pusty
  Problem: Screen is blank/black - possible lock screen or VNC not connected

Dialog: False
Buttons: 0
Text field: False
Windows: 0
```

**Interpretacja:**
- **Brightness < 30** → Ekran jest czarny/bardzo ciemny
- **Edge count < 500** → Bardzo mało contentu
- **Is blank: True** → Problem z VNC lub lock screen

---

## 📊 Diagnostyka Szczegółowa

### Brightness (Jasność)

| Wartość | Interpretacja | Możliwa Przyczyna |
|---------|---------------|-------------------|
| **0-30** | Czarny ekran | VNC nie połączony, screensaver |
| **30-50** | Bardzo ciemny | Lock screen z ciemnym tłem |
| **50-100** | Ciemny | Desktop z ciemnym motywem |
| **100-150** | Normalny | Typowy desktop |
| **150-200** | Jasny | Desktop z jasnym motywem |
| **200-255** | Bardzo jasny | Białe okno, jasne tło |

### Edge Count (Liczba Krawędzi)

| Wartość | Interpretacja | Możliwa Przyczyna |
|---------|---------------|-------------------|
| **0-500** | Prawie brak contentu | Pusty/czarny ekran, VNC problem |
| **500-1000** | Mało contentu | Minimalistyczny desktop, lock screen |
| **1000-5000** | Normalny content | Typowy desktop z kilkoma ikonami |
| **5000-20000** | Dużo contentu | Desktop z wieloma oknami/ikonami |
| **>20000** | Bardzo dużo contentu | Wiele okien, complex UI |

---

## 🔧 Scenariusze Diagnostyczne

### 1. Screen Diagnostics

```bash
make test-diag-screen
```

**Co robi:**
- Łączy się z VNC
- Wykonuje CV detection z diagnostyką
- Pokazuje:
  - Jasność ekranu
  - Liczba krawędzi
  - Czy ekran pusty
  - Możliwy problem

**Czas:** ~5 sekund

### 2. VNC Connection Check

```bash
make test-diag-vnc
```

**Co robi:**
- Sprawdza VNC 2 razy (co 2s)
- Porównuje wyniki
- Jeśli oba testy pokazują blank screen → Problem z VNC

**Użyj gdy:**
- Podejrzewasz problem z VNC
- Desktop powinien być widoczny ale nie jest

### 3. Lock Screen Detection

```bash
make test-diag-lock
```

**Co robi:**
- Wykrywa czy ekran jest zablokowany
- Sprawdza brightness + dialog detection
- Określa typ lock screen

**Kryteria lock screen:**
```
brightness < 50 AND has_dialog = True
→ Lock screen z oknem logowania

brightness < 30 AND is_blank = True
→ Screensaver lub VNC problem
```

### 4. Desktop Ready Check

```bash
make test-diag-ready
```

**Co robi:**
- Sprawdza 3 razy co 2 sekundy
- Monitoruje czy desktop się ładuje
- Wykrywa czy system jest gotowy

**Desktop gotowy gdy:**
```
window_count > 0 OR edge_count > 5000
```

### 5. Full System Check (CV + AI)

```bash
make test-diag-full
```

**Co robi:**
- CV diagnostyka (szybka)
- Screenshot
- AI weryfikacja (jeśli CV wykryje problem)

**Czas:** ~30-60 sekund (AI)

**Użyj gdy:**
- CV pokazuje problemy ale nie jesteś pewien co
- Potrzebujesz AI do opisania co widać

### 6. Auto Recovery

```bash
make test-diag-recovery
```

**Co robi:**
- Sprawdza stan ekranu
- Jeśli wykryje lock screen → próbuje odblokować
- Wpisuje hasło "automation"
- Sprawdza ponownie czy się powiodło

**Użyj gdy:**
- Lock screen blokuje testy
- Chcesz automatycznie odblokować

---

## 🎯 Typowe Problemy i Rozwiązania

### Problem 1: Czarny Ekran

**Objawy:**
```
Brightness: 5.2/255
Edge count: 45
Is blank: True
Problem: Screen is blank/black
```

**Możliwe przyczyny:**
1. VNC nie połączony poprawnie
2. Screensaver aktywny
3. Monitor wyłączony
4. Desktop nie uruchomiony

**Rozwiązanie:**
```bash
# Sprawdź VNC
make test-diag-vnc

# Sprawdź czy VNC działa
make vnc
# Otwórz: http://localhost:6080/vnc.html

# Restart VNC
docker-compose restart vnc-desktop

# Poczekaj i sprawdź ponownie
sleep 10
make test-diag-screen
```

### Problem 2: Lock Screen

**Objawy:**
```
Brightness: 45.3/255
Edge count: 1234
Has dialog: True
Problem: Possible lock screen
```

**Rozwiązanie:**
```bash
# Auto-unlock
make test-diag-recovery

# Lub manualnie z CV
make test-cv-unlock

# Lub z AI
make test-auto-login
```

### Problem 3: Desktop Się Ładuje

**Objawy:**
```
Check 1: edge_count: 234
Check 2: edge_count: 567
Check 3: edge_count: 1234
```

Edge count rośnie → Desktop się ładuje

**Rozwiązanie:**
```bash
# Poczekaj dłużej
make test-diag-ready

# Jeśli nadal nisko - sprawdź VNC
make vnc
```

### Problem 4: VNC Timeout

**Objawy:**
```
Error: Connection timeout
Could not connect to vnc-desktop:5901
```

**Rozwiązanie:**
```bash
# Sprawdź status
make status

# Restart VNC
docker-compose restart vnc-desktop

# Poczekaj 10s
sleep 10

# Sprawdź ponownie
make test-diag-vnc
```

---

## 📊 Example Diagnostics Output

### Healthy Desktop

```bash
$ make test-diag-screen

🔍 CV Detection (fast)...
✓ Analysis done in 3.8ms
  Screen brightness: 128.5/255      # ✅ Normalny
  Content detected: True            # ✅ Jest content
  Dialog: False
  Buttons: 0
  Text field: False
  Windows: 3                        # ✅ 3 okna
```

### Lock Screen

```bash
$ make test-diag-screen

🔍 CV Detection (fast)...
✓ Analysis done in 3.6ms

⚠️  Screen Issue Detected:
  Brightness: 48.2/255              # ⚠️ Ciemny
  Edge count: 1456                  # ⚠️ Mało contentu
  Is blank: False
  Problem: Screen is very dark - possible screensaver or lock screen

  Dialog: True                      # ✅ Wykryto dialog!
  Buttons: 2                        # ✅ Przyciski (Cancel, Unlock)
  Text field: True                  # ✅ Pole hasła
  Windows: 1                        # Dialog window
```

**Akcja:** Użyj `make test-cv-unlock` lub `make test-diag-recovery`

### VNC Problem

```bash
$ make test-diag-screen

🔍 CV Detection (fast)...
✓ Analysis done in 3.9ms

⚠️  Screen Issue Detected:
  Brightness: 0.0/255               # ❌ Całkowicie czarny
  Edge count: 0                     # ❌ Zero krawędzi
  Is blank: True                    # ❌ Pusty
  Problem: Screen is blank/black - possible lock screen or VNC not connected

  Dialog: False
  Buttons: 0
  Text field: False
  Windows: 0
```

**Akcja:** 
1. Sprawdź `make status`
2. Otwórz `make vnc` w przeglądarce
3. Restart `docker-compose restart vnc-desktop`

---

## 🔍 Advanced Diagnostics

### Check Specific Variables

Po uruchomieniu diagnostyki, sprawdź zmienne:

```yaml
📊 Zebrane dane:
  diag_diagnostics_is_blank: True/False
  diag_diagnostics_mean_brightness: 0-255
  diag_diagnostics_edge_count: liczba
  diag_diagnostics_has_content: True/False
  diag_diagnostics_possible_issue: opis lub None
```

### Custom Thresholds

Jeśli chcesz dostosować progi:

Edit `/automation/cv_detection.py`:
```python
# Próg dla blank screen (default: 30)
diagnostics['is_blank'] = mean_brightness < 30  # Zmień na 40 dla strict

# Próg dla content detection (default: 1000)
diagnostics['has_content'] = edge_count > 1000  # Zmień na 2000 dla strict
```

---

## 📚 Quick Reference

### Commands

```bash
# Quick checks
make test-diag-screen    # Szybkie sprawdzenie (5s)
make test-diag-lock      # Wykryj lock screen (5s)

# Detailed checks
make test-diag-vnc       # VNC connection (10s)
make test-diag-ready     # Desktop ready (10s)
make test-diag-full      # Full check with AI (60s)

# Recovery
make test-diag-recovery  # Auto-unlock (10s)

# Lists
make list-diag-tests     # Zobacz wszystkie
```

### Interpretation Guide

**Dobry stan:**
- Brightness: 100-200
- Edge count: >5000
- Is blank: False
- Has content: True
- Windows: >0

**Lock screen:**
- Brightness: 30-100
- Edge count: 1000-5000
- Dialog: True
- Text field: True

**VNC problem:**
- Brightness: <30
- Edge count: <500
- Is blank: True
- Everything else: False/0

---

## 🎯 Best Practices

### 1. Zawsze Sprawdź Najpierw

```bash
# Przed uruchomieniem testów:
make test-diag-screen
```

### 2. Jeśli Problemy

```bash
# Użyj pełnej diagnostyki:
make test-diag-full
```

### 3. Auto-Recovery

```bash
# Dodaj na początku scenariuszy:
- action: cv_detect
  save_to: initial_check

# Jeśli is_blank lub has_dialog:
- action: cv_find_unlock
  click: true
```

---

## 🎉 System Gotowy!

**Diagnostyka pozwala:**
- ✅ Wykryć problemy VNC
- ✅ Znaleźć lock screen
- ✅ Zweryfikować połączenie
- ✅ Auto-recovery
- ✅ Wszystko w milisekundach!

**Dokumentacja:**
- Ten plik - Diagnostics guide
- [CV_DETECTION_GUIDE.md](CV_DETECTION_GUIDE.md) - CV detection
- [WORKING_TESTS_GUIDE.md](WORKING_TESTS_GUIDE.md) - Troubleshooting

---

**Data:** 2025-10-18  
**Feature:** Screen Diagnostics  
**Speed:** 3-5ms (CV detection)  
**Status:** ✅ Production-Ready
