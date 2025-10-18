#!/usr/bin/env python3
"""
Screen Recorder - nagrywanie ekranu VNC do plików MP4
Używa OpenCV do kompresji wideo i zachowania historii testów
"""

import cv2
import numpy as np
from PIL import Image
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable


class ScreenRecorder:
    """Nagrywa ekran podczas testów automatyzacji"""
    
    def __init__(
        self, 
        output_dir: str = "results/videos",
        fps: int = 10,
        codec: str = "mp4v",
        quality: int = 80
    ):
        """
        Args:
            output_dir: Katalog na pliki wideo
            fps: Klatki na sekundę (10-30 zalecane)
            codec: Kodek wideo ('mp4v', 'avc1', 'h264')
            quality: Jakość kompresji 0-100
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.fps = fps
        self.codec = cv2.VideoWriter_fourcc(*codec)
        self.quality = quality
        
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.capture_func: Optional[Callable] = None
        
        self.current_file: Optional[Path] = None
        self.frame_count = 0
        self.start_time: Optional[float] = None
    
    def start_recording(
        self, 
        scenario_name: str, 
        capture_func: Callable[[], Image.Image],
        resolution: tuple = (1280, 720)
    ) -> Path:
        """
        Rozpocznij nagrywanie
        
        Args:
            scenario_name: Nazwa scenariusza testowego
            capture_func: Funkcja zwracająca PIL.Image z aktualnym ekranem
            resolution: Rozdzielczość wideo (width, height)
        
        Returns:
            Path do pliku wideo
        """
        if self.recording:
            raise RuntimeError("Nagrywanie już trwa!")
        
        # Nazwa pliku z timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario_name}_{timestamp}.mp4"
        self.current_file = self.output_dir / filename
        
        # Inicjalizuj VideoWriter
        self.video_writer = cv2.VideoWriter(
            str(self.current_file),
            self.codec,
            self.fps,
            resolution
        )
        
        if not self.video_writer.isOpened():
            raise RuntimeError(f"Nie można otworzyć pliku wideo: {self.current_file}")
        
        self.capture_func = capture_func
        self.recording = True
        self.frame_count = 0
        self.start_time = time.time()
        
        # Uruchom wątek nagrywania
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        
        print(f"📹 Nagrywanie rozpoczęte: {self.current_file}")
        return self.current_file
    
    def _recording_loop(self):
        """Wątek nagrywający klatki"""
        frame_interval = 1.0 / self.fps
        
        while self.recording:
            loop_start = time.time()
            
            try:
                # Pobierz screenshot
                screen = self.capture_func()
                
                # Konwertuj PIL Image -> OpenCV format
                frame = self._pil_to_opencv(screen)
                
                # Zapisz klatkę
                if frame is not None:
                    self.video_writer.write(frame)
                    self.frame_count += 1
                
            except Exception as e:
                print(f"⚠️  Błąd podczas nagrywania klatki: {e}")
            
            # Czekaj do następnej klatki
            elapsed = time.time() - loop_start
            sleep_time = max(0, frame_interval - elapsed)
            time.sleep(sleep_time)
    
    def stop_recording(self) -> dict:
        """
        Zatrzymaj nagrywanie i zapisz plik
        
        Returns:
            Informacje o nagraniu (plik, czas, klatki)
        """
        if not self.recording:
            return {}
        
        self.recording = False
        
        # Poczekaj na zakończenie wątku
        if self.recording_thread:
            self.recording_thread.join(timeout=5)
        
        # Zamknij plik wideo
        if self.video_writer:
            self.video_writer.release()
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        stats = {
            'file': str(self.current_file),
            'frames': self.frame_count,
            'duration': f"{duration:.2f}s",
            'fps': self.fps,
            'size_mb': self.current_file.stat().st_size / (1024 * 1024) if self.current_file.exists() else 0
        }
        
        print(f"✅ Nagrywanie zakończone:")
        print(f"   📁 Plik: {stats['file']}")
        print(f"   🎬 Klatki: {stats['frames']}")
        print(f"   ⏱️  Czas: {stats['duration']}")
        print(f"   💾 Rozmiar: {stats['size_mb']:.2f} MB")
        
        return stats
    
    def _pil_to_opencv(self, pil_image: Image.Image) -> Optional[np.ndarray]:
        """Konwertuj PIL Image do formatu OpenCV (BGR)"""
        try:
            # Konwertuj do RGB
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # PIL -> numpy array
            frame = np.array(pil_image)
            
            # RGB -> BGR (OpenCV używa BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Skaluj jeśli potrzeba (opcjonalnie dodaj kompresję)
            # frame = cv2.resize(frame, (1280, 720))
            
            return frame
        except Exception as e:
            print(f"⚠️  Błąd konwersji obrazu: {e}")
            return None
    
    def add_text_overlay(self, frame: np.ndarray, text: str, position=(10, 30)) -> np.ndarray:
        """Dodaj tekst na klatkę (np. timestamp, action)"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)  # Biały
        thickness = 2
        
        # Dodaj czarne tło dla lepszej czytelności
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.rectangle(
            frame, 
            (position[0] - 5, position[1] - text_height - 5),
            (position[0] + text_width + 5, position[1] + 5),
            (0, 0, 0),  # Czarne tło
            -1
        )
        
        # Dodaj tekst
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
        return frame


class RecordingContext:
    """Context manager dla wygodnego nagrywania"""
    
    def __init__(self, recorder: ScreenRecorder, scenario_name: str, capture_func: Callable):
        self.recorder = recorder
        self.scenario_name = scenario_name
        self.capture_func = capture_func
        self.stats = {}
    
    def __enter__(self):
        self.recorder.start_recording(self.scenario_name, self.capture_func)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stats = self.recorder.stop_recording()
        return False  # Nie przytłumiaj wyjątków


# Helper function dla łatwego użycia
def record_test(scenario_name: str, capture_func: Callable, output_dir: str = "results/videos"):
    """
    Context manager do nagrywania testów
    
    Przykład użycia:
        with record_test("test_firefox", controller.capture_screen):
            # Wykonaj akcje testowe
            controller.click(100, 100)
            controller.type_text("hello")
    """
    recorder = ScreenRecorder(output_dir=output_dir)
    return RecordingContext(recorder, scenario_name, capture_func)
