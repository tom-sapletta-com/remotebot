#!/usr/bin/env python3
"""
CLI Runner dla Remote Automation
Użycie: python automation_cli.py config.yaml scenario_name
"""

import sys
import yaml
import argparse
from pathlib import Path

# Import głównej aplikacji
# from remote_automation import RemoteController, OllamaVision, AutomationEngine


def load_config(config_file: str) -> dict:
    """Wczytuje konfigurację z YAML"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def list_scenarios(config: dict):
    """Wyświetla dostępne scenariusze"""
    print("\n📋 Dostępne scenariusze:\n")
    scenarios = config.get('scenarios', {})
    
    for name, steps in scenarios.items():
        print(f"  • {name}")
        print(f"    Kroków: {len(steps)}")
        
        # Pokaż pierwsze 2 akcje
        if steps:
            print(f"    Rozpoczyna od: {steps[0].get('action', 'unknown')}")
        print()


def run_scenario(config: dict, scenario_name: str, dry_run: bool = False):
    """Uruchamia wybrany scenariusz"""
    
    scenarios = config.get('scenarios', {})
    
    if scenario_name not in scenarios:
        print(f"❌ Scenariusz '{scenario_name}' nie istnieje")
        print("\nDostępne scenariusze:")
        for name in scenarios.keys():
            print(f"  • {name}")
        return False
    
    script = scenarios[scenario_name]
    
    if dry_run:
        print(f"\n🔍 Dry run scenariusza: {scenario_name}\n")
        for i, step in enumerate(script, 1):
            action = step.get('action', 'unknown')
            print(f"  {i}. {action}")
            
            # Pokaż szczegóły
            for key, value in step.items():
                if key != 'action':
                    print(f"     {key}: {value}")
        print()
        return True
    
    # Rzeczywiste uruchomienie
    print(f"\n🚀 Uruchamiam scenariusz: {scenario_name}\n")
    
    try:
        # Import tutaj aby uniknąć błędów jeśli tylko listujemy
        from remote_automation import RemoteController, OllamaVision, AutomationEngine
        
        # Konfiguracja połączenia
        conn_config = config.get('connection', {})
        controller = RemoteController(
            protocol=conn_config.get('protocol', 'vnc'),
            host=conn_config.get('host', 'localhost'),
            port=conn_config.get('port', 5900),
            username=conn_config.get('username', ''),
            password=conn_config.get('password', '')
        )
        
        # Konfiguracja Ollama
        ollama_config = config.get('ollama', {})
        vision = OllamaVision(
            base_url=ollama_config.get('url', 'http://localhost:11434'),
            model=ollama_config.get('model', 'llava:7b')
        )
        
        # Wykonaj
        engine = AutomationEngine(controller, vision)
        engine.execute_dsl(script)
        
        print("\n✅ Scenariusz zakończony pomyślnie!")
        
        # Pokaż zebrane zmienne
        if engine.variables:
            print("\n📊 Zebrane dane:")
            for key, value in engine.variables.items():
                print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_mode(config: dict):
    """Tryb interaktywny"""
    print("\n🎮 Tryb interaktywny\n")
    
    while True:
        print("\nOpcje:")
        print("  1. Lista scenariuszy")
        print("  2. Uruchom scenariusz")
        print("  3. Dry run scenariusza")
        print("  4. Edytuj konfigurację")
        print("  0. Wyjście")
        
        choice = input("\nWybierz opcję: ").strip()
        
        if choice == '0':
            print("👋 Do zobaczenia!")
            break
        
        elif choice == '1':
            list_scenarios(config)
        
        elif choice == '2':
            list_scenarios(config)
            scenario = input("\nNazwa scenariusza: ").strip()
            if scenario:
                run_scenario(config, scenario)
        
        elif choice == '3':
            list_scenarios(config)
            scenario = input("\nNazwa scenariusza: ").strip()
            if scenario:
                run_scenario(config, scenario, dry_run=True)
        
        elif choice == '4':
            print("\nAktualna konfiguracja:")
            print(yaml.dump(config.get('connection', {}), default_flow_style=False))
            print("\nEdytuj config.yaml ręcznie i uruchom ponownie program")
        
        else:
            print("❌ Nieprawidłowa opcja")


def create_sample_config():
    """Tworzy przykładowy plik konfiguracyjny"""
    sample = {
        'connection': {
            'protocol': 'vnc',
            'host': 'localhost',
            'port': 5900,
            'password': ''
        },
        'ollama': {
            'url': 'http://localhost:11434',
            'model': 'llava:7b'
        },
        'scenarios': {
            'hello_world': [
                {'action': 'connect'},
                {'action': 'wait', 'seconds': 1},
                {'action': 'analyze', 'question': 'What do you see on the screen?'},
                {'action': 'disconnect'}
            ]
        }
    }
    
    filename = 'config_sample.yaml'
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(sample, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Utworzono przykładowy plik: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Remote Automation CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s config.yaml --list                    # Lista scenariuszy
  %(prog)s config.yaml --run browser_search      # Uruchom scenariusz
  %(prog)s config.yaml --dry-run browser_search  # Symulacja
  %(prog)s --create-config                       # Utwórz przykładowy config
  %(prog)s config.yaml --interactive             # Tryb interaktywny
        """
    )
    
    parser.add_argument(
        'config', 
        nargs='?',
        help='Plik konfiguracyjny YAML'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Pokaż dostępne scenariusze'
    )
    
    parser.add_argument(
        '--run', '-r',
        metavar='SCENARIO',
        help='Uruchom scenariusz'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        metavar='SCENARIO',
        help='Symuluj scenariusz bez wykonywania'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Tryb interaktywny'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Utwórz przykładowy plik konfiguracyjny'
    )
    
    args = parser.parse_args()
    
    # Utwórz przykładowy config
    if args.create_config:
        create_sample_config()
        return 0
    
    # Sprawdź czy podano config
    if not args.config:
        if args.interactive or args.list or args.run or args.dry_run:
            parser.error("Wymagany plik konfiguracyjny")
        parser.print_help()
        return 1
    
    # Sprawdź czy plik istnieje
    if not Path(args.config).exists():
        print(f"❌ Plik nie istnieje: {args.config}")
        print("\nUżyj --create-config aby utworzyć przykładowy plik")
        return 1
    
    # Wczytaj konfigurację
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Błąd wczytywania konfiguracji: {e}")
        return 1
    
    # Wykonaj akcję
    if args.list:
        list_scenarios(config)
    
    elif args.run:
        success = run_scenario(config, args.run)
        return 0 if success else 1
    
    elif args.dry_run:
        run_scenario(config, args.dry_run, dry_run=True)
    
    elif args.interactive:
        interactive_mode(config)
    
    else:
        # Domyślnie: tryb interaktywny jeśli tylko podano config
        interactive_mode(config)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
