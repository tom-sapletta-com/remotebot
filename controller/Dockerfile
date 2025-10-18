FROM python:3.11-slim

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    # VNC client tools
    tigervnc-viewer \
    # Narzędzia sieciowe
    netcat-traditional \
    curl \
    wget \
    # Narzędzia do debugowania
    vim \
    less \
    procps \
    # Zależności podstawowe
    python3-dev \
    python3-setuptools \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Zainstaluj Python dependencies - bez pynput która nie działa w kontenerach
RUN pip install --no-cache-dir \
    pillow \
    requests \
    PyYAML \
    vncdotool \
    pytest \
    pytest-html

# Utwórz katalog aplikacji
WORKDIR /app

# Skopiuj pliki automatyzacji
COPY automation/ /app/
COPY test_scenarios/ /app/test_scenarios/

# Utwórz katalogi
RUN mkdir -p /app/results /app/shared /app/logs

# Skrypt do czekania na usługi
RUN echo '#!/bin/bash' > /app/wait-for-services.sh && \
    echo 'echo "Waiting for VNC Desktop..."' >> /app/wait-for-services.sh && \
    echo 'until nc -z vnc-desktop 5901; do sleep 1; done' >> /app/wait-for-services.sh && \
    echo 'echo "VNC Desktop is ready!"' >> /app/wait-for-services.sh && \
    echo 'echo "Waiting for Ollama..."' >> /app/wait-for-services.sh && \
    echo 'until curl -f http://ollama:11434/api/tags; do sleep 2; done' >> /app/wait-for-services.sh && \
    echo 'echo "Ollama is ready!"' >> /app/wait-for-services.sh && \
    echo 'echo "All services are ready!"' >> /app/wait-for-services.sh && \
    chmod +x /app/wait-for-services.sh

# Skrypt pomocniczy do testów
RUN echo '#!/bin/bash' > /app/run-test.sh && \
    echo 'echo "Starting automation test..."' >> /app/run-test.sh && \
    echo './wait-for-services.sh' >> /app/run-test.sh && \
    echo 'python3 remote_automation.py "$@"' >> /app/run-test.sh && \
    chmod +x /app/run-test.sh

# Domyślna komenda
CMD ["/bin/bash"]
