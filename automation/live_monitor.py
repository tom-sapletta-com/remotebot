#!/usr/bin/env python3
"""
Live Automation Monitor
Web interface with step list and live VNC preview
"""

from flask import Flask, render_template, jsonify, Response, request
from pathlib import Path
import yaml
import time
import io
import base64
from PIL import Image
import cv2
import numpy as np
from threading import Thread, Lock
import sys
import traceback

# Add automation to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from remote_automation import RemoteController, OllamaVision, AutomationEngine
    REMOTE_AVAILABLE = True
except ImportError:
    REMOTE_AVAILABLE = False
    print("⚠️  remote_automation not available")

app = Flask(__name__)

# Global state
current_scenario = None
current_step = 0
scenario_steps = []
scenario_config = {}  # Connection + ollama config
live_controller = None
live_screenshot = None
screenshot_lock = Lock()
monitoring_active = False
automation_engine = None
execution_lock = Lock()
is_executing = False

def load_scenario(yaml_path: str, scenario_name: str):
    """Load scenario from YAML file"""
    global current_scenario, scenario_steps, scenario_config
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    if scenario_name in data.get('scenarios', {}):
        current_scenario = scenario_name
        scenario_steps = data['scenarios'][scenario_name]
        scenario_config = {
            'connection': data.get('connection', {}),
            'ollama': data.get('ollama', {})
        }
        return True
    return False

def capture_vnc_screenshot():
    """Capture screenshot from VNC"""
    global live_controller, live_screenshot, screenshot_lock
    
    if not REMOTE_AVAILABLE:
        print("[Monitor] Cannot capture screenshot: REMOTE_AVAILABLE=False")
        return None
        
    if not live_controller:
        print("[Monitor] Cannot capture screenshot: live_controller is None")
        return None
    
    try:
        print("[Monitor] Capturing screenshot...")
        screen = live_controller.capture_screen()
        
        if screen is None:
            print("[Monitor] Screenshot capture returned None")
            return None
        
        # Convert PIL to bytes for streaming
        img_io = io.BytesIO()
        screen.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        
        screenshot_data = img_io.getvalue()
        print(f"[Monitor] Screenshot captured successfully ({len(screenshot_data)} bytes)")
        
        with screenshot_lock:
            live_screenshot = screenshot_data
        
        return live_screenshot
    except Exception as e:
        print(f"[Monitor] Screenshot error: {e}")
        traceback.print_exc()
        return None

def screenshot_worker():
    """Background thread for capturing screenshots"""
    global monitoring_active, live_controller
    
    while monitoring_active:
        if live_controller and live_controller.connection:
            capture_vnc_screenshot()
        time.sleep(1)  # 1 FPS

@app.route('/')
def index():
    """Main monitoring page"""
    return render_template('monitor.html')

@app.route('/api/scenarios')
def list_scenarios():
    """List available scenarios"""
    scenarios_dir = Path('/app/test_scenarios')
    scenarios = []
    
    for yaml_file in scenarios_dir.glob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if 'scenarios' in data:
                for scenario_name in data['scenarios'].keys():
                    scenarios.append({
                        'file': yaml_file.name,
                        'name': scenario_name,
                        'path': str(yaml_file)
                    })
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}")
    
    return jsonify(scenarios)

@app.route('/api/load/<path:yaml_file>/<scenario_name>')
def load_scenario_api(yaml_file, scenario_name):
    """Load specific scenario"""
    global current_step
    
    yaml_path = f'/app/test_scenarios/{yaml_file}'
    
    if load_scenario(yaml_path, scenario_name):
        current_step = 0
        return jsonify({
            'success': True,
            'scenario': scenario_name,
            'steps': scenario_steps,
            'step_count': len(scenario_steps)
        })
    
    return jsonify({'success': False, 'error': 'Scenario not found'}), 404

