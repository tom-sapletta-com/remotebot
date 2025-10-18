#!/usr/bin/env python3
"""
Monitoring Dashboard dla Remote Automation
Monitoruje status środowiska Docker w czasie rzeczywistym
"""

import time
import subprocess
import json
import requests
from datetime import datetime
from pathlib import Path
import sys

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Monitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.containers = ['automation-vnc', 'automation-ollama', 'automation-controller']
        
    def clear_screen(self):
        """Wyczyść ekran"""
        subprocess.run(['clear'] if sys.platform != 'win32' else ['cls'], shell=True)
    
    def get_container_stats(self, container_name):
        """Pobierz statystyki kontenera"""
        try:
            # CPU i Memory
            result = subprocess.run(
                f"docker stats {container_name} --no-stream --format '{{{{.CPUPerc}}}}|{{{{.MemUsage}}}}|{{{{.NetIO}}}}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 3:
                    return {
                        'cpu': parts[0],
                        'memory': parts[1],
                        'network': parts[2]
                    }
        except:
            pass
        return None
    
    def get_container_status(self, container_name):
        """Sprawdź status kontenera"""
        try:
            result = subprocess.run(
                f"docker inspect -f '{{{{.State.Running}}}}|{{{{.State.Status}}}}' {container_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                return {
                    'running': parts[0] == 'true',
                    'status': parts[1] if len(parts) > 1 else 'unknown'
                }
        except:
            pass
        return {'running': False, 'status': 'unknown'}
    
    def check_vnc_port(self):
        """Sprawdź port VNC"""
        try:
            result = subprocess.run(
                "nc -z -w2 localhost 5901",
                shell=True,
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
    
    def check_novnc_port(self):
        """Sprawdź port noVNC"""
        try:
            response = requests.get('http://localhost:6080', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def check_ollama_api(self):
        """Sprawdź Ollama API i modele"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                return True, models
        except:
            pass
        return False, []
    
    def get_recent_test_results(self):
        """Pobierz ostatnie wyniki testów"""
        results_file = Path('results/test_results.json')
        if results_file.exists():
            try:
                with open(results_file) as f:
                    data = json.load(f)
                    return data.get('summary', {})
            except:
                pass
        return None
    
    def draw_header(self):
        """Rysuj nagłówek"""
        uptime = datetime.now() - self.start_time
        
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}  Remote Automation - Monitoring Dashboard{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}Czas działania monitora: {uptime}{Colors.END}")
        print(f"{Colors.CYAN}Aktualizacja: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")
        print()
    
    def draw_container_section(self):
        """Rysuj sekcję kontenerów"""
        print(f"{Colors.BOLD}{Colors.UNDERLINE}Kontenery Docker{Colors.END}")
        print()
        
        for container in self.containers:
            status = self.get_container_status(container)
            stats = self.get_container_stats(container) if status['running'] else None
            
            # Status indicator
            if status['running']:
                indicator = f"{Colors.GREEN}●{Colors.END}"
                status_text = f"{Colors.GREEN}RUNNING{Colors.END}"
            else:
                indicator = f"{Colors.RED}●{Colors.END}"
                status_text = f"{Colors.RED}STOPPED{Colors.END}"
            
            print(f"{indicator} {Colors.BOLD}{container}{Colors.END}")
            print(f"   Status: {status_text}")
            
            if stats:
                print(f"   CPU: {Colors.YELLOW}{stats['cpu']}{Colors.END}")
                print(f"   Memory: {Colors.YELLOW}{stats['memory']}{Colors.END}")
                print(f"   Network: {Colors.YELLOW}{stats['network']}{Colors.END}")
            
            print()
    
    def draw_services_section(self):
        """Rysuj sekcję usług"""
        print(f"{Colors.BOLD}{Colors.UNDERLINE}Usługi{Colors.END}")
        print()
        
        # VNC
        vnc_status = self.check_vnc_port()
        vnc_indicator = f"{Colors.GREEN}●{Colors.END}" if vnc_status else f"{Colors.RED}●{Colors.END}"
        print(f"{vnc_indicator} VNC Server (5901): ", end="")
        print(f"{Colors.GREEN}DOSTĘPNY{Colors.END}" if vnc_status else f"{Colors.RED}NIEDOSTĘPNY{Colors.END}")
        
        # noVNC
        novnc_status = self.check_novnc_port()
        novnc_indicator = f"{Colors.GREEN}●{Colors.END}" if novnc_status else f"{Colors.RED}●{Colors.END}"
        print(f"{novnc_indicator} noVNC (6080): ", end="")
        print(f"{Colors.GREEN}DOSTĘPNY{Colors.END}" if novnc_status else f"{Colors.RED}NIEDOSTĘPNY{Colors.END}")
        if novnc_status:
            print(f"   {Colors.CYAN}→ http://localhost:6080/vnc.html{Colors.END}")
        
        # Ollama
        ollama_status, models = self.check_ollama_api()
        ollama_indicator = f"{Colors.GREEN}●{Colors.END}" if ollama_status else f"{Colors.RED}●{Colors.END}"
        print(f"{ollama_indicator} Ollama API (11434): ", end="")
        print(f"{Colors.GREEN}DOSTĘPNY{Colors.END}" if ollama_status else f"{Colors.RED}NIEDOSTĘPNY{Colors.END}")
        if models:
            print(f"   Modele: {Colors.YELLOW}{', '.join(models)}{Colors.END}")
        
        print()
    
    def draw_tests_section(self):
        """Rysuj sekcję testów"""
        print(f"{Colors.BOLD}{Colors.UNDERLINE}Ostatnie testy{Colors.END}")
        print()
        
        results = self.get_recent_test_results()
        if results:
            total = results.get('total', 0)
            passed = results.get('passed', 0)
            failed = results.get('failed', 0)
            timestamp = results.get('timestamp', 'unknown')
            
            if timestamp != 'unknown':
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            print(f"Wykonano: {timestamp}")
            print(f"Wszystkie testy: {total}")
            print(f"{Colors.GREEN}Zaliczone: {passed}{Colors.END}")
            print(f"{Colors.RED}Niezaliczone: {failed}{Colors.END}")
            
            if total > 0:
                success_rate = (passed / total) * 100
                if success_rate == 100:
                    color = Colors.GREEN
                elif success_rate >= 80:
                    color = Colors.YELLOW
                else:
                    color = Colors.RED
                print(f"Wskaźnik sukcesu: {color}{success_rate:.1f}%{Colors.END}")
        else:
            print(f"{Colors.YELLOW}Brak wyników testów{Colors.END}")
            print("Uruchom: make test")
        
        print()
    
    def draw_quick_commands(self):
        """Rysuj szybkie komendy"""
        print(f"{Colors.BOLD}{Colors.UNDERLINE}Szybkie komendy{Colors.END}")
        print()
        print(f"{Colors.CYAN}make status{Colors.END}      - Status usług")
        print(f"{Colors.CYAN}make logs{Colors.END}        - Zobacz logi")
        print(f"{Colors.CYAN}make test{Colors.END}        - Uruchom testy")
        print(f"{Colors.CYAN}make restart{Colors.END}     - Restart środowiska")
        print(f"{Colors.CYAN}make shell{Colors.END}       - Otwórz shell")
        print()
    
    def draw_footer(self):
        """Rysuj stopkę"""
        print(f"{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}Naciśnij Ctrl+C aby wyjść | Odświeżanie co 5 sekund{Colors.END}")
    
    def display(self):
        """Wyświetl pełny dashboard"""
        self.clear_screen()
        self.draw_header()
        self.draw_container_section()
        self.draw_services_section()
        self.draw_tests_section()
        self.draw_quick_commands()
        self.draw_footer()
    
    def run(self, interval=5):
        """Uruchom monitoring w pętli"""
        print(f"{Colors.CYAN}Inicjalizacja monitora...{Colors.END}")
        time.sleep(1)
        
        try:
            while True:
                self.display()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitor zatrzymany{Colors.END}")
            sys.exit(0)

def main():
    """Główna funkcja"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitoring Dashboard')
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help='Interwał odświeżania w sekundach (domyślnie: 5)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Wyświetl raz i zakończ (bez auto-refresh)'
    )
    
    args = parser.parse_args()
    
    monitor = Monitor()
    
    if args.once:
        monitor.display()
    else:
        monitor.run(interval=args.interval)

if __name__ == "__main__":
    main()
