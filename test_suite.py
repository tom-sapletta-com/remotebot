#!/usr/bin/env python3
"""
Test Suite dla Remote Automation
Uruchamia kompletne testy środowiska Docker
"""

import time
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

class TestRunner:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def info(self, msg):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")
    
    def success(self, msg):
        print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")
        
    def error(self, msg):
        print(f"{Colors.RED}[✗]{Colors.NC} {msg}")
        
    def warning(self, msg):
        print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")
    
    def run_command(self, cmd, check=True):
        """Uruchom komendę shell"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if check and result.returncode != 0:
                self.error(f"Komenda nie powiodła się: {cmd}")
                self.error(f"Output: {result.stderr}")
                return None
            return result
        except subprocess.TimeoutExpired:
            self.error(f"Timeout dla komendy: {cmd}")
            return None
        except Exception as e:
            self.error(f"Błąd wykonania komendy: {e}")
            return None
    
    def test_docker_running(self):
        """Test 1: Sprawdź czy Docker działa"""
        self.info("Test 1: Sprawdzanie Docker...")
        
        result = self.run_command("docker ps", check=False)
        if result and result.returncode == 0:
            self.success("Docker działa")
            return True
        else:
            self.error("Docker nie działa lub nie jest dostępny")
            return False
    
    def test_containers_running(self):
        """Test 2: Sprawdź czy kontenery są uruchomione"""
        self.info("Test 2: Sprawdzanie kontenerów...")
        
        containers = ['automation-vnc', 'automation-ollama', 'automation-controller']
        all_running = True
        
        for container in containers:
            result = self.run_command(
                f"docker inspect -f '{{{{.State.Running}}}}' {container}",
                check=False
            )
            if result and result.stdout.strip() == "true":
                self.success(f"{container} działa")
            else:
                self.error(f"{container} nie działa")
                all_running = False
        
        return all_running
    
    def test_vnc_port(self):
        """Test 3: Sprawdź czy port VNC jest dostępny"""
        self.info("Test 3: Sprawdzanie portu VNC...")
        
        result = self.run_command(
            "nc -z -v -w5 localhost 5901 2>&1",
            check=False
        )
        if result and "succeeded" in result.stdout.lower():
            self.success("Port VNC (5901) jest dostępny")
            return True
        else:
            self.error("Port VNC (5901) nie odpowiada")
            return False
    
    def test_novnc_port(self):
        """Test 4: Sprawdź czy port noVNC jest dostępny"""
        self.info("Test 4: Sprawdzanie portu noVNC...")
        
        result = self.run_command(
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:6080",
            check=False
        )
        if result and result.stdout.strip() == "200":
            self.success("noVNC (6080) jest dostępne")
            return True
        else:
            self.warning("noVNC może jeszcze się uruchamiać...")
            return False
    
    def test_ollama_api(self):
        """Test 5: Sprawdź czy Ollama API działa"""
        self.info("Test 5: Sprawdzanie Ollama API...")
        
        result = self.run_command(
            "curl -s http://localhost:11434/api/tags",
            check=False
        )
        if result and result.stdout:
            try:
                data = json.loads(result.stdout)
                if 'models' in data:
                    models = [m['name'] for m in data.get('models', [])]
                    self.success(f"Ollama API działa. Modele: {', '.join(models)}")
                    return True
            except:
                pass
        
        self.error("Ollama API nie odpowiada")
        return False
    
    def test_ollama_model(self):
        """Test 6: Sprawdź czy model jest załadowany"""
        self.info("Test 6: Sprawdzanie modelu Ollama...")
        
        result = self.run_command(
            "curl -s http://localhost:11434/api/tags",
            check=False
        )
        if result and result.stdout:
            try:
                data = json.loads(result.stdout)
                models = data.get('models', [])
                
                # Sprawdź czy jest jakiś model vision
                vision_models = [m for m in models if 'llava' in m['name'] or 'moondream' in m['name'] or 'bakllava' in m['name']]
                
                if vision_models:
                    self.success(f"Model vision znaleziony: {vision_models[0]['name']}")
                    return True
                else:
                    self.warning("Brak modelu vision. Uruchom: ollama pull llava:7b")
                    return False
            except:
                pass
        
        return False
    
    def test_vnc_connection(self):
        """Test 7: Test połączenia VNC"""
        self.info("Test 7: Test połączenia VNC...")
        
        # Użyj vncdotool do testu połączenia
        result = self.run_command(
            "docker-compose exec -T automation-controller python3 -c \"import vncdotool.api as vnc; c = vnc.connect('vnc-desktop::5901', password='automation'); print('OK')\"",
            check=False
        )
        
        if result and "OK" in result.stdout:
            self.success("Połączenie VNC działa")
            return True
        else:
            self.error("Nie można połączyć się z VNC")
            return False
    
    def test_automation_simple(self):
        """Test 8: Prosty test automatyzacji"""
        self.info("Test 8: Prosty test automatyzacji...")
        
        # Utwórz prosty test script
        test_script = """
import sys
sys.path.insert(0, '/app')
from remote_automation import RemoteController, OllamaVision, AutomationEngine

