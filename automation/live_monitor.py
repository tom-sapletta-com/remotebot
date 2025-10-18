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

# Add automation to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from remote_automation import RemoteController
    REMOTE_AVAILABLE = True
except ImportError:
    REMOTE_AVAILABLE = False
    print("⚠️  remote_automation not available")

app = Flask(__name__)

# Global state
current_scenario = None
current_step = 0
scenario_steps = []
live_controller = None
live_screenshot = None
screenshot_lock = Lock()
monitoring_active = False

def load_scenario(yaml_path: str, scenario_name: str):
    """Load scenario from YAML file"""
    global current_scenario, scenario_steps
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    if scenario_name in data.get('scenarios', {}):
        current_scenario = scenario_name
        scenario_steps = data['scenarios'][scenario_name]
        return True
    return False

def capture_vnc_screenshot():
    """Capture screenshot from VNC"""
    global live_controller, live_screenshot, screenshot_lock
    
    if not REMOTE_AVAILABLE or not live_controller:
        return None
    
    try:
        screen = live_controller.capture_screen()
        
        # Convert PIL to bytes for streaming
        img_io = io.BytesIO()
        screen.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        
        with screenshot_lock:
            live_screenshot = img_io.getvalue()
        
        return live_screenshot
    except Exception as e:
        print(f"Screenshot error: {e}")
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
            
            if (!value) return;
            
            const [file, name] = value.split('|||');
            
            fetch(`/api/load/${file}/${name}`)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        displaySteps(data.steps);
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
                `;
                
                container.appendChild(stepDiv);
            });
        }
        
        function connect() {
            document.getElementById('spinner').style.display = 'block';
            
            fetch('/api/connect')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        connected = true;
                        document.getElementById('connectBtn').disabled = true;
                        document.getElementById('disconnectBtn').disabled = false;
                        document.getElementById('status').className = 'status connected';
                        document.getElementById('status').textContent = 'Status: Connected ✓';
                        
                        startLivePreview();
                    }
                })
                .finally(() => {
                    document.getElementById('spinner').style.display = 'none';
                });
        }
        
        function disconnect() {
            fetch('/api/disconnect')
                .then(() => {
                    connected = false;
                    document.getElementById('connectBtn').disabled = false;
                    document.getElementById('disconnectBtn').disabled = true;
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