@app.route('/api/steps')
def get_steps():
    """Get current scenario steps"""
    return jsonify({
        'scenario': current_scenario,
        'current_step': current_step,
        'steps': scenario_steps,
        'total': len(scenario_steps)
    })

@app.route('/api/connect')
def connect_vnc():
    """Connect to VNC"""
    global live_controller, monitoring_active
    
    if not REMOTE_AVAILABLE:
        return jsonify({'success': False, 'error': 'Remote automation not available'}), 500
    
    try:
        live_controller = RemoteController(
            protocol='vnc',
            host='vnc-desktop',
            port=5901,
            password='automation'
        )
        live_controller.connect()
        
        # Start screenshot worker
        monitoring_active = True
        thread = Thread(target=screenshot_worker, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Connected to VNC'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disconnect')
def disconnect_vnc():
    """Disconnect from VNC"""
    global live_controller, monitoring_active
    
    monitoring_active = False
    
    if live_controller:
        try:
            live_controller.disconnect()
        except:
            pass
        live_controller = None
    
    return jsonify({'success': True, 'message': 'Disconnected'})

@app.route('/api/screenshot')
def get_screenshot():
    """Get latest screenshot as base64"""
    global live_screenshot, screenshot_lock
    
    with screenshot_lock:
        if live_screenshot:
            img_base64 = base64.b64encode(live_screenshot).decode('utf-8')
            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{img_base64}'
            })
    
    return jsonify({'success': False, 'error': 'No screenshot available'}), 404

