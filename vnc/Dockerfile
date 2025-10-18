FROM ubuntu:22.04

# Unikaj interakcji podczas instalacji
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV VNC_PORT=5901
ENV NO_VNC_PORT=6080
ENV VNC_PASSWORD=automation

# Podstawowe narzędzia i desktop environment
RUN apt-get update && apt-get install -y \
    # Desktop environment (lekki XFCE)
    xfce4 \
    xfce4-terminal \
    xfce4-goodies \
    dbus-x11 \
    # VNC Server
    tigervnc-standalone-server \
    tigervnc-common \
    # NoVNC (dostęp przez przeglądarkę)
    novnc \
    websockify \
    # Przeglądarki
    firefox \
    # Narzędzia
    nano \
    vim \
    wget \
    curl \
    git \
    htop \
    net-tools \
    iputils-ping \
    # Python i pip
    python3 \
    python3-pip \
    python3-dev \
    # Biblioteki graficzne
    libgl1-mesa-glx \
    libglib2.0-0 \
    # Fonty
    fonts-liberation \
    # File manager
    thunar \
    # Edytor tekstu
    mousepad \
    # Kalkulator
    galculator \
    # Viewer obrazków
    ristretto \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Zainstaluj Python dependencies dla automatyzacji
RUN pip3 install --no-cache-dir \
    pillow \
    requests \
    pynput \
    PyYAML

# Utwórz użytkownika
RUN useradd -m -s /bin/bash automation && \
    echo "automation:automation" | chpasswd && \
    usermod -aG sudo automation

# Przełącz na użytkownika
USER automation
WORKDIR /home/automation

# Utwórz katalog dla VNC
RUN mkdir -p /home/automation/.vnc

# Ustaw hasło VNC
RUN echo ${VNC_PASSWORD} | vncpasswd -f > /home/automation/.vnc/passwd && \
    chmod 600 /home/automation/.vnc/passwd

# Konfiguracja VNC
RUN echo "#!/bin/sh" > /home/automation/.vnc/xstartup && \
    echo "unset SESSION_MANAGER" >> /home/automation/.vnc/xstartup && \
    echo "unset DBUS_SESSION_BUS_ADDRESS" >> /home/automation/.vnc/xstartup && \
    echo "exec startxfce4" >> /home/automation/.vnc/xstartup && \
    chmod +x /home/automation/.vnc/xstartup

# Utwórz skrypt startowy
RUN echo "#!/bin/bash" > /home/automation/start_vnc.sh && \
    echo "vncserver :1 -geometry 1280x800 -depth 24 -localhost no" >> /home/automation/start_vnc.sh && \
    echo "websockify -D --web=/usr/share/novnc/ 6080 localhost:5901" >> /home/automation/start_vnc.sh && \
    echo "tail -f /home/automation/.vnc/*.log" >> /home/automation/start_vnc.sh && \
    chmod +x /home/automation/start_vnc.sh

# Utwórz przykładowe pliki testowe
RUN mkdir -p /home/automation/Desktop && \
    mkdir -p /home/automation/Documents && \
    mkdir -p /home/automation/test_files

# Przykładowy dokument testowy
RUN echo "# Test Document" > /home/automation/Documents/test.txt && \
    echo "This is a test document for automation." >> /home/automation/Documents/test.txt && \
    echo "Line 1: Important information" >> /home/automation/Documents/test.txt && \
    echo "Line 2: More data" >> /home/automation/Documents/test.txt

# Przykładowy skrypt bash do testowania
RUN echo "#!/bin/bash" > /home/automation/test_files/test_script.sh && \
    echo "echo 'Test script executed successfully'" >> /home/automation/test_files/test_script.sh && \
    echo "echo 'Current date:' \$(date)" >> /home/automation/test_files/test_script.sh && \
    echo "echo 'Current user:' \$(whoami)" >> /home/automation/test_files/test_script.sh && \
    chmod +x /home/automation/test_files/test_script.sh

# Przykładowy HTML do testowania przeglądarki
RUN echo '<!DOCTYPE html>' > /home/automation/test_files/test.html && \
    echo '<html><head><title>Test Page</title></head>' >> /home/automation/test_files/test.html && \
    echo '<body style="font-family: Arial; padding: 20px;">' >> /home/automation/test_files/test.html && \
    echo '<h1>Automation Test Page</h1>' >> /home/automation/test_files/test.html && \
    echo '<p>This is a test page for automation.</p>' >> /home/automation/test_files/test.html && \
    echo '<button id="testButton">Click Me</button>' >> /home/automation/test_files/test.html && \
    echo '<input type="text" id="testInput" placeholder="Enter text here">' >> /home/automation/test_files/test.html && \
    echo '<div id="result"></div>' >> /home/automation/test_files/test.html && \
    echo '</body></html>' >> /home/automation/test_files/test.html

# Utwórz skróty na pulpicie
RUN echo "[Desktop Entry]" > /home/automation/Desktop/Firefox.desktop && \
    echo "Version=1.0" >> /home/automation/Desktop/Firefox.desktop && \
    echo "Type=Application" >> /home/automation/Desktop/Firefox.desktop && \
    echo "Name=Firefox" >> /home/automation/Desktop/Firefox.desktop && \
    echo "Exec=firefox" >> /home/automation/Desktop/Firefox.desktop && \
    echo "Icon=firefox" >> /home/automation/Desktop/Firefox.desktop && \
    echo "Terminal=false" >> /home/automation/Desktop/Firefox.desktop && \
    chmod +x /home/automation/Desktop/Firefox.desktop

RUN echo "[Desktop Entry]" > /home/automation/Desktop/Terminal.desktop && \
    echo "Version=1.0" >> /home/automation/Desktop/Terminal.desktop && \
    echo "Type=Application" >> /home/automation/Desktop/Terminal.desktop && \
    echo "Name=Terminal" >> /home/automation/Desktop/Terminal.desktop && \
    echo "Exec=xfce4-terminal" >> /home/automation/Desktop/Terminal.desktop && \
    echo "Icon=utilities-terminal" >> /home/automation/Desktop/Terminal.desktop && \
    echo "Terminal=false" >> /home/automation/Desktop/Terminal.desktop && \
    chmod +x /home/automation/Desktop/Terminal.desktop

RUN echo "[Desktop Entry]" > /home/automation/Desktop/TextEditor.desktop && \
    echo "Version=1.0" >> /home/automation/Desktop/TextEditor.desktop && \
    echo "Type=Application" >> /home/automation/Desktop/TextEditor.desktop && \
    echo "Name=Text Editor" >> /home/automation/Desktop/TextEditor.desktop && \
    echo "Exec=mousepad" >> /home/automation/Desktop/TextEditor.desktop && \
    echo "Icon=accessories-text-editor" >> /home/automation/Desktop/TextEditor.desktop && \
    echo "Terminal=false" >> /home/automation/Desktop/TextEditor.desktop && \
    chmod +x /home/automation/Desktop/TextEditor.desktop

# Expose ports
EXPOSE 5901 6080

# Uruchom VNC server
CMD ["/home/automation/start_vnc.sh"]
