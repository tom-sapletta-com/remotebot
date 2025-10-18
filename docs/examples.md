# 📚 Examples & Integration Patterns

Praktyczne przykłady użycia i integracje z popularnymi frameworkami.

## 📑 Spis treści

- [Podstawowe przykłady](#podstawowe-przykłady)
- [Pytest Integration](#pytest-integration)
- [Python Scripts](#python-scripts)
- [Scheduled Tasks](#scheduled-tasks)
- [Web Dashboard](#web-dashboard)
- [Slack/Discord Notifications](#slackdiscord-notifications)
- [Data Processing](#data-processing)

---

## Podstawowe przykłady

### Hello World - Minimalna automatyzacja

```python
#!/usr/bin/env python3
from remote_automation import RemoteController, OllamaVision, AutomationEngine

# Konfiguracja
controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
vision = OllamaVision('http://ollama:11434', 'llava:7b')
engine = AutomationEngine(controller, vision)

# Prosty scenariusz
script = [
    {'action': 'connect'},
    {'action': 'wait', 'seconds': 2},
    {'action': 'analyze', 'question': 'What desktop environment is this?'},
    {'action': 'disconnect'}
]

# Wykonaj
engine.execute_dsl(script)
print(f"Result: {engine.variables}")
```

### Parametryzowane testy

```python
#!/usr/bin/env python3
def test_multiple_websites(websites):
    """Test multiple websites in one go"""
    
    for url in websites:
        script = [
            {'action': 'connect'},
            {'action': 'find_and_click', 'element': 'Firefox'},
            {'action': 'wait', 'seconds': 3},
            {'action': 'type', 'text': url},
            {'action': 'key', 'key': 'enter'},
            {'action': 'wait', 'seconds': 3},
            {'action': 'analyze', 'question': f'Is {url} loaded successfully?'},
            {'action': 'disconnect'}
        ]
        
        engine.execute_dsl(script)
        print(f"{url}: {engine.variables.get('result', 'unknown')}")

# Uruchom
websites = ['https://example.com', 'https://github.com', 'https://python.org']
test_multiple_websites(websites)
```

---

## Pytest Integration

### Struktura testów

```
tests/
├── conftest.py          # Fixtures
├── test_browser.py      # Testy przeglądarki
├── test_forms.py        # Testy formularzy
└── test_accessibility.py # Testy dostępności
```

### conftest.py - Shared fixtures

```python
# tests/conftest.py
import pytest
import sys
sys.path.insert(0, '/app')

from remote_automation import RemoteController, OllamaVision, AutomationEngine

@pytest.fixture(scope="session")
def vnc_controller():
    """Reusable VNC connection"""
    controller = RemoteController(
        protocol='vnc',
        host='vnc-desktop',
        port=5901,
        password='automation'
    )
    controller.connect()
    yield controller
    controller.disconnect()

@pytest.fixture(scope="session")
def vision():
    """Ollama vision instance"""
    return OllamaVision('http://ollama:11434', 'llava:7b')

@pytest.fixture
def automation_engine(vnc_controller, vision):
    """Fresh engine for each test"""
    return AutomationEngine(vnc_controller, vision)

@pytest.fixture(autouse=True)
def reset_desktop(vnc_controller):
    """Reset desktop state before each test"""
    # Close all windows
    vnc_controller.key_press('alt+F4')
    yield
    # Cleanup after test
    vnc_controller.key_press('alt+F4')
```

### test_browser.py

```python
# tests/test_browser.py
import pytest

def test_firefox_opens(automation_engine):
    """Test Firefox browser opens successfully"""
    script = [
        {'action': 'find_and_click', 'element': 'Firefox icon'},
        {'action': 'wait', 'seconds': 5},
        {'action': 'verify', 'expected': 'Firefox is open'}
    ]
    
    automation_engine.execute_dsl(script)
    # Assert based on results
    assert 'Firefox is open' in str(automation_engine.variables)

def test_google_search(automation_engine):
    """Test Google search functionality"""
    script = [
        {'action': 'find_and_click', 'element': 'Firefox'},
        {'action': 'wait', 'seconds': 3},
        {'action': 'type', 'text': 'https://google.com'},
        {'action': 'key', 'key': 'enter'},
        {'action': 'wait', 'seconds': 3},
        {'action': 'analyze', 'question': 'Is Google search page visible?', 'save_to': 'google_loaded'},
        {'action': 'find_and_click', 'element': 'search box'},
        {'action': 'type', 'text': 'Python automation'},
        {'action': 'key', 'key': 'enter'},
        {'action': 'wait', 'seconds': 3},
        {'action': 'analyze', 'question': 'Are search results displayed?', 'save_to': 'results'}
    ]
    
    automation_engine.execute_dsl(script)
    assert 'yes' in automation_engine.variables.get('results', '').lower()

@pytest.mark.parametrize("url,expected", [
    ("https://example.com", "Example Domain"),
    ("https://github.com", "GitHub"),
    ("https://python.org", "Python"),
])
def test_website_titles(automation_engine, url, expected):
    """Test multiple websites load correctly"""
    script = [
        {'action': 'find_and_click', 'element': 'Firefox'},
        {'action': 'wait', 'seconds': 3},
        {'action': 'type', 'text': url},
        {'action': 'key', 'key': 'enter'},
        {'action': 'wait', 'seconds': 3},
        {'action': 'analyze', 'question': f'What is the main heading or title?', 'save_to': 'title'}
    ]
    
    automation_engine.execute_dsl(script)
    title = automation_engine.variables.get('title', '')
    assert expected.lower() in title.lower()
```

### Uruchomienie testów

```bash
# Wszystkie testy
docker-compose exec automation-controller pytest tests/

# Konkretny plik
docker-compose exec automation-controller pytest tests/test_browser.py

# Z raportem HTML
docker-compose exec automation-controller pytest tests/ --html=report.html

# Verbose
docker-compose exec automation-controller pytest tests/ -v

# Tylko failed
docker-compose exec automation-controller pytest tests/ --lf
```

---

## Python Scripts

### Scheduled monitoring script

```python
#!/usr/bin/env python3
"""
scheduled_monitor.py - Monitor application health
Run: python3 scheduled_monitor.py
"""

import time
from datetime import datetime
from remote_automation import RemoteController, OllamaVision, AutomationEngine
import json

def check_application_health():
    """Check if application is healthy"""
    controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
    vision = OllamaVision('http://ollama:11434', 'llava:7b')
    engine = AutomationEngine(controller, vision)
    
    script = [
        {'action': 'connect'},
        {'action': 'analyze', 'question': 'Is the desktop responsive? Any error dialogs?', 'save_to': 'health'},
        {'action': 'find_and_click', 'element': 'Terminal'},
        {'action': 'wait', 'seconds': 2},
        {'action': 'type', 'text': 'free -h'},
        {'action': 'key', 'key': 'enter'},
        {'action': 'wait', 'seconds': 1},
        {'action': 'analyze', 'question': 'What is memory usage?', 'save_to': 'memory'},
        {'action': 'disconnect'}
    ]
    
    engine.execute_dsl(script)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'health': engine.variables.get('health', 'unknown'),
        'memory': engine.variables.get('memory', 'unknown')
    }

def main():
    """Run monitoring loop"""
    while True:
        try:
            result = check_application_health()
            
            # Save results
            with open('monitoring_results.jsonl', 'a') as f:
                f.write(json.dumps(result) + '
')
            
            print(f"[{result['timestamp']}] Health check completed")
            
            # Check if unhealthy
            if 'error' in result['health'].lower():
                print("⚠️ ALERT: Application appears unhealthy!")
                # Send alert (implement notification)
            
        except Exception as e:
            print(f"Error in health check: {e}")
        
        # Wait 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    main()
```

### Batch processing script

```python
#!/usr/bin/env python3
"""
batch_processor.py - Process multiple tasks
"""

from pathlib import Path
import csv
from remote_automation import RemoteController, OllamaVision, AutomationEngine

def process_urls_from_csv(csv_file):
    """Process list of URLs from CSV"""
    
    results = []
    
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        urls = list(reader)
    
    controller = RemoteController('vnc', 'vnc-desktop', 5901, password='automation')
    vision = OllamaVision('http://ollama:11434', 'llava:7b')
    
    controller.connect()
    
    for i, row in enumerate(urls, 1):
        url = row['url']
        print(f"[{i}/{len(urls)}] Processing: {url}")
        
        engine = AutomationEngine(controller, vision)
        
        script = [
            {'action': 'find_and_click', 'element': 'Firefox'},
            {'action': 'wait', 'seconds': 2},
            {'action': 'key', 'key': 'ctrl+l'},
            {'action': 'type', 'text': url},
            {'action': 'key', 'key': 'enter'},
            {'action': 'wait', 'seconds': 3},
            {'action': 'analyze', 'question': 'Extract the main heading and meta description', 'save_to': 'data'},
            {'action': 'key', 'key': 'ctrl+w'}  # Close tab
        ]
        
        engine.execute_dsl(script)
        
        results.append({
            'url': url,
            'data': engine.variables.get('data', '')
        })
    
    controller.disconnect()
    
    # Save results
    with open('batch_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'data'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Processed {len(results)} URLs")

# Usage
process_urls_from_csv('urls.csv')
```

---

## Scheduled Tasks

### Cron job example

```bash
# Dodaj do crontab
crontab -e

# Uruchom co godzinę
0 * * * * cd /path/to/remote-automation && docker-compose exec -T automation-controller python3 /app/scheduled_monitor.py

# Uruchom codziennie o 2:00
0 2 * * * cd /path/to/remote-automation && docker-compose exec -T automation-controller python3 /app/daily_report.py

# Backup wyników co tydzień
0 0 * * 0 cd /path/to/remote-automation && make backup-results
```

### Systemd service (Linux)

```bash
# /etc/systemd/system/automation-monitor.service
[Unit]
Description=Remote Automation Monitor
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/path/to/remote-automation
ExecStart=/usr/bin/docker-compose exec -T automation-controller python3 /app/scheduled_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable automation-monitor
sudo systemctl start automation-monitor
sudo systemctl status automation-monitor
```

---

## Web Dashboard

### Flask dashboard example

```python
#!/usr/bin/env python3
"""
dashboard.py - Simple web dashboard
Run: python3 dashboard.py
Access: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from remote_automation import RemoteController, OllamaVision, AutomationEngine
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """Get system status"""
    # Check services
    return jsonify({
        'vnc': check_vnc_status(),
        'ollama': check_ollama_status(),
        'tests': get_recent_tests()
    })

@app.route('/api/run-test', methods=['POST'])
def run_test():
    """Run a test scenario"""
    scenario_name = request.json.get('scenario')
    
    # Run test in background
    # ... implementation
    
    return jsonify({'status': 'started', 'scenario': scenario_name})

@app.route('/api/results')
def results():
    """Get test results"""
    results_file = Path('results/test_results.json')
    if results_file.exists():
        with open(results_file) as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'No results found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Slack/Discord Notifications

### Slack integration

```python
#!/usr/bin/env python3
"""
slack_notifier.py - Send alerts to Slack
"""

import requests
import json

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def send_slack_alert(message, status='info'):
    """Send alert to Slack"""
    
    color_map = {
        'success': '#36a64f',
        'warning': '#ff9900',
        'error': '#ff0000',
        'info': '#0099ff'
    }
    
    payload = {
        'attachments': [{
            'color': color_map.get(status, '#0099ff'),
            'title': 'Remote Automation Alert',
            'text': message,
            'footer': 'Automation Bot',
            'ts': int(time.time())
        }]
    }
    
    response = requests.post(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    
    return response.status_code == 200

# Usage
if test_failed:
    send_slack_alert(
        f"❌ Test failed: {test_name}
{error_message}",
        status='error'
    )
```

### Discord webhook

```python
def send_discord_notification(message, webhook_url):
    """Send notification to Discord"""
    
    payload = {
        'content': message,
        'username': 'Automation Bot',
        'avatar_url': 'https://example.com/bot-avatar.png'
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 204
```

---

## Data Processing

### Export to Excel

```python
#!/usr/bin/env python3
"""
export_to_excel.py - Export test results to Excel
"""

import pandas as pd
import json
from pathlib import Path

def export_results_to_excel():
    """Export test results to Excel file"""
    
    # Load results
    results_file = Path('results/test_results.json')
    with open(results_file) as f:
        data = json.load(f)
    
    # Create DataFrame
    tests = data.get('tests', [])
    df = pd.DataFrame(tests)
    
    # Add summary sheet
    summary = pd.DataFrame([data.get('summary', {})])
    
    # Write to Excel
    with pd.ExcelWriter('test_results.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Tests', index=False)
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print("✅ Results exported to test_results.xlsx")

export_results_to_excel()
```

### Generate PDF report

```python
#!/usr/bin/env python3
"""
generate_pdf_report.py - Generate PDF test report
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json

def generate_pdf_report(results_file, output_file='test_report.pdf'):
    """Generate PDF report from test results"""
    
    # Load data
    with open(results_file) as f:
        data = json.load(f)
    
    # Create PDF
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Test Results Report", styles['Title'])
    elements.append(title)
    
    # Summary table
    summary = data.get('summary', {})
    summary_data = [
        ['Metric', 'Value'],
        ['Total Tests', summary.get('total', 0)],
        ['Passed', summary.get('passed', 0)],
        ['Failed', summary.get('failed', 0)],
        ['Duration', f"{summary.get('duration', 0):.2f}s"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF report generated: {output_file}")

generate_pdf_report('results/test_results.json')
```

---

## Więcej przykładów

Zobacz folder `examples/` w projekcie dla:
- Integration z Jenkins
- GitLab CI templates  
- Azure DevOps pipelines
- Custom reporters
- Performance benchmarks
- Visual regression tests

---

**Pytania?** Zobacz [README.md](README.md) lub [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
