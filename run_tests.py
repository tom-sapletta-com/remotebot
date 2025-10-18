#!/usr/bin/env python3
"""
Run Tests wrapper - uruchamia test_suite.py
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Uruchom test suite"""
    
    # Sprawdź czy test_suite.py istnieje
    test_suite_path = Path(__file__).parent / "test_suite.py"
    if not test_suite_path.exists():
        print("❌ Błąd: test_suite.py nie istnieje")
        return 1
    
    # Uruchom test_suite.py z argumentami
    cmd = [sys.executable, str(test_suite_path)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 Testy przerwane przez użytkownika")
        return 1
    except Exception as e:
        print(f"❌ Błąd uruchamiania testów: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
