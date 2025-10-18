#!/usr/bin/env python3
"""
Quick VNC Connection Test
Szybki test połączenia VNC - 5 sekund
"""

import sys
import time
from pathlib import Path

# Dodaj katalog automation do ścieżki
sys.path.insert(0, str(Path(__file__).parent))

from remote_automation import RemoteController

def main():
    """Szybki test połączenia"""
    try:
        print("🔌 Łączenie z VNC...")
        controller = RemoteController(
            protocol='vnc',
            host='vnc-desktop',
            port=5901,
            password='automation'
        )
        
        controller.connect()
        print("✓ Połączono z vnc-desktop:5901")
        
        print("⏳ Czekam 2 sekundy...")
        time.sleep(2)
        
        controller.disconnect()
        print("✓ Rozłączono")
        print("✅ Test zakończony pomyślnie!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
