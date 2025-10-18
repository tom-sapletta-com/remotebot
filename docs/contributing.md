# 🤝 Contributing to Remote Automation

Dziękujemy za zainteresowanie wkładem w projekt! Każdy wkład jest ceniony.

## 📋 Spis treści

- [Code of Conduct](#code-of-conduct)
- [Jak pomóc](#jak-pomóc)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

### Nasze zobowiązanie

W trosce o otwarte i przyjazne środowisko, zobowiązujemy się do:

- ✅ Używania przyjaznego i włączającego języka
- ✅ Szanowania różnych punktów widzenia
- ✅ Akceptowania konstruktywnej krytyki
- ✅ Skupiania się na tym co najlepsze dla społeczności

### Niedozwolone zachowania

- ❌ Trolling, obraźliwe komentarze
- ❌ Ataki personalne lub polityczne
- ❌ Publiczne lub prywatne nękanie
- ❌ Publikowanie prywatnych informacji innych osób

---

## Jak pomóc

### 🐛 Zgłaszanie błędów

**Przed zgłoszeniem:**
1. Sprawdź [Issues](https://github.com/your-repo/issues) czy błąd nie został już zgłoszony
2. Przeczytaj [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Upewnij się że używasz najnowszej wersji

**Zgłaszając błąd, dołącz:**
- Jasny opis problemu
- Kroki do reprodukcji
- Oczekiwane vs faktyczne zachowanie
- Wersje (OS, Docker, Python)
- Logi i screenshoty

**Template:**
```markdown
## Opis problemu
[Krótki opis]

## Kroki do reprodukcji
1. Uruchom...
2. Kliknij...
3. Zobacz błąd...

## Oczekiwane zachowanie
[Co powinno się stać]

## Faktyczne zachowanie
[Co się stało]

## Środowisko
- OS: Ubuntu 22.04
- Docker: 24.0.0
- Python: 3.11
- Model: llava:7b

## Logi
```
[Wklej logi]
```

## Screenshots
[Dołącz jeśli pomocne]
```

### 💡 Propozycje funkcji

**Przed propozycją:**
1. Sprawdź [Roadmap](README.md#roadmap)
2. Sprawdź czy nie była już zaproponowana

**Template:**
```markdown
## Problem/Use Case
[Jaki problem rozwiązuje ta funkcja?]

## Proponowane rozwiązanie
[Jak to powinno działać?]

## Alternatywy
[Czy rozważałeś inne rozwiązania?]

## Dodatkowy kontekst
[Screenshoty, przykłady, etc.]
```

### 📝 Poprawa dokumentacji

Dokumentacja to kluczowa część projektu!

- Popraw błędy i literówki
- Dodaj przykłady
- Popraw niejasne opisy
- Dodaj tłumaczenia

### 💻 Kod

Zobacz [Development Setup](#development-setup) poniżej.

---

## Development Setup

### 1. Fork i Clone

```bash
# Fork repo na GitHub, następnie:
git clone https://github.com/YOUR-USERNAME/remote-automation.git
cd remote-automation

# Dodaj upstream
git remote add upstream https://github.com/original-repo/remote-automation.git
```

### 2. Utwórz branch

```bash
# Zawsze twórz nowy branch dla zmian
git checkout -b feature/your-feature-name

# Lub dla bugfixa
git checkout -b fix/bug-description
```

### 3. Setup środowiska

```bash
# Uruchom setup
make setup

# Zainstaluj dev dependencies
pip install -r requirements-dev.txt

# Zbuduj środowisko
make build
make up
```

### 4. Wprowadź zmiany

```bash
# Edytuj pliki
# Test locally
make test

# Sprawdź styl kodu
flake8 automation/*.py
black automation/*.py

# Commit
git add .
git commit -m "feat: Add feature description"
```

### 5. Push i Pull Request

```bash
# Push do swojego forka
git push origin feature/your-feature-name

# Utwórz Pull Request na GitHub
```

---

## Pull Request Process

### Before submitting

- [ ] Kod działa lokalnie
- [ ] Testy przechodzą (`make test`)
- [ ] Dokumentacja zaktualizowana
- [ ] Changelog zaktualizowany
- [ ] Kod jest sformatowany (`black`, `flake8`)
- [ ] Commit messages są jasne

### Commit Message Convention

Używamy [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - Nowa funkcja
- `fix:` - Poprawka błędu
- `docs:` - Dokumentacja
- `style:` - Formatowanie (nie wpływa na działanie)
- `refactor:` - Refaktoryzacja kodu
- `test:` - Dodanie/poprawka testów
- `chore:` - Maintenance (deps, build, etc.)

**Przykłady:**
```bash
feat(ollama): Add support for Llama 3 model
fix(vnc): Resolve connection timeout issue
docs(readme): Update installation instructions
test(browser): Add Firefox startup tests
```

### PR Template

```markdown
## Opis zmian
[Co robi ten PR?]

## Typ zmiany
- [ ] Bug fix
- [ ] Nowa funkcja
- [ ] Breaking change
- [ ] Dokumentacja

## Jak przetestować?
1. [Krok 1]
2. [Krok 2]

## Checklist
- [ ] Kod jest przetestowany
- [ ] Testy przechodzą
- [ ] Dokumentacja zaktualizowana
- [ ] Changelog zaktualizowany

## Screenshots (jeśli dotyczy)
[Dodaj screenshots]

## Powiązane Issues
Fixes #123
Related to #456
```

---

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** where appropriate
- **Docstrings** for functions/classes
- **Max line length:** 120 characters

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When input is invalid
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    return len(param1) > param2
```

### Code Formatting

```bash
# Auto-format with black
black automation/*.py

# Check with flake8
flake8 automation/*.py --max-line-length=120

# Sort imports
isort automation/*.py
```

### Naming Conventions

- **Classes:** `PascalCase`
- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

```python
# Good
class RemoteController:
    MAX_RETRIES = 3
    
    def __init__(self):
        self._connection = None
    
    def connect_to_vnc(self, host: str) -> bool:
        pass

# Bad
class remote_controller:
    maxRetries = 3
    
    def ConnectToVNC(self, Host):
        pass
```

---

## Testing Guidelines

### Writing Tests

```python
# tests/test_feature.py
import pytest
from remote_automation import RemoteController

class TestRemoteController:
    """Test suite for RemoteController"""
    
    @pytest.fixture
    def controller(self):
        """Fixture for controller instance"""
        return RemoteController('vnc', 'localhost', 5901)
    
    def test_connect_success(self, controller):
        """Test successful connection"""
        result = controller.connect()
        assert result is True
    
    def test_connect_invalid_host(self, controller):
        """Test connection with invalid host"""
        controller.host = 'invalid-host'
        with pytest.raises(ConnectionError):
            controller.connect()
    
    @pytest.mark.parametrize("protocol,port", [
        ("vnc", 5901),
        ("rdp", 3389),
        ("spice", 5900)
    ])
    def test_multiple_protocols(self, protocol, port):
        """Test different protocols"""
        controller = RemoteController(protocol, 'localhost', port)
        assert controller.protocol == protocol
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/test_feature.py

# With coverage
pytest --cov=automation tests/

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

### Test Coverage

Minimum coverage: **80%**

```bash
# Generate coverage report
pytest --cov=automation --cov-report=html tests/

# View report
open htmlcov/index.html
```

---

## Documentation

### README Updates

- Update [README.md](README.md) for significant changes
- Update [QUICK_START.md](QUICK_START.md) if setup changes
- Update [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

### Code Comments

```python
# Good comments explain WHY, not WHAT
# ✅ GOOD
# Use exponential backoff to avoid overwhelming the server
retry_delay = 2 ** attempt

# ❌ BAD
# Multiply 2 by attempt
retry_delay = 2 ** attempt
```

### Docstrings

```python
def find_element(self, image: Image.Image, element_desc: str) -> Optional[Dict]:
    """
    Find an element on screen using AI vision.
    
    This method uses Ollama to analyze the screenshot and locate
    the specified element based on its description.
    
    Args:
        image: PIL Image object of the screen
        element_desc: Natural language description of the element
                     Example: "Login button in top right"
    
    Returns:
        Dictionary with keys:
            - found (bool): Whether element was found
            - x (int): X coordinate if found
            - y (int): Y coordinate if found
            - confidence (int): Confidence score 0-100
        
        Returns None if analysis fails.
    
    Raises:
        OllamaError: If Ollama API is unreachable
    
    Example:
        >>> controller = RemoteController(...)
        >>> screen = controller.capture_screen()
        >>> result = vision.find_element(screen, "Submit button")
        >>> if result and result['found']:
        ...     controller.click(result['x'], result['y'])
    """
    pass
```

---

## Review Process

### What reviewers look for

1. **Functionality** - Does it work as intended?
2. **Tests** - Are there adequate tests?
3. **Code Quality** - Is it readable and maintainable?
4. **Documentation** - Are changes documented?
5. **Performance** - Any performance implications?
6. **Security** - Any security concerns?

### Addressing Review Comments

```bash
# Make requested changes
git add .
git commit -m "refactor: Address review comments"
git push origin feature/your-feature-name

# If you need to update from main
git fetch upstream
git rebase upstream/main
git push origin feature/your-feature-name --force-with-lease
```

---

## Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes for significant contributions
- Given credit in commit history

---

## Questions?

- Open a [Discussion](https://github.com/your-repo/discussions)
- Join our [Discord](https://discord.gg/your-invite)
- Email: contact@your-project.com

---

## Thank You! 🎉

Your contributions make this project better for everyone. We appreciate your time and effort!

**Happy coding!** 🚀