try:
    controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
    vision = OllamaVision('http://ollama:11434', 'llava:7b')
    
    script = [
        {'action': 'connect'},
        {'action': 'wait', 'seconds': 1},
        {'action': 'disconnect'}
    ]
    
    engine = AutomationEngine(controller, vision)
    engine.execute_dsl(script)
    print("TEST_SUCCESS")
except Exception as e:
    print(f"TEST_FAILED: {e}")
"""
        
        # Zapisz skrypt
        Path("/tmp/test_automation.py").write_text(test_script)
        
        # Uruchom test
        result = self.run_command(
            "docker cp /tmp/test_automation.py automation-controller:/tmp/ && "
            "docker-compose exec -T automation-controller python3 /tmp/test_automation.py",
            check=False
        )
        
        if result and "TEST_SUCCESS" in result.stdout:
            self.success("Test automatyzacji przeszedł pomyślnie")
            return True
        else:
            self.error("Test automatyzacji nie powiódł się")
            return False
    
    def test_desktop_screenshot(self):
        """Test 9: Sprawdź czy można pobrać screenshot"""
        self.info("Test 9: Test przechwytywania ekranu...")
        
        test_script = """
import sys
sys.path.insert(0, '/app')
from remote_automation import RemoteController

try:
    controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
    controller.connect()
    screen = controller.capture_screen()
    if screen.size[0] > 0 and screen.size[1] > 0:
        print(f"SCREENSHOT_OK: {screen.size[0]}x{screen.size[1]}")
    controller.disconnect()
except Exception as e:
    print(f"SCREENSHOT_FAILED: {e}")
"""
        
        Path("/tmp/test_screenshot.py").write_text(test_script)
        
        result = self.run_command(
            "docker cp /tmp/test_screenshot.py automation-controller:/tmp/ && "
            "docker-compose exec -T automation-controller python3 /tmp/test_screenshot.py",
            check=False
        )
        
        if result and "SCREENSHOT_OK" in result.stdout:
            size = result.stdout.split("SCREENSHOT_OK: ")[1].strip()
            self.success(f"Screenshot przechwycony: {size}")
            return True
        else:
            self.error("Nie można przechwycić screenshot")
            return False
    
    def test_ollama_vision(self):
        """Test 10: Test analizy vision przez Ollama"""
        self.info("Test 10: Test Ollama Vision...")
        
        test_script = """
import sys
sys.path.insert(0, '/app')
from remote_automation import RemoteController, OllamaVision

try:
    controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
    vision = OllamaVision('http://ollama:11434', 'llava:7b')
    
    controller.connect()
    screen = controller.capture_screen()
    
    response = vision.analyze_screen(screen, "What operating system is this? Answer in one word.")
    
    if response and len(response) > 0:
        print(f"VISION_OK: {response[:50]}")
    controller.disconnect()
except Exception as e:
    print(f"VISION_FAILED: {e}")
"""
        
        Path("/tmp/test_vision.py").write_text(test_script)
        
        result = self.run_command(
            "docker cp /tmp/test_vision.py automation-controller:/tmp/ && "
            "docker-compose exec -T automation-controller python3 /tmp/test_vision.py",
            check=False
        )
        
        if result and "VISION_OK" in result.stdout:
            response = result.stdout.split("VISION_OK: ")[1].strip()
            self.success(f"Ollama Vision działa: {response}")
            return True
        else:
            self.error("Ollama Vision nie działa")
            return False
    
    def run_all_tests(self):
        """Uruchom wszystkie testy"""
        print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.BLUE}  Test Suite - Remote Automation{Colors.NC}")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")
        
        tests = [
            ("Docker Status", self.test_docker_running),
            ("Containers Running", self.test_containers_running),
            ("VNC Port", self.test_vnc_port),
            ("noVNC Port", self.test_novnc_port),
            ("Ollama API", self.test_ollama_api),
            ("Ollama Model", self.test_ollama_model),
            ("VNC Connection", self.test_vnc_connection),
            ("Automation Simple", self.test_automation_simple),
            ("Desktop Screenshot", self.test_desktop_screenshot),
            ("Ollama Vision", self.test_ollama_vision),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                result = test_func()
                self.results.append({
                    'test': name,
                    'passed': result,
                    'time': datetime.now().isoformat()
                })
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.error(f"Test {name} wywołał wyjątek: {e}")
                failed += 1
                self.results.append({
                    'test': name,
                    'passed': False,
                    'error': str(e),
                    'time': datetime.now().isoformat()
                })
            
            print()  # Nowa linia między testami
        
        # Podsumowanie
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.BLUE}  Podsumowanie{Colors.NC}")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"Testy wykonane: {passed + failed}")
        print(f"{Colors.GREEN}Zaliczone: {passed}{Colors.NC}")
        print(f"{Colors.RED}Niezaliczone: {failed}{Colors.NC}")
        print(f"Czas: {duration:.2f}s")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")
        
        # Zapisz wyniki
        results_file = Path("results/test_results.json")
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': passed + failed,
                    'passed': passed,
                    'failed': failed,
                    'duration': duration,
                    'timestamp': self.start_time.isoformat()
                },
                'tests': self.results
            }, f, indent=2)
        
        self.info(f"Wyniki zapisane: {results_file}")
        
        return failed == 0

def main():
    runner = TestRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        runner.info("Czekam 60 sekund na uruchomienie usług...")
        time.sleep(60)
    
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
