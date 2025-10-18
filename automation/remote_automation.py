#!/usr/bin/env python3
"""
Remote Control Automation z integracją Ollama Vision
Wymaga: pip install pillow requests pynput python-vnc pyvirtualdisplay
"""

import base64
import io
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None
from typing import Dict, List, Optional
import subprocess
import re

# Try to import pynput, but don't fail if it's not available
try:
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Controller as KeyboardController, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class OllamaVision:
    """Integracja z Ollama do analizy obrazu"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llava:7b"):
        self.base_url = base_url
        self.model = model
    
    def encode_image(self, image: Image.Image) -> str:
        """Konwertuje obraz PIL do base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def analyze_screen(self, image: Image.Image, prompt: str) -> str:
        """Analizuje screenshot z promptem"""
        print(f"🤖 Wysyłam zapytanie do Ollama ({self.model})...")
        print(f"   Timeout: 120s - to może chwilę potrwać...")
        
        img_b64 = self.encode_image(image)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            elapsed = time.time() - start_time
            print(f"   ✓ Odpowiedź otrzymana po {elapsed:.1f}s")
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception(f"Ollama error: {response.text}")
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama timeout po 120s - model może nie być pobrany lub Ollama nie działa")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Nie można połączyć z Ollama ({self.base_url}) - sprawdź czy usługa działa")
    
    def find_element(self, image: Image.Image, element_desc: str) -> Optional[Dict]:
        """Znajduje element na ekranie i zwraca współrzędne"""
        width, height = image.size
        
        # Pierwsza próba - dokładne współrzędne
        prompt = f"""Analyze this screenshot (size: {width}x{height} pixels) and locate: {element_desc}

Look carefully at the entire screen. If you can see this element, estimate its center position in pixels.

Respond ONLY with JSON format:
{{"found": true, "x": <pixel_x>, "y": <pixel_y>, "confidence": <0-100>}}

If not visible, respond:
{{"found": false}}

Example responses:
{{"found": true, "x": 150, "y": 80, "confidence": 90}}
{{"found": false}}"""
        
        response = self.analyze_screen(image, prompt)
        
        # Wyciągnij JSON z odpowiedzi
        try:
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                if result.get('found'):
                    return result
        except:
            pass
        
        # Druga próba - użyj opisu pozycji jeśli nie znaleziono dokładnych współrzędnych
        prompt2 = f"""Look at this screenshot. Can you see: {element_desc}?

Answer with ONLY:
- "TOP-LEFT" if it's in the top-left quarter
- "TOP-RIGHT" if it's in the top-right quarter  
- "BOTTOM-LEFT" if it's in the bottom-left quarter
- "BOTTOM-RIGHT" if it's in the bottom-right quarter
- "CENTER" if it's in the center
- "NOT-FOUND" if you cannot see it

One word only."""
        
        response2 = self.analyze_screen(image, prompt2).strip().upper()
        
        # Mapuj pozycje na współrzędne
        position_map = {
            'TOP-LEFT': (width // 4, height // 4),
            'TOP-RIGHT': (3 * width // 4, height // 4),
            'BOTTOM-LEFT': (width // 4, 3 * height // 4),
            'BOTTOM-RIGHT': (3 * width // 4, 3 * height // 4),
            'CENTER': (width // 2, height // 2),
        }
        
        for pos_name, (x, y) in position_map.items():
            if pos_name in response2:
                return {"found": True, "x": x, "y": y, "confidence": 60}
        
        return {"found": False}


class RemoteController:
    """Kontroler dla zdalnych połączeń"""
    
    def __init__(self, protocol: str, host: str, port: int, **kwargs):
        self.protocol = protocol.lower()
        self.host = host
        self.port = port
        self.connection = None
        self.kwargs = kwargs
        
    def connect(self):
        """Nawiązuje połączenie"""
        if self.protocol == "vnc":
            self._connect_vnc()
        elif self.protocol == "rdp":
            self._connect_rdp()
        elif self.protocol == "spice":
            self._connect_spice()
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
    
    def _connect_vnc(self):
        """Połączenie VNC przez vncdotool"""
        import vncdotool.api as vnc
        password = self.kwargs.get('password', '')
        self.connection = vnc.connect(f"{self.host}::{self.port}", password=password)
        print(f"✓ Connected to VNC: {self.host}:{self.port}")
    
    def _connect_rdp(self):
        """Połączenie RDP przez xfreerdp"""
        username = self.kwargs.get('username', '')
        password = self.kwargs.get('password', '')
        
        cmd = [
            'xfreerdp',
            f'/v:{self.host}:{self.port}',
            f'/u:{username}',
            f'/p:{password}',
            '/cert-ignore',
            '/dynamic-resolution'
        ]
        
        self.connection = subprocess.Popen(cmd)
        time.sleep(3)
        print(f"✓ Connected to RDP: {self.host}:{self.port}")
    
    def _connect_spice(self):
        """Połączenie SPICE przez remote-viewer"""
        cmd = ['remote-viewer', f'spice://{self.host}:{self.port}']
        self.connection = subprocess.Popen(cmd)
        time.sleep(3)
        print(f"✓ Connected to SPICE: {self.host}:{self.port}")
    
    def click(self, x: int, y: int):
        """Kliknięcie na współrzędnych"""
        if self.protocol == "vnc" and self.connection:
            self.connection.mousePress(x, y, 1)
        else:
            # Dla RDP/SPICE używamy pynput jeśli dostępne
            if PYNPUT_AVAILABLE:
                mouse = MouseController()
                mouse.position = (x, y)
                mouse.click(Button.left)
            else:
                print(f"Warning: pynput not available, cannot click at ({x}, {y})")
    
    def type_text(self, text: str):
        """Wpisanie tekstu"""
        if self.protocol == "vnc" and self.connection:
            self.connection.keyPress(text)
        else:
            if PYNPUT_AVAILABLE:
                keyboard = KeyboardController()
                keyboard.type(text)
            else:
                print(f"Warning: pynput not available, cannot type text: {text}")
    
    def key_press(self, key: str):
        """Naciśnięcie klawisza"""
        if self.protocol == "vnc" and self.connection:
            self.connection.keyPress(key)
        else:
            if PYNPUT_AVAILABLE:
                keyboard = KeyboardController()
                
                # Mapowanie klawiszy specjalnych
                key_map = {
                    'enter': Key.enter,
                    'tab': Key.tab,
                    'esc': Key.esc,
                    'space': Key.space,
                }
                
                if key.lower() in key_map:
                    keyboard.press(key_map[key.lower()])
                    keyboard.release(key_map[key.lower()])
                else:
                    keyboard.press(key)
                    keyboard.release(key)
            else:
                print(f"Warning: pynput not available, cannot press key: {key}")
    
    def capture_screen(self) -> Image.Image:
        """Przechwytuje screenshot"""
        if self.protocol == "vnc" and self.connection:
            self.connection.captureScreen('temp_screen.png')
            return Image.open('temp_screen.png')
        else:
            if ImageGrab:
                return ImageGrab.grab()
            else:
                # Create a dummy image if ImageGrab is not available
                return Image.new('RGB', (800, 600), color='black')
    
    def disconnect(self):
        """Rozłącza połączenie"""
        if self.connection:
            if hasattr(self.connection, 'disconnect'):
                self.connection.disconnect()
            elif hasattr(self.connection, 'terminate'):
                self.connection.terminate()


class AutomationEngine:
    """Silnik automatyzacji z DSL"""
    
    def __init__(self, controller: RemoteController, vision: OllamaVision, enable_recording: bool = False, debug_mode: bool = False):
        self.controller = controller
        self.vision = vision
        self.variables = {}
        self.enable_recording = enable_recording
        self.recorder = None
        self.errors = []  # Śledzenie błędów
        self.debug_mode = debug_mode
        self.step_counter = 0
        self.screenshot_dir = Path('/app/results/screenshots')
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        if enable_recording:
            try:
                from screen_recorder import ScreenRecorder
                self.recorder = ScreenRecorder()
            except ImportError as e:
                print(f"⚠️  screen_recorder nie jest dostępny (brak cv2?), nagrywanie wyłączone")
                print(f"   Błąd importu: {e}")
                self.enable_recording = False
            except Exception as e:
                print(f"⚠️  Błąd inicjalizacji screen_recorder: {e}")
                self.enable_recording = False
    
    def log(self, message: str, level: str = "INFO"):
        """Loguje wiadomość z timestampem"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✓",
            "ERROR": "✗",
            "DEBUG": "🔍"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")
    
    def save_screenshot(self, name: str, screen: Image.Image = None):
        """Zapisuje screenshot z timestampem"""
        if screen is None:
            screen = self.controller.capture_screen()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{self.step_counter:03d}_{name}.png"
        filepath = self.screenshot_dir / filename
        
        screen.save(str(filepath))
        self.log(f"Screenshot saved: {filepath.name}", "DEBUG")
        return str(filepath)
    
    def execute_dsl(self, script: List[Dict], scenario_name: str = "test"):
        """Wykonuje skrypt DSL"""
        recording_stats = {}
        
        self.log(f"Starting scenario: {scenario_name}", "INFO")
        if self.debug_mode:
            self.log("Debug mode ENABLED - saving screenshots", "DEBUG")
        
        # Rozpocznij nagrywanie jeśli włączone
        if self.enable_recording and self.recorder:
            try:
                self.recorder.start_recording(
                    scenario_name, 
                    self.controller.capture_screen
                )
            except Exception as e:
                print(f"⚠️  Nie można rozpocząć nagrywania: {e}")
        
        try:
            for step in script:
                self.step_counter += 1
                action = step.get('action')
                
                self.log(f"Step {self.step_counter}: {action}", "INFO")
                
                # Screenshot przed akcją (jeśli debug)
                if self.debug_mode and action not in ['wait', 'disconnect']:
                    try:
                        screen = self.controller.capture_screen()
                        self.save_screenshot(f"before_{action}", screen)
                    except Exception as e:
                        self.log(f"Could not save screenshot: {e}", "ERROR")
                
                if action == 'connect':
                    self.controller.connect()
                    self.log(f"Connected to {self.controller.host}:{self.controller.port}", "SUCCESS")
            
                elif action == 'wait':
                    seconds = step.get('seconds', 1)
                    self.log(f"Waiting {seconds}s...", "INFO")
                    time.sleep(seconds)
                
                elif action == 'find_and_click':
                    element = step.get('element')
                    screen = self.controller.capture_screen()
                    print(f"  Searching for: {element}")
                    print(f"  Screen size: {screen.size}")
                    
                    result = self.vision.find_element(screen, element)
                    
                    if result.get('found'):
                        x, y = result['x'], result['y']
                        confidence = result.get('confidence', 'unknown')
                        print(f"  ✓ Found at ({x}, {y}) - confidence: {confidence}")
                        self.controller.click(x, y)
                    else:
                        error_msg = f"Element not found: {element}"
                        print(f"  ✗ {error_msg}")
                        print(f"  Tip: Check if the element is visible on screen")
                        self.errors.append(error_msg)
                
                elif action == 'click':
                    x, y = step.get('x'), step.get('y')
                    self.controller.click(x, y)
                
                elif action == 'click_position':
                    # Kliknij w opisaną pozycję (np. "top-left", "center")
                    screen = self.controller.capture_screen()
                    width, height = screen.size
                    position = step.get('position', 'center').lower()
                    
                    position_map = {
                        'top-left': (width // 4, height // 4),
                        'top-center': (width // 2, height // 4),
                        'top-right': (3 * width // 4, height // 4),
                        'center-left': (width // 4, height // 2),
                        'center': (width // 2, height // 2),
                        'center-right': (3 * width // 4, height // 2),
                        'bottom-left': (width // 4, 3 * height // 4),
                        'bottom-center': (width // 2, 3 * height // 4),
                        'bottom-right': (3 * width // 4, 3 * height // 4),
                    }
                    
                    if position in position_map:
                        x, y = position_map[position]
                        print(f"  Clicking at {position}: ({x}, {y})")
                        self.controller.click(x, y)
                    else:
                        print(f"  ✗ Unknown position: {position}")
                        print(f"  Available: {', '.join(position_map.keys())}")
                
                elif action == 'type':
                    text = step.get('text')
                    self.controller.type_text(text)
                
                elif action == 'key':
                    key = step.get('key')
                    self.controller.key_press(key)
                
                elif action == 'verify':
                    screen = self.controller.capture_screen()
                    expected = step.get('expected')
                    response = self.vision.analyze_screen(
                        screen, 
                        f"Check if the screen shows: {expected}. Answer only YES or NO."
                    )
                    
                    if 'yes' in response.lower():
                        print(f"  ✓ Verified: {expected}")
                    else:
                        error_msg = f"Verification failed: {expected}"
                        print(f"  ✗ {error_msg}")
                        self.errors.append(error_msg)
                
                elif action == 'analyze':
                    screen = self.controller.capture_screen()
                    question = step.get('question')
                    response = self.vision.analyze_screen(screen, question)
                    print(f"  Analysis: {response}")
                    
                    # Zapisz do zmiennej jeśli podano
                    var_name = step.get('save_to')
                    if var_name:
                        self.variables[var_name] = response
                
                elif action == 'screenshot':
                    # Manualne zapisanie screenshota
                    name = step.get('name', 'manual')
                    screen = self.controller.capture_screen()
                    filepath = self.save_screenshot(name, screen)
                    self.log(f"Screenshot: {filepath}", "SUCCESS")
                
                elif action == 'disconnect':
                    self.controller.disconnect()
                    self.log("Disconnected", "INFO")
                
                else:
                    self.log(f"Unknown action: {action}", "ERROR")
                
                # Screenshot po akcji (jeśli debug)
                if self.debug_mode and action not in ['wait', 'disconnect', 'screenshot']:
                    try:
                        screen = self.controller.capture_screen()
                        self.save_screenshot(f"after_{action}", screen)
                    except Exception as e:
                        self.log(f"Could not save screenshot: {e}", "ERROR")
                
                # Krótka przerwa między akcjami
                time.sleep(0.5)
        
        finally:
            # Zatrzymaj nagrywanie jeśli było aktywne
            if self.enable_recording and self.recorder:
                try:
                    recording_stats = self.recorder.stop_recording()
                    return recording_stats
                except Exception as e:
                    print(f"⚠️  Błąd zatrzymania nagrywania: {e}")
            
            return recording_stats


def main():
    """Przykład użycia"""
    
    # Konfiguracja
    config = {
        'protocol': 'vnc',  # vnc, rdp, lub spice
        'host': 'localhost',
        'port': 5900,
        'password': ''
    }
    
    # Skrypt DSL - przykład otwierania przeglądarki i wyszukiwania
    dsl_script = [
        {
            'action': 'connect'
        },
        {
            'action': 'wait',
            'seconds': 2
        },
        {
            'action': 'find_and_click',
            'element': 'Firefox browser icon'
        },
        {
            'action': 'wait',
            'seconds': 3
        },
        {
            'action': 'find_and_click',
            'element': 'address bar or search box'
        },
        {
            'action': 'type',
            'text': 'https://example.com'
        },
        {
            'action': 'key',
            'key': 'enter'
        },
        {
            'action': 'wait',
            'seconds': 2
        },
        {
            'action': 'verify',
            'expected': 'Example Domain page is loaded'
        },
        {
            'action': 'analyze',
            'question': 'What is the main heading on this page?',
            'save_to': 'heading'
        },
        {
            'action': 'disconnect'
        }
    ]
    
    # Uruchomienie
    try:
        controller = RemoteController(
            protocol=config['protocol'],
            host=config['host'],
            port=config['port'],
            password=config.get('password')
        )
        
        vision = OllamaVision(model="llava:7b")  # lub llava:13b, moondream, bakllava
        
        engine = AutomationEngine(controller, vision)
        engine.execute_dsl(dsl_script)
        
        print("\n✓ Automation completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
