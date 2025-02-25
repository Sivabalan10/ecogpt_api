from flask import Flask, request, jsonify, render_template
import threading
import requests
import time
import socket
from datetime import datetime, timedelta

app = Flask(__name__)

connected_systems = {}

def calculate_energy_credit_points(power_consumed):
    """Calculates Energy Credit points based on power consumption."""
    if power_consumed < 30:
        return 100
    elif 30 <= power_consumed < 40:
        return 85
    elif 40 <= power_consumed < 50:
        return 70
    elif 50 <= power_consumed < 60:
        return 55
    else:
        return 40

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_page')
def send_page():
    return render_template('send_page.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/receive', methods=['POST'])
def receive_data():
    """Receives data from the clients and updates their last seen time."""
    data = request.json
    device_id = data.get("device_id", "Unknown")
    data["last_seen"] = datetime.utcnow()

    connected_systems[device_id] = data
    print(f"Updated {device_id}: {data}")  # Debugging log

    return jsonify({"message": "Data received"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    global connected_systems
    """Returns the list of active systems, removing inactive ones."""
    now = datetime.utcnow()
    offline_threshold = now - timedelta(seconds=5)

    # Remove systems that haven't sent data for more than 5 seconds
    active_systems = {
        k: v for k, v in connected_systems.items() if v["last_seen"] > offline_threshold
    }

    # Update the global dictionary
    
    connected_systems = active_systems

    return jsonify({
        "connected_systems": len(connected_systems),
        "systems_data": active_systems
    })


def send_data():
    """Continuously sends data to the '/receive' endpoint every 2 seconds."""
    while True:
        try:
            device_id = socket.gethostname()
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            data = {
                "device_id": device_id,
                "total_power_consumed": round(time.time() % 100, 2),
                "total_screen_on_duration": str(timedelta(seconds=int(time.time() % 3600))),
                "timestamp": current_time
            }
            
            requests.post("http://192.168.16.28:5002/receive", json=data)
        except Exception as e:
            print("Error sending data:", e)
        
        time.sleep(3)

if __name__ == '__main__':
    threading.Thread(target=send_data, daemon=True).start()
    app.run(host='0.0.0.0', port=5002, debug=True)
