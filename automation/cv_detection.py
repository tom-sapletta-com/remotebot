#!/usr/bin/env python3
"""
Computer Vision Detection Module
Szybka detekcja okien, przycisków, krawędzi bez AI
"""

import cv2
import numpy as np
from PIL import Image
import io
from typing import List, Tuple, Optional, Dict

class CVDetector:
    """Computer Vision detector dla automatyzacji"""
    
    def __init__(self):
        self.last_screenshot = None
        self.debug = False
    
    def set_debug(self, debug: bool):
        """Włącz debug mode - zapisuje pośrednie obrazy"""
        self.debug = debug
    
    def screenshot_to_cv(self, screenshot_data) -> np.ndarray:
        """Konwertuj screenshot PIL/bytes do OpenCV format"""
        if isinstance(screenshot_data, bytes):
            # Z bytes
            nparr = np.frombuffer(screenshot_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(screenshot_data, Image.Image):
            # Z PIL
            img = cv2.cvtColor(np.array(screenshot_data), cv2.COLOR_RGB2BGR)
        else:
            # Już numpy array
            img = screenshot_data
        
        self.last_screenshot = img
        return img
    
    def detect_edges(self, img: np.ndarray, low_threshold: int = 50, 
                     high_threshold: int = 150) -> np.ndarray:
        """
        Wykryj krawędzie używając Canny edge detection
        
        Args:
            img: Obraz wejściowy
            low_threshold: Dolny próg Canny
            high_threshold: Górny próg Canny
            
        Returns:
            Obraz z krawędziami (binary)
        """
        # Konwertuj do grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Blur dla redukcji szumu
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        if self.debug:
            cv2.imwrite('/app/results/debug_edges.png', edges)
        
        return edges
    
    def detect_rectangles(self, img: np.ndarray, 
                          min_area: int = 1000) -> List[Tuple[int, int, int, int]]:
        """
        Wykryj prostokąty (okna, dialogi, przyciski)
        
        Args:
            img: Obraz wejściowy
            min_area: Minimalna powierzchnia prostokąta
            
        Returns:
            Lista prostokątów: [(x, y, width, height), ...]
        """
        edges = self.detect_edges(img)
        
        # Znajdź kontury
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            # Aproksymuj kontur do prostokąta
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area >= min_area:
                # Sprawdź czy to rzeczywiście prostokąt (aspect ratio)
                aspect_ratio = w / float(h) if h > 0 else 0
                if 0.2 < aspect_ratio < 5:  # Rozumne proporcje
                    rectangles.append((x, y, w, h))
        
        # Sortuj po powierzchni (największe pierwsze)
        rectangles.sort(key=lambda r: r[2] * r[3], reverse=True)
        
        if self.debug:
            debug_img = img.copy()
            for (x, y, w, h) in rectangles[:10]:  # Rysuj top 10
                cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imwrite('/app/results/debug_rectangles.png', debug_img)
        
        return rectangles
    
    def find_window_center(self, img: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Znajdź centrum najbardziej widocznego okna
        
        Returns:
            (x, y) centrum okna lub None
        """
        rectangles = self.detect_rectangles(img, min_area=5000)
        
        if rectangles:
            # Weź największy prostokąt
            x, y, w, h = rectangles[0]
            center_x = x + w // 2
            center_y = y + h // 2
            return (center_x, center_y)
        
        return None
    
    def detect_buttons(self, img: np.ndarray) -> List[Dict]:
        """
        Wykryj przyciski (małe prostokąty z tekstem)
        
        Returns:
            Lista słowników: [{'x': x, 'y': y, 'width': w, 'height': h, 
                              'center': (cx, cy)}, ...]
        """
        # Szukaj mniejszych prostokątów (przyciski)
        rectangles = self.detect_rectangles(img, min_area=500)
        
        buttons = []
        for (x, y, w, h) in rectangles:
            # Przyciski mają typowe wymiary
            if 50 < w < 300 and 20 < h < 100:
                aspect_ratio = w / float(h)
                # Przyciski są szersze niż wysokie
                if 1.5 < aspect_ratio < 10:
                    buttons.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center': (x + w//2, y + h//2),
                        'area': w * h
                    })
        
        # Sortuj po pozycji Y (od góry)
        buttons.sort(key=lambda b: b['y'])
        
        return buttons
    
    def find_text_field(self, img: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Znajdź pole tekstowe (input field)
        
        Returns:
            (x, y) centrum pola lub None
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Pola tekstowe często są białe lub jasne
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Pole tekstowe: szerokie, niskie
            if w > 100 and 20 < h < 60:
                aspect_ratio = w / float(h)
                if aspect_ratio > 3:  # Bardzo szerokie
                    return (x + w//2, y + h//2)
        
        return None
    
    def template_match(self, img: np.ndarray, template_path: str, 
                       threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Znajdź lokalizację szablonu na obrazie
        
        Args:
            img: Obraz do przeszukania
            template_path: Ścieżka do obrazu szablonu
            threshold: Próg dopasowania (0-1)
            
        Returns:
            (x, y) centrum znalezionego szablonu lub None
        """
        try:
            template = cv2.imread(template_path)
            if template is None:
                return None
            
            # Template matching
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Znaleziono
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y)
        
        except Exception as e:
            print(f"Template matching error: {e}")
        
        return None
    
    def detect_dialog_box(self, img: np.ndarray) -> Optional[Dict]:
        """
        Wykryj dialog box (okno logowania, alert, etc.)
        
        Returns:
            Słownik z informacjami o dialogu lub None
        """
        rectangles = self.detect_rectangles(img, min_area=10000)
        
        height, width = img.shape[:2]
        
        for (x, y, w, h) in rectangles:
            # Dialog jest zazwyczaj w centrum i nie zajmuje całego ekranu
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Sprawdź czy w centrum ekranu
            if (width * 0.3 < center_x < width * 0.7 and 
                height * 0.3 < center_y < height * 0.7):
                
                # I nie jest za duży (dialog vs full window)
                if w < width * 0.8 and h < height * 0.8:
                    return {
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center': (center_x, center_y),
                        'area': w * h
                    }
        
        return None
    
    def find_unlock_button(self, img: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Znajdź przycisk Unlock/Login/OK w dialogu
        
        Returns:
            (x, y) centrum przycisku lub None
        """
        dialog = self.detect_dialog_box(img)
        if not dialog:
            return None
        
        # Szukaj przycisków w obszarze dialogu
        dx, dy, dw, dh = dialog['x'], dialog['y'], dialog['width'], dialog['height']
        
        # Wytnij obszar dialogu
        dialog_img = img[dy:dy+dh, dx:dx+dw]
        
        buttons = self.detect_buttons(dialog_img)
        
        if buttons:
            # Weź dolny prawy przycisk (zazwyczaj OK/Unlock)
            rightmost = max(buttons, key=lambda b: b['x'])
            
            # Przelicz współrzędne z powrotem do pełnego obrazu
            abs_x = dx + rightmost['center'][0]
            abs_y = dy + rightmost['center'][1]
            
            return (abs_x, abs_y)
        
        return None
    
    def is_screen_blank(self, img: np.ndarray, threshold: int = 30) -> bool:
        """
        Sprawdź czy ekran jest pusty/czarny/zablokowany
        
        Args:
            img: Obraz wejściowy
            threshold: Próg jasności (0-255)
            
        Returns:
            True jeśli ekran jest prawie całkowicie czarny
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Sprawdź czy większość pikseli jest ciemna
        dark_pixels = np.sum(gray < threshold)
        total_pixels = gray.size
        dark_ratio = dark_pixels / total_pixels
        
        return mean_brightness < threshold and dark_ratio > 0.9
    
    def get_screen_diagnostics(self, img: np.ndarray) -> Dict:
        """
        Diagnostyka ekranu - co może być nie tak?
        
        Returns:
            Słownik z diagnostyką
        """
        diagnostics = {
            'is_blank': False,
            'mean_brightness': 0,
            'has_content': False,
            'edge_count': 0,
            'possible_issue': None
        }
        
        # Sprawdź jasność
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        diagnostics['mean_brightness'] = float(mean_brightness)
        
        # Sprawdź czy ekran jest pusty
        diagnostics['is_blank'] = self.is_screen_blank(img)
        
        # Policz krawędzie (content detection)
        edges = self.detect_edges(img)
        edge_count = np.sum(edges > 0)
        diagnostics['edge_count'] = int(edge_count)
        
        # Określ czy jest content
        diagnostics['has_content'] = edge_count > 1000
        
        # Diagnoza problemu
        if diagnostics['is_blank']:
            diagnostics['possible_issue'] = "Screen is blank/black - possible lock screen or VNC not connected"
        elif mean_brightness < 50:
            diagnostics['possible_issue'] = "Screen is very dark - possible screensaver or lock screen"
        elif edge_count < 500:
            diagnostics['possible_issue'] = "Very few edges detected - possible empty desktop or loading screen"
        elif edge_count < 1000:
            diagnostics['possible_issue'] = "Low content - desktop may be minimalist or partially loaded"
        else:
            diagnostics['possible_issue'] = None
        
        return diagnostics
    
    def quick_analysis(self, img: np.ndarray) -> Dict:
        """
        Szybka analiza obrazu (milisekundy!)
        
        Returns:
            Słownik z wynikami detekcji
        """
        results = {
            'has_dialog': False,
            'dialog_center': None,
            'has_buttons': False,
            'button_positions': [],
            'has_text_field': False,
            'text_field_position': None,
            'window_count': 0,
            'unlock_button': None,
            'diagnostics': {}
        }
        
        # Dodaj diagnostykę
        results['diagnostics'] = self.get_screen_diagnostics(img)
        
        # Wykryj dialog
        dialog = self.detect_dialog_box(img)
        if dialog:
            results['has_dialog'] = True
            results['dialog_center'] = dialog['center']
        
        # Wykryj przyciski
        buttons = self.detect_buttons(img)
        if buttons:
            results['has_buttons'] = True
            results['button_positions'] = [b['center'] for b in buttons]
        
        # Wykryj pole tekstowe
        text_field = self.find_text_field(img)
        if text_field:
            results['has_text_field'] = True
            results['text_field_position'] = text_field
        
        # Policz okna
        rectangles = self.detect_rectangles(img, min_area=5000)
        results['window_count'] = len(rectangles)
        
        # Znajdź przycisk Unlock
        unlock_btn = self.find_unlock_button(img)
        if unlock_btn:
            results['unlock_button'] = unlock_btn
        
        return results


# Przykład użycia
if __name__ == "__main__":
    detector = CVDetector()
    detector.set_debug(True)
    
    # Test z przykładowym obrazem
    import sys
    if len(sys.argv) > 1:
        img = cv2.imread(sys.argv[1])
        if img is not None:
            results = detector.quick_analysis(img)
            print("🔍 Quick CV Analysis:")
            print(f"  Dialog detected: {results['has_dialog']}")
            print(f"  Buttons found: {len(results['button_positions'])}")
            print(f"  Text field: {results['has_text_field']}")
            print(f"  Windows: {results['window_count']}")
            print(f"  Unlock button: {results['unlock_button']}")
