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
from PIL import Image, ImageGrab
from typing import Dict, List, Optional
import subprocess
import re

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
        img_b64 = self.encode_image(image)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama error: {response.text}")
    
    def find_element(self, image: Image.Image, element_desc: str) -> Optional[Dict]:
        """Znajduje element na ekranie i zwraca współrzędne"""
        prompt = f"""Analyze this screenshot and find: {element_desc}
Return ONLY a JSON object with coordinates:
{{"found": true/false, "x": pixel_x, "y": pixel_y, "confidence": 0-100}}
If not found, return {{"found": false}}"""
        
        response = self.analyze_screen(image, prompt)
        
        # Wyciągnij JSON z odpowiedzi
        try:
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
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
            # Dla RDP/SPICE używamy pynput
            from pynput.mouse import Button, Controller
            mouse = Controller()
            mouse.position = (x, y)
            mouse.click(Button.left)
    
    def type_text(self, text: str):
        """Wpisanie tekstu"""
        if self.protocol == "vnc" and self.connection:
            self.connection.keyPress(text)
        else:
            from pynput.keyboard import Controller
            keyboard = Controller()
            keyboard.type(text)
    
    def key_press(self, key: str):
        """Naciśnięcie klawisza"""
        if self.protocol == "vnc" and self.connection:
            self.connection.keyPress(key)
        else:
            from pynput.keyboard import Controller, Key
            keyboard = Controller()
            
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
    
    def capture_screen(self) -> Image.Image:
        """Przechwytuje screenshot"""
        if self.protocol == "vnc" and self.connection:
            self.connection.captureScreen('temp_screen.png')
            return Image.open('temp_screen.png')
        else:
            return ImageGrab.grab()
    
    def disconnect(self):
        """Rozłącza połączenie"""
        if self.connection:
            if hasattr(self.connection, 'disconnect'):
                self.connection.disconnect()
            elif hasattr(self.connection, 'terminate'):
                self.connection.terminate()


class AutomationEngine:
    """Silnik automatyzacji z DSL"""
    
    def __init__(self, controller: RemoteController, vision: OllamaVision):
        self.controller = controller
        self.vision = vision
        self.variables = {}
    
    def execute_dsl(self, script: List[Dict]):
        """Wykonuje skrypt DSL"""
        for step in script:
            action = step.get('action')
            print(f"→ Executing: {action}")
            
            if action == 'connect':
                self.controller.connect()
            
            elif action == 'wait':
                time.sleep(step.get('seconds', 1))
            
            elif action == 'find_and_click':
                element = step.get('element')
                screen = self.controller.capture_screen()
                result = self.vision.find_element(screen, element)
                
                if result.get('found'):
                    x, y = result['x'], result['y']
                    print(f"  Found at ({x}, {y})")
                    self.controller.click(x, y)
                else:
                    print(f"  ✗ Element not found: {element}")
            
            elif action == 'click':
                x, y = step.get('x'), step.get('y')
                self.controller.click(x, y)
            
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
                    print(f"  ✗ Verification failed: {expected}")
            
            elif action == 'analyze':
                screen = self.controller.capture_screen()
                question = step.get('question')
                response = self.vision.analyze_screen(screen, question)
                print(f"  Analysis: {response}")
                
                # Zapisz do zmiennej jeśli podano
                var_name = step.get('save_to')
                if var_name:
                    self.variables[var_name] = response
            
            elif action == 'disconnect':
                self.controller.disconnect()
            
            else:
                print(f"  ✗ Unknown action: {action}")
            
            # Krótka przerwa między akcjami
            time.sleep(0.5)


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
