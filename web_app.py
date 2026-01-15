"""
Oracle Cloud VM.Standard.A1.Flex Auto-Register - Web Service Version

This Flask application runs the auto-register loop in a background thread
while exposing a web UI to monitor the status.

For use with Render.com's free Web Service tier.
"""

import os
import sys
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify

from config import Config
from oci_client import OCIClient
from telegram_notifier import TelegramNotifier


# ============================================================================
# Global State
# ============================================================================

app_state = {
    "status": "initializing",  # initializing, running, success, error
    "attempt": 0,
    "last_attempt_time": None,
    "last_result": None,
    "start_time": None,
    "instance_created": False,
    "instance_info": None,
    "error_message": None,
    "config_summary": None,
}


# ============================================================================
# HTML Template
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Oracle Cloud Auto-Register</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e4;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 30px 0;
        }
        
        .header h1 {
            font-size: 2rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #888;
            font-size: 0.9rem;
        }
        
        .status-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .status-dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-dot.running {
            background: #00d4ff;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }
        
        .status-dot.success {
            background: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            animation: none;
        }
        
        .status-dot.error {
            background: #ff4444;
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        }
        
        .status-dot.initializing {
            background: #ffaa00;
            box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(0.95); }
        }
        
        .status-text {
            font-size: 1.5rem;
            font-weight: 600;
            text-transform: capitalize;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.03);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .info-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .info-label {
            color: #888;
        }
        
        .info-value {
            color: #e4e4e4;
            font-family: 'Courier New', monospace;
        }
        
        .success-box {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .success-box h3 {
            color: #00ff88;
            margin-bottom: 15px;
        }
        
        .last-result {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #aaa;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            font-size: 0.8rem;
        }
        
        .auto-refresh {
            display: inline-block;
            padding: 5px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            font-size: 0.75rem;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Oracle Cloud Auto-Register</h1>
            <p>VM.Standard.A1.Flex Instance Monitor</p>
        </div>
        
        <div class="status-card">
            <div class="status-indicator">
                <div class="status-dot {{ status }}"></div>
                <span class="status-text">{{ status_text }}</span>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{{ attempt }}</div>
                    <div class="stat-label">Attempts</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ uptime }}</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ retry_interval }}s</div>
                    <div class="stat-label">Retry Interval</div>
                </div>
            </div>
            
            {% if instance_info %}
            <div class="success-box">
                <h3>🎉 Instance Created Successfully!</h3>
                <div class="info-row">
                    <span class="info-label">Instance ID</span>
                    <span class="info-value">{{ instance_info.id[:30] }}...</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Public IP</span>
                    <span class="info-value">{{ instance_info.public_ip }}</span>
                </div>
            </div>
            {% endif %}
            
            <div class="info-section">
                <div class="info-row">
                    <span class="info-label">Region</span>
                    <span class="info-value">{{ region }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Shape</span>
                    <span class="info-value">VM.Standard.A1.Flex</span>
                </div>
                <div class="info-row">
                    <span class="info-label">OCPUs / Memory</span>
                    <span class="info-value">{{ ocpus }} / {{ memory_gb }} GB</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Last Attempt</span>
                    <span class="info-value">{{ last_attempt }}</span>
                </div>
            </div>
            
            {% if last_result %}
            <div class="last-result">
                {{ last_result }}
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <span class="auto-refresh">🔄 Auto-refresh every 30 seconds</span>
        </div>
    </div>
</body>
</html>
"""


# ============================================================================
# Flask Application
# ============================================================================

app = Flask(__name__)


def get_uptime() -> str:
    """Calculate uptime since start."""
    if not app_state["start_time"]:
        return "0s"
    
    delta = datetime.now() - app_state["start_time"]
    total_seconds = int(delta.total_seconds())
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@app.route("/")
def index():
    """Main status page."""
    status_text_map = {
        "initializing": "Initializing...",
        "running": "Searching for capacity...",
        "success": "Instance Created!",
        "error": "Error occurred",
    }
    
    return render_template_string(
        HTML_TEMPLATE,
        status=app_state["status"],
        status_text=status_text_map.get(app_state["status"], app_state["status"]),
        attempt=app_state["attempt"],
        uptime=get_uptime(),
        retry_interval=app_state.get("retry_interval", 60),
        region=app_state.get("region", "N/A"),
        ocpus=app_state.get("ocpus", "N/A"),
        memory_gb=app_state.get("memory_gb", "N/A"),
        last_attempt=app_state["last_attempt_time"] or "Never",
        last_result=app_state["last_result"],
        instance_info=app_state["instance_info"],
    )


@app.route("/health")
def health():
    """Health check endpoint for Render."""
    return jsonify({
        "status": "healthy",
        "app_status": app_state["status"],
        "attempt": app_state["attempt"],
        "uptime_seconds": (datetime.now() - app_state["start_time"]).total_seconds() if app_state["start_time"] else 0,
    })


@app.route("/api/status")
def api_status():
    """API endpoint for current status."""
    return jsonify(app_state)


# ============================================================================
# Background Worker
# ============================================================================

def get_timestamp() -> str:
    """Get current timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def background_loop(config: Config, oci_client: OCIClient, notifier: TelegramNotifier):
    """Background loop that attempts to create the instance."""
    import traceback
    global app_state
    
    try:
        app_state["status"] = "running"
        app_state["start_time"] = datetime.now()
        app_state["retry_interval"] = config.retry_interval
        app_state["region"] = config.oci_region
        app_state["ocpus"] = config.ocpus
        app_state["memory_gb"] = config.memory_gb
        
        print(f"[{get_timestamp()}] 🚀 Background loop started", flush=True)
        print(f"   • Target: VM.Standard.A1.Flex in {config.oci_region}", flush=True)
        print(f"   • Retry interval: {config.retry_interval} seconds", flush=True)
        
        # Send startup notification (non-blocking)
        try:
            notifier.send_startup_message()
        except Exception as e:
            print(f"[{get_timestamp()}] ⚠️ Failed to send startup notification: {e}", flush=True)
        
        while True:
            app_state["attempt"] += 1
            app_state["last_attempt_time"] = get_timestamp()
            
            print(f"[{get_timestamp()}] Attempt #{app_state['attempt']} - Trying to create instance...", flush=True)
            
            try:
                result = oci_client.create_instance()
                
                if result["success"]:
                    # SUCCESS!
                    app_state["status"] = "success"
                    app_state["instance_created"] = True
                    app_state["instance_info"] = result["instance"]
                    app_state["last_result"] = f"✅ Instance created successfully!"
                    
                    print(f"\n🎉 SUCCESS! Instance created on attempt #{app_state['attempt']}", flush=True)
                    print(f"   Instance ID: {result['instance']['id']}", flush=True)
                    print(f"   Public IP: {result['instance']['public_ip']}", flush=True)
                    
                    # Send Telegram notification
                    try:
                        notifier.send_success_message(result["instance"])
                    except Exception as e:
                        print(f"[{get_timestamp()}] ⚠️ Failed to send success notification: {e}", flush=True)
                    
                    # Don't exit - keep web server running to show success
                    print("✅ Instance created! Web server will keep running to display status.", flush=True)
                    break
                
                elif result["is_capacity_error"]:
                    app_state["last_result"] = f"⏳ Out of capacity. Retrying in {config.retry_interval}s..."
                    print(f"[{get_timestamp()}] ⏳ Out of capacity. Retrying in {config.retry_interval}s...", flush=True)
                
                else:
                    app_state["last_result"] = f"❌ {result['message']}"
                    print(f"[{get_timestamp()}] ❌ Error: {result['message']}", flush=True)
            
            except Exception as e:
                app_state["last_result"] = f"❌ Exception: {str(e)}"
                print(f"[{get_timestamp()}] ❌ Exception in create_instance: {e}", flush=True)
                print(traceback.format_exc(), flush=True)
            
            time.sleep(config.retry_interval)
    
    except Exception as e:
        app_state["status"] = "error"
        app_state["error_message"] = f"Background loop crashed: {str(e)}"
        app_state["last_result"] = f"❌ FATAL: {str(e)}"
        print(f"[{get_timestamp()}] ❌ FATAL ERROR in background loop: {e}", flush=True)
        print(traceback.format_exc(), flush=True)


def start_background_worker():
    """Initialize and start the background worker thread."""
    import traceback
    global app_state
    
    try:
        print("Loading configuration...", flush=True)
        config = Config()
        
        # Validate configuration first
        if not config.validate():
            app_state["status"] = "error"
            app_state["error_message"] = "Configuration validation failed"
            print("❌ Configuration validation failed", flush=True)
            return
        
        print("✅ Configuration validated successfully", flush=True)
        
        # Initialize clients
        oci_client = OCIClient(config)
        notifier = TelegramNotifier(config)
        
        # Validate OCI credentials
        print("Validating OCI credentials...", flush=True)
        if not oci_client.validate_credentials():
            app_state["status"] = "error"
            app_state["error_message"] = "OCI credential validation failed"
            print("❌ OCI credential validation failed", flush=True)
            return
        
        print("✅ OCI credentials validated successfully", flush=True)
        
        # Set initial state with config values
        app_state["retry_interval"] = config.retry_interval
        app_state["region"] = config.oci_region
        app_state["ocpus"] = config.ocpus
        app_state["memory_gb"] = config.memory_gb
        
        # Start background thread
        thread = threading.Thread(
            target=background_loop,
            args=(config, oci_client, notifier),
            daemon=True
        )
        thread.start()
        print("✅ Background worker thread started", flush=True)
        
    except ValueError as e:
        app_state["status"] = "error"
        app_state["error_message"] = f"Configuration error: {str(e)}"
        print(f"❌ Configuration error: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
    
    except Exception as e:
        app_state["status"] = "error"
        app_state["error_message"] = f"Startup error: {str(e)}"
        print(f"❌ Startup error: {e}", flush=True)
        print(traceback.format_exc(), flush=True)


# ============================================================================
# Entry Point
# ============================================================================

# Start background worker when app loads
start_background_worker()

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🌐 Starting web server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
