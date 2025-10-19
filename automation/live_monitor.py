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
log_buffer = []  # Store last 100 logs
log_lock = Lock()
MAX_LOGS = 100

def add_log(level, message):
    """Add log entry to buffer"""
    global log_buffer
    with log_lock:
        timestamp = time.strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,  # info, success, error, warning
            'message': message
        }
        log_buffer.append(log_entry)
        if len(log_buffer) > MAX_LOGS:
            log_buffer.pop(0)
        print(f"[{timestamp}] [{level.upper()}] {message}")

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
        add_log('error', 'Remote automation not available')
        return jsonify({'success': False, 'error': 'Remote automation not available'}), 500
    
    try:
        add_log('info', 'Connecting to VNC desktop...')
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
        
        add_log('success', 'Connected to VNC successfully!')
        return jsonify({'success': True, 'message': 'Connected to VNC'})
    except Exception as e:
        add_log('error', f'Connection failed: {str(e)}')
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disconnect')
def disconnect_vnc():
    """Disconnect from VNC"""
    global live_controller, monitoring_active
    
    add_log('info', 'Disconnecting from VNC...')
    monitoring_active = False
    
    if live_controller:
        try:
            live_controller.disconnect()
        except:
            pass
        live_controller = None
    
    add_log('success', 'Disconnected from VNC')
    return jsonify({'success': True, 'message': 'Disconnected'})

