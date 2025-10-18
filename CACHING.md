# 🚀 Optymalizacja Cache'owania i Przechowywania Modeli

## 📦 Persistent Storage

### Modele Ollama
- **Volume**: `ollama-data` - trwałe przechowywanie modeli LLM
- **Ścieżka**: `/root/.ollama` w kontenerze
- **Korzyści**: Modele pobierane tylko raz, nie są usuwane przy restartach

### Cache Volumes
- **pip-cache**: Cache pakietów Python dla szybszego rebuildu
- **apt-cache**: Cache pakietów systemowych (planowane)

## ⚡ Docker Build Cache

### Włączony DOCKER_BUILDKIT
```bash
make build  # Używa cache
make build-no-cache  # Wymusza pełny rebuild
```

### Optymalizacje w Dockerfile
1. **Layer caching**: requirements.txt kopiowane przed kodem
2. **Pip cache**: `--mount=type=cache,target=/root/.cache/pip`
3. **Porządek warstw**: Dependencies przed application code

### .dockerignore
Wykluczono:
- `logs/`, `results/` - zmienne pliki
- `.git/`, `docs/` - niepotrzebne dla runtime
- `*test.py` - testy lokalne

## 🔧 Komendy Zarządzania

### Cache Management
```bash
make clean-cache     # Usuń cache (zostaw modele)
make clean-all       # Usuń wszystko (niebezpieczne!)
```

### Model Management
```bash
make models          # Lista zainstalowanych modeli
make backup-models   # Backup modeli do pliku
make restore-models  # Instrukcje przywracania
```

### Volume Information
```bash
make volumes         # Status wszystkich volumes
docker volume ls     # Lista wszystkich volumes
```

## 📊 Monitorowanie Rozmiaru

### Sprawdź rozmiar volumes
```bash
docker system df -v
docker volume inspect remote-automation_ollama-data
```

### Sprawdź zajętość dysku
```bash
du -sh ~/.local/share/docker/volumes/remote-automation_ollama-data/
```

## 🚨 Najlepsze Praktyki

### ✅ DO
- Regularnie sprawdzaj `make volumes`
- Rób backup modeli przed update'ami
- Używaj `make build` (z cache) dla rozwoju
- Monitoruj rozmiar volumes

### ❌ DON'T
- Nie używaj `make clean-all` bez backupu
- Nie usuwaj `ollama-data` volume bez potrzeby
- Nie kopiuj dużych plików do kontenerów
- Nie ignoruj ostrzeżeń o miejscu na dysku

## 🔄 Workflow Rozwoju

1. **Pierwszy setup**:
   ```bash
   make build
   make up
   # Modele pobierają się automatycznie
   ```

2. **Codzienny rozwój**:
   ```bash
   make build  # Szybko dzięki cache
   make up
   ```

3. **Cleanup co jakiś czas**:
   ```bash
   make clean-cache  # Usuń cache, zostaw modele
   ```

4. **Backup przed update'ami**:
   ```bash
   make backup-models
   ```

## 📈 Korzyści

- **60-90%** szybszy rebuild kontenerów
- **Brak ponownego pobierania** modeli LLM (4-8GB)
- **Szybsze instalowanie** pakietów Python
- **Persistent storage** - bezpieczne restarty
- **Łatwe zarządzanie** przez make commands

## 🔍 Troubleshooting

### Problem: Modele znikają po restarcie
```bash
# Sprawdź czy volume istnieje
make volumes

# Sprawdź czy jest podmontowany
docker-compose exec ollama ls -la /root/.ollama
```

### Problem: Cache nie działa
```bash
# Sprawdź DOCKER_BUILDKIT
echo $DOCKER_BUILDKIT  # powinno być "1"

# Wymuś rebuild
make build-no-cache
```

### Problem: Brak miejsca na dysku
```bash
# Wyczyść niepotrzebne dane Docker
docker system prune -af

# Usuń stare volumes
docker volume prune
```
