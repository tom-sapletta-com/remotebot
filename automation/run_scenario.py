#!/usr/bin/env python3
"""
Run Scenario - uruchamia scenariusze testowe z opcjonalnym nagrywaniem wideo
"""

import sys
import yaml
import argparse
from pathlib import Path

# Dodaj katalog automation do ścieżki (już jesteśmy w automation/)
sys.path.insert(0, str(Path(__file__).parent))

from remote_automation import RemoteController, OllamaVision, AutomationEngine


def load_scenario(scenario_file: Path):
    """Wczytaj scenariusz z pliku YAML"""
    with open(scenario_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_scenario(scenario_file: Path, scenario_name: str, enable_recording: bool = True, debug_mode: bool = False):
    """
    Uruchom scenariusz testowy
    
    Args:
        scenario_file: Ścieżka do pliku YAML ze scenariuszem
        scenario_name: Nazwa scenariusza do uruchomienia
        enable_recording: Czy nagrywać wideo
        debug_mode: Czy zapisywać screenshoty przed/po każdym kroku
    """
    
    # Wczytaj scenariusz
    print(f"📄 Wczytuję scenariusz: {scenario_file}")
    config = load_scenario(scenario_file)
    
    # Sprawdź czy scenariusz istnieje
    if scenario_name not in config.get('scenarios', {}):
        print(f"❌ Scenariusz '{scenario_name}' nie istnieje w pliku {scenario_file}")
        print(f"\nDostępne scenariusze:")
        for name in config.get('scenarios', {}).keys():
            print(f"  - {name}")
        return False
    
    # Pobierz konfigurację połączenia
    conn_config = config.get('connection', {})
    ollama_config = config.get('ollama', {})
    
    print(f"\n🚀 Uruchamiam scenariusz: {scenario_name}")
    if enable_recording:
        print(f"📹 Nagrywanie: WŁĄCZONE")
    else:
        print(f"📹 Nagrywanie: WYŁĄCZONE")
    if debug_mode:
        print(f"🔍 Debug mode: WŁĄCZONY (screenshoty przed/po każdym kroku)")
    print()
    
    controller = None
    engine = None
    
    try:
        # Inicjalizuj kontroler
        controller = RemoteController(
            protocol=conn_config.get('protocol', 'vnc'),
            host=conn_config.get('host', 'localhost'),
            port=conn_config.get('port', 5900),
            password=conn_config.get('password', '')
        )
        
        # Inicjalizuj vision
        vision = OllamaVision(
            base_url=ollama_config.get('url', 'http://localhost:11434'),
            model=ollama_config.get('model', 'llava:7b')
        )
        
        # Inicjalizuj engine z nagrywaniem i debug mode
        engine = AutomationEngine(
            controller, 
            vision, 
            enable_recording=enable_recording,
            debug_mode=debug_mode
        )
        
        # Uruchom scenariusz
        script = config['scenarios'][scenario_name]
        recording_stats = engine.execute_dsl(script, scenario_name=scenario_name)
        
        print()
        
        # Sprawdź czy były błędy
        if engine.errors:
            print("⚠️  Scenariusz zakończony z błędami:")
            for error in engine.errors:
                print(f"  - {error}")
            success = False
        else:
            print("✅ Scenariusz zakończony pomyślnie!")
            success = True
        
        # Wyświetl zebrane dane
        if engine.variables:
            print()
            print("📊 Zebrane dane:")
            for key, value in engine.variables.items():
                # Obetnij długie wartości
                display_value = value[:100] + "..." if len(value) > 100 else value
                print(f"  {key}: {display_value}")
        
        # Wyświetl statystyki nagrywania
        if recording_stats:
            print()
            print("🎬 Statystyki nagrywania:")
            for key, value in recording_stats.items():
                print(f"  {key}: {value}")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scenariusz przerwany przez użytkownika")
        return False
        
    except Exception as e:
        print(f"\n❌ Błąd podczas wykonywania scenariusza: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Zawsze zamknij połączenie i wyczyść zasoby
        if controller is not None:
            try:
                controller.disconnect()
                print("\n🔌 Połączenie zamknięte")
            except Exception as e:
                print(f"\n⚠️  Błąd podczas zamykania połączenia: {e}")
        
        # Wyczyść zasoby engine (jeśli są jakieś)
        if engine is not None and hasattr(engine, 'recorder') and engine.recorder:
            try:
                # Upewnij się, że nagrywanie jest zatrzymane
                if hasattr(engine.recorder, 'is_recording') and engine.recorder.is_recording:
                    engine.recorder.stop_recording()
            except Exception as e:
                print(f"⚠️  Błąd podczas czyszczenia zasobów nagrywania: {e}")


def main():
    """Główna funkcja"""
    parser = argparse.ArgumentParser(
        description="Uruchamia scenariusze testowe z opcjonalnym nagrywaniem wideo"
    )
    
    parser.add_argument(
        'scenario_file',
        type=Path,
        help='Ścieżka do pliku YAML ze scenariuszem'
    )
    
    parser.add_argument(
        'scenario_name',
        help='Nazwa scenariusza do uruchomienia'
    )
    
    parser.add_argument(
        '--no-recording',
        action='store_true',
        help='Wyłącz nagrywanie wideo'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Tryb debug - zapisuj screenshoty przed/po każdym kroku'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Wyświetl listę dostępnych scenariuszy'
    )
    
    args = parser.parse_args()
    
    # Sprawdź czy plik istnieje
    if not args.scenario_file.exists():
        print(f"❌ Plik nie istnieje: {args.scenario_file}")
        return 1
    
    # Lista scenariuszy
    if args.list:
        config = load_scenario(args.scenario_file)
        print(f"\n📋 Dostępne scenariusze w {args.scenario_file}:")
        for name in config.get('scenarios', {}).keys():
            print(f"  - {name}")
        print()
        return 0
    
    # Uruchom scenariusz
    enable_recording = not args.no_recording
    debug_mode = args.debug
    success = run_scenario(args.scenario_file, args.scenario_name, enable_recording, debug_mode)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