@app.route('/api/screenshot')
def get_screenshot():
    """Get latest screenshot as base64 (deprecated - use /video_feed instead)"""
    global live_screenshot, screenshot_lock
    
    try:
        with screenshot_lock:
            if live_screenshot and len(live_screenshot) > 0:
                img_base64 = base64.b64encode(live_screenshot).decode('utf-8')
                return jsonify({
                    'success': True,
                    'image': f'data:image/jpeg;base64,{img_base64}'
                })
        
        return jsonify({'success': False, 'error': 'No screenshot available'}), 404
    except Exception as e:
        print(f"[Monitor] Error in get_screenshot: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

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

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    global log_buffer
    with log_lock:
        return jsonify({
            'success': True,
            'logs': log_buffer.copy()
        })

@app.route('/api/logs/clear')
def clear_logs():
    """Clear log buffer"""
    global log_buffer
    with log_lock:
        log_buffer.clear()
    add_log('info', 'Logs cleared')
    return jsonify({'success': True})

@app.route('/api/logs/download')
def download_logs():
    """Download logs as text file"""
    global log_buffer
    with log_lock:
        logs_text = '\n'.join([
            f"[{log['timestamp']}] [{log['level'].upper()}] {log['message']}"
            for log in log_buffer
        ])
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'live_monitor_logs_{timestamp}.txt'
    
    return Response(
        logs_text,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

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
                add_log('info', 'Initializing automation engine...')
                ollama_config = scenario_config.get('ollama', {})
                vision = OllamaVision(
                    base_url=ollama_config.get('url', 'http://ollama:11434'),
                    model=ollama_config.get('model', 'llava:7b')
                )
                automation_engine = AutomationEngine(live_controller, vision, enable_recording=False)
                add_log('success', 'Automation engine initialized')
            except Exception as e:
                add_log('error', f'Failed to initialize engine: {str(e)}')
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': f'Failed to initialize automation engine: {str(e)}',
                    'traceback': traceback.format_exc()
                }), 500
        
        # Execute single step
        step = scenario_steps[step_index]
        action = step.get('action', 'unknown')
        
        add_log('info', f'Executing step {step_index + 1}: {action}')
        
        try:
            # Execute the step
            automation_engine.execute_dsl([step], f'step_{step_index + 1}')
            add_log('success', f'Step {step_index + 1} completed: {action}')
            
            # Capture screenshot after execution
            time.sleep(0.5)
            capture_vnc_screenshot()
            
            return jsonify({
                'success': True,
                'step_index': step_index,
                'step': step
            })
        except Exception as e:
            add_log('error', f'Step {step_index + 1} failed: {str(e)}')
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Step execution failed: {str(e)}',
                'traceback': traceback.format_exc()
            }), 500
    
    except Exception as e:
        add_log('error', f'Unexpected error: {str(e)}')
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
            add_log('info', f'Starting scenario: {current_scenario}')
            
            # Initialize engine if not exists
            if not automation_engine:
                add_log('info', 'Initializing automation engine...')
                ollama_config = scenario_config.get('ollama', {})
                vision = OllamaVision(
                    base_url=ollama_config.get('url', 'http://ollama:11434'),
                    model=ollama_config.get('model', 'llava:7b')
                )
                automation_engine = AutomationEngine(live_controller, vision, enable_recording=False)
                add_log('success', 'Automation engine initialized')
            
            # Execute all steps
            for i, step in enumerate(scenario_steps):
                current_step = i
                action = step.get('action', 'unknown')
                add_log('info', f'Step {i + 1}/{len(scenario_steps)}: {action}')
                
                automation_engine.execute_dsl([step], f'step_{i + 1}')
                add_log('success', f'Step {i + 1} completed')
                
                # Capture screenshot after each step
                time.sleep(0.5)
                capture_vnc_screenshot()
            
            add_log('success', f'Scenario completed! {len(scenario_steps)} steps executed')
            
        except Exception as e:
            add_log('error', f'Scenario execution failed: {str(e)}')
            traceback.print_exc()
        
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
            display: grid;
            grid-template-columns: 400px 1fr 350px;
            height: 100vh;
        }
        
        .sidebar {
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
        
        /* Log Panel */
        .log-panel {
            background: #1e1e1e;
            border-left: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }
        
        .log-header {
            padding: 15px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .log-header h2 {
            font-size: 14px;
            color: #4fc3f7;
        }
        
        .log-header button {
            padding: 5px 10px;
            background: #3e3e42;
            color: #e0e0e0;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11px;
        }
        
        .log-header button:hover {
            background: #4e4e52;
        }
        
        .log-content {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            line-height: 1.5;
        }
        
        .log-entry {
            padding: 6px 10px;
            margin-bottom: 2px;
            border-left: 3px solid transparent;
            border-radius: 2px;
            display: flex;
            gap: 10px;
        }
        
        .log-entry .timestamp {
            color: #858585;
            min-width: 70px;
        }
        
        .log-entry .message {
            flex: 1;
            word-wrap: break-word;
        }
        
        .log-entry.info {
            border-left-color: #4fc3f7;
            background: #1a2832;
        }
        
        .log-entry.success {
            border-left-color: #4caf50;
            background: #1a2819;
            color: #81c784;
        }
        
        .log-entry.error {
            border-left-color: #f44336;
            background: #321a1a;
            color: #ef5350;
        }
        
        .log-entry.warning {
            border-left-color: #ff9800;
            background: #322a1a;
            color: #ffb74d;
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
        
        <div class="log-panel">
            <div class="log-header">
                <h2>📋 Execution Logs</h2>
                <div style="display: flex; gap: 5px;">
                    <button onclick="copyLogs()" title="Copy logs to clipboard">📋 Copy</button>
                    <button onclick="downloadLogs()" title="Download logs as file">💾 Save</button>
                    <button onclick="clearLogs()" title="Clear all logs">🗑️ Clear</button>
                </div>
            </div>
            <div class="log-content" id="logContent">
                <div class="log-entry info">
                    <span class="timestamp">--:--:--</span>
                    <span class="message">Waiting for connection...</span>
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
            // Use video feed instead of polling for better performance
            preview.innerHTML = '<img id="liveImage" src="/video_feed" alt="VNC Preview" style="width: 100%; height: auto;">';
        }
        
        function stopLivePreview() {
            const preview = document.getElementById('previewContent');
            if (preview) {
                preview.innerHTML = `
                    <div class="no-preview">
                        <h3>Disconnected</h3>
                        <p>Connect to VNC to see live preview</p>
                    </div>
                `;
            }
        }
        
        function updateScreenshot() {
            // No longer needed - using video feed instead
            console.log('[Monitor] Using video feed for live preview');
        }
        
        // Log Management
        let logPollInterval = null;
        
        function startLogPolling() {
            if (logPollInterval) return;
            
            updateLogs();  // Initial update
            logPollInterval = setInterval(updateLogs, 1000);  // Poll every second
        }
        
        function stopLogPolling() {
            if (logPollInterval) {
                clearInterval(logPollInterval);
                logPollInterval = null;
            }
        }
        
        function updateLogs() {
            fetch('/api/logs')
                .then(r => r.json())
                .then(data => {
                    if (data.success && data.logs) {
                        displayLogs(data.logs);
                    }
                })
                .catch(err => console.error('Log update error:', err));
        }
        
        function displayLogs(logs) {
            const container = document.getElementById('logContent');
            if (!logs || logs.length === 0) {
                container.innerHTML = `
                    <div class="log-entry info">
                        <span class="timestamp">--:--:--</span>
                        <span class="message">No logs yet...</span>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = logs.map(log => `
                <div class="log-entry ${log.level}">
                    <span class="timestamp">${log.timestamp}</span>
                    <span class="message">${escapeHtml(log.message)}</span>
                </div>
            `).join('');
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function clearLogs() {
            fetch('/api/logs/clear')
                .then(() => updateLogs())
                .catch(err => console.error('Clear logs error:', err));
        }
        
        function copyLogs() {
            fetch('/api/logs')
                .then(r => r.json())
                .then(data => {
                    if (data.success && data.logs) {
                        // Format logs as text
                        const logsText = data.logs.map(log => 
                            `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`
                        ).join('\n');
                        
                        // Copy to clipboard
                        navigator.clipboard.writeText(logsText)
                            .then(() => {
                                // Show feedback
                                const btn = event.target;
                                const originalText = btn.textContent;
                                btn.textContent = '✓ Copied!';
                                btn.style.background = '#4caf50';
                                
                                setTimeout(() => {
                                    btn.textContent = originalText;
                                    btn.style.background = '';
                                }, 2000);
                            })
                            .catch(err => {
                                console.error('Copy failed:', err);
                                alert('Failed to copy logs to clipboard');
                            });
                    }
                })
                .catch(err => console.error('Copy logs error:', err));
        }
        
        function downloadLogs() {
            // Open download endpoint in new window (will trigger download)
            window.open('/api/logs/download', '_blank');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Start log polling when page loads
        window.addEventListener('load', () => {
            startLogPolling();
        });
        
        // Stop log polling when page unloads
        window.addEventListener('beforeunload', () => {
            stopLogPolling();
        });
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
    add_log('info', 'Live Monitor started - Ready for connections')
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
