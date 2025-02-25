from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import threading
import time

app = Flask(__name__)
CORS(app)
device_status = {"status": "inactive"}  # Default to inactive

def check_device_status():
    global device_status
    while True:
        try:
            response = requests.get("http://192.0.0.2:5001/device_status", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "active":
                    device_status["status"] = "active"
                else:
                    device_status["status"] = "inactive"
            else:
                device_status["status"] = "inactive"
        except requests.exceptions.RequestException:
            device_status["status"] = "inactive"

        time.sleep(2)  # Check every 2 seconds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_devices')
def get_devices():
    return jsonify([
        {"id": "Device 1", "lat": 13.0339, "lon": 80.0432, "status": device_status["status"]}
    ])

if __name__ == '__main__':
    # Start background thread to check device status
    thread = threading.Thread(target=check_device_status, daemon=True)
    thread.start()
    
    app.run(host='0.0.0.0', port=3535, debug=True)
