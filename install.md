# 📦 Instalacja - Remote Automation Environment

Szczegółowe instrukcje instalacji dla różnych systemów operacyjnych.

## 📑 Spis treści

- [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
- [Linux (Fedora/RHEL)](#linux-fedorarhel)
- [macOS](#macos)
- [Windows (WSL2)](#windows-wsl2)
- [Docker Desktop](#docker-desktop)
- [Weryfikacja instalacji](#weryfikacja-instalacji)

---

## Linux (Ubuntu/Debian)

### 1. Zainstaluj Docker

```bash
# Aktualizuj system
sudo apt-get update
sudo apt-get upgrade -y

# Zainstaluj wymagane pakiety
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Dodaj klucz GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Dodaj repozytorium Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Zainstaluj Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER

# Zaloguj się ponownie lub wykonaj:
newgrp docker

# Sprawdź instalację
docker --version
docker compose version
```

### 2. Zainstaluj dodatkowe narzędzia

```bash
# Python i pip (opcjonalne, dla lokalnych testów)
sudo apt-get install -y python3 python3-pip

# VNC viewer (opcjonalnie)
sudo apt-get install -y tigervnc-viewer

# Make (dla Makefile)
sudo apt-get install -y make

# Git
sudo apt-get install -y git
```

### 3. Pobierz projekt

```bash
# Sklonuj repozytorium
git clone <repository-url>
cd remote-automation

# Lub pobierz ZIP
wget <download-url>/remote-automation.zip
unzip remote-automation.zip
cd remote-automation
```

### 4. Uruchom setup

```bash
chmod +x setup.sh
./setup.sh

# Zbuduj obrazy
make build

# Uruchom środowisko
make up
```

---

## Linux (Fedora/RHEL)

### 1. Zainstaluj Docker

```bash
# Usuń stare wersje (jeśli są)
sudo dnf remove docker \
                docker-client \
                docker-client-latest \
                docker-common \
                docker-latest \
                docker-latest-logrotate \
                docker-logrotate \
                docker-selinux \
                docker-engine-selinux \
                docker-engine

# Zainstaluj dnf-plugins-core
sudo dnf -y install dnf-plugins-core

# Dodaj repozytorium Docker
sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo

# Zainstaluj Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Uruchom Docker
sudo systemctl start docker
sudo systemctl enable docker

# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER
newgrp docker

# Sprawdź instalację
docker --version
docker compose version
```

### 2. Zainstaluj dodatkowe narzędzia

```bash
# Python i pip
sudo dnf install -y python3 python3-pip

# VNC viewer
sudo dnf install -y tigervnc

# Make
sudo dnf install -y make

# Git
sudo dnf install -y git
```

### 3. Dalsze kroki

Jak w sekcji Ubuntu - pobierz projekt i uruchom setup.

---

## macOS

### 1. Zainstaluj Docker Desktop

**Opcja A: Pobierz instalator**

1. Wejdź na: https://www.docker.com/products/docker-desktop
2. Pobierz Docker Desktop dla Mac (Intel lub Apple Silicon)
3. Otwórz pobrany `.dmg` i przeciągnij do Applications
4. Uruchom Docker Desktop z Applications
5. Poczekaj na pełne uruchomienie (ikona w menu bar)

**Opcja B: Homebrew**

```bash
# Zainstaluj Homebrew (jeśli nie masz)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Zainstaluj Docker Desktop
brew install --cask docker

# Uruchom Docker Desktop
open /Applications/Docker.app
```

### 2. Konfiguracja Docker Desktop

1. Otwórz Docker Desktop
2. Preferences → Resources → Advanced
3. Ustaw co najmniej:
   - **Memory: 4GB** (więcej dla większych modeli)
   - **CPUs: 2** (więcej dla szybszego działania)
   - **Disk: 20GB**
4. Apply & Restart

### 3. Zainstaluj dodatkowe narzędzia

```bash
# Homebrew tools
brew install make
brew install git
brew install python3

# VNC viewer (opcjonalnie)
brew install --cask vnc-viewer
```

### 4. Pobierz projekt

```bash
# Sklonuj
git clone <repository-url>
cd remote-automation

# Lub pobierz ZIP przez przeglądarkę i rozpakuj
```

### 5. Uruchom setup

```bash
chmod +x setup.sh
./setup.sh

# Zbuduj obrazy
make build

# Uruchom
make up
```

### macOS specyficzne uwagi

- Docker Desktop musi działać cały czas
- Pierwszy build może zająć więcej czasu
- noVNC (przeglądarka) może być wolniejsze niż natywny VNC client

---

## Windows (WSL2)

### 1. Włącz WSL2

```powershell
# Uruchom PowerShell jako Administrator

# Włącz WSL
wsl --install

# Restartuj komputer

# Po restarcie, ustaw WSL2 jako domyślny
wsl --set-default-version 2

# Zainstaluj Ubuntu
wsl --install -d Ubuntu
```

### 2. Zainstaluj Docker Desktop

1. Pobierz: https://www.docker.com/products/docker-desktop
2. Zainstaluj Docker Desktop
3. W Settings → General → zaznacz "Use WSL 2 based engine"
4. W Settings → Resources → WSL Integration → włącz dla Ubuntu
5. Apply & Restart

### 3. W WSL2 (Ubuntu)

```bash
# Uruchom terminal Ubuntu (Windows Terminal lub WSL)

# Aktualizuj system
sudo apt-get update
sudo apt-get upgrade -y

# Zainstaluj narzędzia
sudo apt-get install -y make git python3 python3-pip

# Sprawdź Docker
docker --version
docker compose version

# Jeśli nie działa, sprawdź czy Docker Desktop działa w Windows
```

### 4. Pobierz projekt

```bash
# W WSL2 terminal

# Utwórz katalog w home
cd ~
mkdir -p projects
cd projects

# Sklonuj
git clone <repository-url>
cd remote-automation

# Lub skopiuj z Windows
# cp -r /mnt/c/Users/TwojeImię/Downloads/remote-automation .
```

### 5. Uruchom setup

```bash
chmod +x setup.sh
./setup.sh

make build
make up
```

### Windows specyficzne uwagi

- Zawsze pracuj w WSL2, nie w natywnym Windows
- Docker Desktop musi działać w Windows
- Pliki przechowuj w systemie plików WSL2 (`~`) nie w `/mnt/c/`
- Dostęp przez przeglądarkę: `http://localhost:6080` działa zarówno z WSL jak i Windows

---

## Docker Desktop (uniwersalne)

Jeśli używasz Docker Desktop na dowolnym systemie:

### Konfiguracja zasobów

1. Docker Desktop → Preferences/Settings
2. Resources → Advanced
3. **Minimum:**
   - Memory: 4GB
   - CPUs: 2
   - Disk: 20GB
4. **Rekomendowane:**
   - Memory: 8GB
   - CPUs: 4
   - Disk: 30GB

### Weryfikacja

```bash
docker info | grep -i memory
docker info | grep -i cpus
```

---

## Weryfikacja instalacji

Po instalacji, zweryfikuj wszystko:

### 1. Sprawdź Docker

```bash
docker --version
# Oczekiwane: Docker version 20.10+ lub nowszy

docker compose version
# Oczekiwane: Docker Compose version v2.0+ lub nowszy

docker ps
# Powinno działać bez błędów
```

### 2. Sprawdź uprawnienia

```bash
# Linux: sprawdź czy jesteś w grupie docker
groups
# Powinno zawierać 'docker'

# Jeśli nie, wykonaj:
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Test podstawowy

```bash
docker run hello-world
```

Powinno wyświetlić komunikat powitalny od Docker.

### 4. Sprawdź make

```bash
make --version
# Powinno wyświetlić wersję Make

# Jeśli nie masz make:
# Ubuntu/Debian: sudo apt-get install make
# macOS: brew install make
# Fedora: sudo dnf install make
```

### 5. Sprawdź Git

```bash
git --version
```

### 6. Sprawdź Python (opcjonalnie)

```bash
python3 --version
pip3 --version
```

---

## Następne kroki

Po pomyślnej instalacji:

1. **Przejdź do [QUICK_START.md](QUICK_START.md)**
2. Uruchom setup: `./setup.sh`
3. Zbuduj obrazy: `make build`
4. Uruchom środowisko: `make up`
5. Otwórz przeglądarkę: http://localhost:6080/vnc.html

---

## Rozwiązywanie problemów instalacji

### Problem: "permission denied" przy Docker

```bash
# Linux: dodaj się do grupy docker
sudo usermod -aG docker $USER
newgrp docker

# Lub użyj sudo
sudo docker ps
```

### Problem: "Cannot connect to Docker daemon"

```bash
# Linux: uruchom Docker
sudo systemctl start docker
sudo systemctl enable docker

# macOS/Windows: upewnij się że Docker Desktop działa
```

### Problem: Docker Compose nie działa

```bash
# Sprawdź czy masz v2 (plugin)
docker compose version

# Jeśli masz v1 (standalone)
docker-compose version

# Jeśli żadne nie działa, zainstaluj plugin
# Ubuntu:
sudo apt-get install docker-compose-plugin
```

### Problem: WSL2 nie działa

```powershell
# Windows PowerShell (Administrator)

# Sprawdź wersję WSL
wsl --list --verbose

# Powinno pokazać version 2
# Jeśli version 1:
wsl --set-version Ubuntu 2

# Jeśli błąd, zainstaluj kernel update:
# https://aka.ms/wsl2kernel
```

### Problem: Brak miejsca na dysku

```bash
# Sprawdź zużycie
docker system df

# Wyczyść nieużywane zasoby
docker system prune -a

# Uwolni przestrzeń używaną przez:
# - Zatrzymane kontenery
# - Nieużywane obrazy
# - Nieużywane volumes
# - Build cache
```

### Problem: Wolne działanie

1. **Zwiększ zasoby Docker Desktop**
   - Memory: 8GB+
   - CPUs: 4+

2. **Użyj lżejszego modelu**
   ```bash
   make pull-model-small  # moondream zamiast llava
   ```

3. **Zamknij inne aplikacje**

4. **Sprawdź czy masz SSD** (nie HDD)

---

## Wymagania minimalne

| Komponent | Minimum | Rekomendowane |
|-----------|---------|---------------|
| RAM | 4GB wolne | 8GB wolne |
| CPU | 2 rdzenie | 4 rdzenie |
| Dysk | 10GB wolne | 20GB wolne |
| System | Ubuntu 20.04+, macOS 11+, Windows 10+ | Ubuntu 22.04+, macOS 12+, Windows 11 |
| Docker | 20.10+ | 24.0+ |

---

## Wsparcie

Jeśli masz problemy z instalacją:

1. Sprawdź [QUICK_START.md](QUICK_START.md) - Rozwiązywanie problemów
2. Sprawdź [DOCKER_README.md](DOCKER_README.md) - Szczegóły Docker
3. Sprawdź logi: `make logs`
4. Uruchom diagnostykę: `make check-docker`

---

**Powodzenia z instalacją! 🚀**