@app.route('/video_feed')
def video_feed():
    """MJPEG video stream"""
    def generate():
        global live_screenshot, screenshot_lock
        
        while monitoring_active:
            with screenshot_lock:
                if live_screenshot:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + live_screenshot + b'\r\n')
            time.sleep(1)  # 1 FPS
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get monitoring status"""
    return jsonify({
        'connected': live_controller is not None and live_controller.connection is not None,
        'monitoring': monitoring_active,
        'scenario': current_scenario,
        'current_step': current_step,
        'total_steps': len(scenario_steps),
        'is_executing': is_executing
    })

@app.route('/api/execute_step/<int:step_index>')
def execute_step(step_index):
    """Execute specific step"""
    global current_step, is_executing, automation_engine, live_controller
    
    if not REMOTE_AVAILABLE:
        return jsonify({'success': False, 'error': 'Automation not available'}), 500
    
    if not live_controller or not live_controller.connection:
        return jsonify({'success': False, 'error': 'Not connected to VNC'}), 400
    
    if step_index < 0 or step_index >= len(scenario_steps):
        return jsonify({'success': False, 'error': 'Invalid step index'}), 400
    
    with execution_lock:
        if is_executing:
            return jsonify({'success': False, 'error': 'Already executing'}), 409
        
        is_executing = True
        current_step = step_index
    
    try:
        # Initialize engine if not exists
        if not automation_engine:
            try:
                print(f"[Monitor] Initializing automation engine...")
                ollama_config = scenario_config.get('ollama', {})
                print(f"[Monitor] Ollama config: {ollama_config}")
                vision = OllamaVision(
                    base_url=ollama_config.get('url', 'http://ollama:11434'),
                    model=ollama_config.get('model', 'llava:7b')
                )
                automation_engine = AutomationEngine(live_controller, vision, enable_recording=False)
                print(f"[Monitor] Automation engine initialized successfully")
            except Exception as e:
                print(f"[Monitor] Failed to initialize automation engine: {e}")
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': f'Failed to initialize automation engine: {str(e)}',
                    'traceback': traceback.format_exc()
                }), 500
        
        # Execute single step
        step = scenario_steps[step_index]
        
        print(f"[Monitor] Executing step {step_index + 1}: {step.get('action', 'unknown')}")
        print(f"[Monitor] Step details: {step}")
        
        try:
            # Execute the step
            automation_engine.execute_steps([step])
            print(f"[Monitor] Step {step_index + 1} executed successfully")
            
            # Capture screenshot after execution
            time.sleep(0.5)
            capture_vnc_screenshot()
            
            return jsonify({
                'success': True,
                'step_index': step_index,
                'step': step
            })
        except Exception as e:
            print(f"[Monitor] Error executing step: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Step execution failed: {str(e)}',
                'traceback': traceback.format_exc()
            }), 500
    
    except Exception as e:
        print(f"[Monitor] Unexpected error in execute_step: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500
    
    finally:
        is_executing = False

@app.route('/api/execute_all')
def execute_all():
    """Execute all steps in scenario"""
    global current_step, is_executing, automation_engine, live_controller
    
    if not REMOTE_AVAILABLE:
        return jsonify({'success': False, 'error': 'Automation not available'}), 500
    
    if not live_controller or not live_controller.connection:
        return jsonify({'success': False, 'error': 'Not connected to VNC'}), 400
    
    if not scenario_steps:
        return jsonify({'success': False, 'error': 'No scenario loaded'}), 400
    
    with execution_lock:
        if is_executing:
            return jsonify({'success': False, 'error': 'Already executing'}), 409
        
        is_executing = True
    
    def run_scenario():
        global current_step, is_executing, automation_engine
        
        try:
            # Initialize engine if not exists
            if not automation_engine:
                ollama_config = scenario_config.get('ollama', {})
                vision = OllamaVision(
                    base_url=ollama_config.get('url', 'http://ollama:11434'),
                    model=ollama_config.get('model', 'llava:7b')
                )
                automation_engine = AutomationEngine(live_controller, vision, enable_recording=False)
            
            # Execute all steps
            for i, step in enumerate(scenario_steps):
                current_step = i
                print(f"[Monitor] Executing step {i + 1}/{len(scenario_steps)}: {step.get('action', 'unknown')}")
                
                automation_engine.execute_steps([step])
                
                # Capture screenshot after each step
                time.sleep(0.5)
                capture_vnc_screenshot()
            
            print(f"[Monitor] Scenario completed!")
            
        except Exception as e:
            print(f"[Monitor] Error executing scenario: {e}")
        
        finally:
            is_executing = False
            current_step = 0
    
    # Run in background thread
    thread = Thread(target=run_scenario, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Scenario execution started',
        'total_steps': len(scenario_steps)
    })

# HTML Template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Automation Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #e0e0e0;
            height: 100vh;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 400px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            padding: 20px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
        }
        
        .header h1 {
            font-size: 18px;
            margin-bottom: 10px;
            color: #4fc3f7;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        button {
            padding: 8px 16px;
            background: #0e639c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        button:hover {
            background: #1177bb;
        }
        
        button:disabled {
            background: #3e3e42;
            cursor: not-allowed;
        }
        
        .scenario-selector {
            padding: 15px 20px;
            border-bottom: 1px solid #3e3e42;
        }
        
        select {
            width: 100%;
            padding: 8px;
            background: #3c3c3c;
            color: #e0e0e0;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .steps-container {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .step {
            padding: 12px;
            margin-bottom: 8px;
            background: #2d2d30;
            border-left: 3px solid #3e3e42;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .step:hover {
            background: #333333;
        }
        
        .step.active {
            border-left-color: #4fc3f7;
            background: #264f78;
        }
        
        .step.completed {
            border-left-color: #6a9955;
            opacity: 0.7;
        }
        
        .step-number {
            font-size: 12px;
            color: #858585;
            margin-bottom: 4px;
        }
        
        .step-action {
            font-weight: 600;
            color: #4fc3f7;
            margin-bottom: 4px;
        }
        
        .step-details {
            font-size: 13px;
            color: #cccccc;
        }
        
        .execute-btn {
            margin-top: 8px;
            padding: 6px 12px;
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            width: 100%;
        }
        
        .execute-btn:hover {
            background: #388e3c;
        }
        
        .step.executing {
            border-left-color: #ff9800;
            background: #4a3c1a;
            animation: pulse 1s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .preview {
            flex: 1;
            background: #1e1e1e;
            display: flex;
            flex-direction: column;
        }
        
        .preview-header {
            padding: 20px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
        }
        
        .preview-header h2 {
            font-size: 16px;
            color: #4fc3f7;
        }
        
        .status {
            margin-top: 10px;
            padding: 8px 12px;
            background: #1e1e1e;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .status.connected { color: #6a9955; }
        .status.disconnected { color: #f48771; }
        
        .preview-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .preview-content img {
            max-width: 100%;
            max-height: 100%;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .no-preview {
            text-align: center;
            color: #858585;
        }
        
        .no-preview h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }
        
        .spinner {
            border: 3px solid #3e3e42;
            border-top: 3px solid #4fc3f7;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="header">
                <h1>🎬 Live Automation Monitor</h1>
                <div class="controls">
                    <button id="connectBtn" onclick="connect()">Connect VNC</button>
                    <button id="disconnectBtn" onclick="disconnect()" disabled>Disconnect</button>
                    <button id="runAllBtn" onclick="executeAll()" disabled style="background: #2e7d32; margin-left: 10px;">▶ Run All</button>
                </div>
            </div>
            
            <div class="scenario-selector">
                <label for="scenarioSelect" style="display: block; margin-bottom: 8px; font-size: 13px; color: #858585;">
                    Select Scenario:
                </label>
                <select id="scenarioSelect" onchange="loadScenario()">
                    <option value="">-- Choose Scenario --</option>
                </select>
            </div>
            
            <div class="steps-container" id="stepsContainer">
                <div class="no-preview">
                    <h3>No scenario loaded</h3>
                    <p>Select a scenario from the dropdown above</p>
                </div>
            </div>
        </div>
        
        <div class="preview">
            <div class="preview-header">
                <h2>📺 Live VNC Preview</h2>
                <div class="status disconnected" id="status">
                    Status: Disconnected
                </div>
            </div>
            
            <div class="preview-content" id="previewContent">
                <div class="no-preview">
                    <h3>No VNC Connection</h3>
                    <p>Click "Connect VNC" to start monitoring</p>
                    <div class="spinner" style="display: none;" id="spinner"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let connected = false;
        let updateInterval = null;
        
        // Load scenarios on page load
        fetch('/api/scenarios')
            .then(r => r.json())
            .then(scenarios => {
                const select = document.getElementById('scenarioSelect');
                scenarios.forEach(s => {
                    const option = document.createElement('option');
                    option.value = `${s.file}|||${s.name}`;
                    option.textContent = `${s.file} → ${s.name}`;
                    select.appendChild(option);
                });
            });
        
        function loadScenario() {
            const select = document.getElementById('scenarioSelect');
            const value = select.value;
            
            if (!value) {
                document.getElementById('runAllBtn').disabled = true;
                return;
            }
            
            const [file, name] = value.split('|||');
            
            fetch(`/api/load/${file}/${name}`)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        displaySteps(data.steps);
                        // Enable Run All button if connected
                        if (connected) {
                            document.getElementById('runAllBtn').disabled = false;
                        }
                    }
                });
        }
        
        function displaySteps(steps) {
            const container = document.getElementById('stepsContainer');
            container.innerHTML = '';
            
            steps.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'step';
                stepDiv.id = `step-${index}`;
                
                const action = step.action || 'unknown';
                const details = Object.entries(step)
                    .filter(([k, v]) => k !== 'action')
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(', ');
                
                stepDiv.innerHTML = `
                    <div class="step-number">Step ${index + 1}</div>
                    <div class="step-action">${action}</div>
                    ${details ? `<div class="step-details">${details}</div>` : ''}
                    <button class="execute-btn" onclick="executeStep(${index})">▶ Execute</button>
                `;
                
                container.appendChild(stepDiv);
            });
        }
        
        function executeStep(stepIndex) {
            fetch(`/api/execute_step/${stepIndex}`)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        // Highlight executed step
                        document.querySelectorAll('.step').forEach(s => s.classList.remove('executing'));
                        document.getElementById(`step-${stepIndex}`).classList.add('executing');
                        
                        console.log(`Executed step ${stepIndex + 1}`);
                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(err => {
                    console.error('Execute error:', err);
                    alert(`Failed to execute step: ${err}`);
                });
        }
        
        function executeAll() {
            if (!confirm('Execute all steps in scenario?')) {
                return;
            }
            
            fetch('/api/execute_all')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        console.log('Scenario execution started');
                        startStatusPolling();
                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(err => {
                    console.error('Execute all error:', err);
                    alert(`Failed to execute scenario: ${err}`);
                });
        }
        
        function startStatusPolling() {
            const pollInterval = setInterval(() => {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(status => {
                        // Update current step highlight
                        document.querySelectorAll('.step').forEach(s => s.classList.remove('executing'));
                        if (status.is_executing && status.current_step >= 0) {
                            const stepEl = document.getElementById(`step-${status.current_step}`);
                            if (stepEl) {
                                stepEl.classList.add('executing');
                                stepEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            }
                        }
                        
                        // Stop polling when done
                        if (!status.is_executing) {
                            clearInterval(pollInterval);
                        }
                    })
                    .catch(err => console.error('Status poll error:', err));
            }, 500);  // Poll every 500ms
        }
        
        function connect() {
            const spinner = document.getElementById('spinner');
            if (spinner) spinner.style.display = 'block';
            
            fetch('/api/connect')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        connected = true;
                        document.getElementById('connectBtn').disabled = true;
                        document.getElementById('disconnectBtn').disabled = false;
                        document.getElementById('status').className = 'status connected';
                        document.getElementById('status').textContent = 'Status: Connected ✓';
                        
                        // Enable Run All if scenario loaded
                        const scenarioSelect = document.getElementById('scenarioSelect');
                        if (scenarioSelect.value) {
                            document.getElementById('runAllBtn').disabled = false;
                        }
                        
                        startLivePreview();
                    }
                })
                .finally(() => {
                    const spinner = document.getElementById('spinner');
                    if (spinner) spinner.style.display = 'none';
                });
        }
        
        function disconnect() {
            fetch('/api/disconnect')
                .then(() => {
                    connected = false;
                    document.getElementById('connectBtn').disabled = false;
                    document.getElementById('disconnectBtn').disabled = true;
                    document.getElementById('runAllBtn').disabled = true;
                    document.getElementById('status').className = 'status disconnected';
                    document.getElementById('status').textContent = 'Status: Disconnected';
                    
                    stopLivePreview();
                });
        }
        
        function startLivePreview() {
            const preview = document.getElementById('previewContent');
            preview.innerHTML = '<img id="liveImage" src="" alt="VNC Preview">';
            
            updateInterval = setInterval(updateScreenshot, 1000);
            updateScreenshot();
        }
        
        function stopLivePreview() {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
            
            document.getElementById('previewContent').innerHTML = `
                <div class="no-preview">
                    <h3>Disconnected</h3>
                    <p>Connect to VNC to see live preview</p>
                </div>
            `;
        }
        
        function updateScreenshot() {
            if (!connected) return;
            
            fetch('/api/screenshot')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('liveImage').src = data.image;
                    }
                })
                .catch(err => console.error('Screenshot update error:', err));
        }
    </script>
</body>
</html>'''

# Create templates directory and save HTML
templates_dir = Path(__file__).parent / 'templates'
templates_dir.mkdir(exist_ok=True)
(templates_dir / 'monitor.html').write_text(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🎬 Starting Live Automation Monitor...")
    print("📺 Open: http://localhost:5000")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
