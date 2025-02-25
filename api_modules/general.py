from flask import Flask, request, jsonify, render_template, flash,get_flashed_messages
import requests
from db_functions import *  
import random
import urllib.parse  
import sqlite3
import json
from bs4 import BeautifulSoup 
app = Flask(__name__)
app.secret_key = "secret_key123"

# Documentation
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/admin_portal", methods=["GET"])
def admin():
    return render_template("admin_portal.html")

@app.route("/user_management")
def user_management():
    return render_template("user_management.html")

@app.route("/records")
def records():
    return render_template("records.html")

@app.route("/power_units")
def power_units():
    return render_template("power_units.html")


# map --------
REC_BOUNDARIES = {
    "min_lat": 13.0328, "max_lat": 13.0350,
    "min_lon": 80.0415, "max_lon": 80.0450
}

# Generate random IoT devices
def generate_iot_devices(count=10):
    devices = []
    for i in range(count):
        lat = random.uniform(REC_BOUNDARIES["min_lat"], REC_BOUNDARIES["max_lat"])
        lon = random.uniform(REC_BOUNDARIES["min_lon"], REC_BOUNDARIES["max_lon"])
        status = random.choice(["active", "inactive"])
        devices.append({"id": f"Device_{i+1}", "lat": lat, "lon": lon, "status": status})
    return devices

@app.route("/map")
def index():
    return render_template("map.html")

@app.route("/get_devices")
def get_devices():
    return jsonify(generate_iot_devices())


# ------------------- CLIENT API ------------------- #

# 1. User Login
@app.route("/user_login", methods=["POST"])
def user_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = execute_query("SELECT * FROM user_management WHERE username = ? AND password = ?", (username, password), fetch=True, fetchone=True)
    
    if user:
        return jsonify({"status": "success", "message": "Login successful", "user_data": user})
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

# 2. User Logout
@app.route("/user_log_out", methods=["POST"])
def user_log_out():
    return jsonify({"status": "success", "message": "User logged out successfully"})

# 3. Get all user table data
@app.route("/get_all_user_table_data/<int:user_id>", methods=["GET"])
def get_all_user_table_data(user_id):
    user = execute_query("SELECT * FROM user_management WHERE user_id = ?", (user_id,), fetch=True, fetchone=True)
    if user:
        return jsonify({"status": "success", "user_data": user})
    return jsonify({"status": "error", "message": "User not found"}), 404

# 4. Check-in validation and update

# -----------------------------------------------------------------------------------------------------------------------------------
# 5. Check-out validation and update
def get_db_connection():
    conn = sqlite3.connect("energy_saving.db")
    conn.row_factory = sqlite3.Row
    return conn

# Function to update user data
def update_user(user_id, check_in_status=None, check_in_area=None, check_out_status=None, cc_points=0):
    conn = get_db_connection()
    cursor = conn.cursor()

    if check_in_status:
        cursor.execute("""
            UPDATE user_management 
            SET check_in_status=?, check_in_area=?, source='mobile' 
            WHERE user_id=?
        """, (check_in_status, check_in_area, user_id))

    if check_out_status:
        cursor.execute("""
            UPDATE user_management 
            SET check_out_status=?, cc_point = cc_point + ? 
            WHERE user_id=?
        """, (check_out_status, cc_points, user_id))

    conn.commit()
    conn.close()


@app.route("/check_in_out", methods=["POST"])
def check_in_out():
    try:
        data = request.json
        qr_url = data.get("qr_url")  # URL from QR
        user_id = data.get("user_id")
        user_lat, user_lon = data.get("lat"), data.get("lon")
        print(qr_url, user_id, user_lat, user_lon)
        if not (qr_url and user_id and user_lat is not None and user_lon is not None):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Decode and extract QR data
        response = requests.get(qr_url, allow_redirects=True)
        
        if response.status_code != 200:
            print("Error: Failed to fetch QR data.")
            return None, None, None, None

        decoded_qr = response.text.strip()  # Get the actual content

        # Step 2: Parse HTML and extract the QR data inside <p> tag
        soup = BeautifulSoup(decoded_qr, "html.parser")
        p_tag = soup.find("p")  # Find the <p> tag containing JSON data

        if not p_tag:
            print("Error: No QR data found in HTML.")
            return None, None, None, None

        qr_json_str = p_tag.text.strip()

        # Step 3: Convert JSON-like string to a proper JSON object
        qr_json_str = qr_json_str.replace("&#34;", "\"")  # Fix HTML-escaped quotes
        qr_data = json.loads(qr_json_str)

        # Step 4: Extract values safely
        qr_lat = float(qr_data.get("lat", 0))
        qr_lon = float(qr_data.get("lon", 0))
        location_id = int(qr_data.get("location_id", 0))
        status = qr_data.get("status", "").strip().lower()

        print(qr_data,qr_lat, qr_lon, location_id, status)
        flash(f"User {status} with the ID {user_id} has {status} at location {location_id}")

        # Validate location
        if (user_lat, user_lon) != (qr_lat, qr_lon):
            return jsonify({"status": "error", "message": "Invalid location"}), 400

        # Check-in or Check-out process
        if status == "in":
            update_user(user_id, check_in_status="checked_in", check_in_area=f"Lat:{user_lat}, Lon:{user_lon}")
            return jsonify({"status": "success", "message": "Check-in successful"})

        elif status == "out":
            update_user(user_id, check_out_status="checked_out", cc_points=10)  # Adding CC points
            return jsonify({"status": "success", "message": "Check-out successful, CC points added"})

        else:
            return jsonify({"status": "error", "message": "Invalid status in QR data"}), 400

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid QR code data"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/get_flash_messages")
def get_flash_messages():
    messages = get_flashed_messages()
    return jsonify({"message": messages[0] if messages else ""})
#------------------------------------------------------------------------------------------------------------------------------------------

# 6. View Reports
@app.route("/view_reports/<int:user_id>", methods=["GET"])
def view_reports(user_id):
    records = execute_query("SELECT * FROM records WHERE user_id = ?", (user_id,), fetch=True)
    return jsonify({"status": "success", "records": records})

# 7. Make Transaction (Reduce CC points and update records)
@app.route("/make_transaction", methods=["POST"])
def make_transaction():
    data = request.json
    user_id = data.get("user_id")
    product_name = data.get("product_name")

    conn = sqlite3.connect('energy_saving.db')  # Get DB connection
    cursor = conn.cursor()

    try:
        # Fetch user CC points
        cursor.execute("SELECT cc_point FROM user_management WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        # Fetch product details
        cursor.execute("SELECT id, cc_cost, quantity_available FROM products_list WHERE product_name = ?", (product_name,))
        product = cursor.fetchone()

        if user and product:
            user_cc = user[0]
            product_id, product_cost, quantity = product

            if user_cc >= product_cost and quantity > 0:
                # Deduct CC points
                cursor.execute("UPDATE user_management SET cc_point = cc_point - ? WHERE user_id = ?", (product_cost, user_id))

                # Reduce product quantity
                cursor.execute("UPDATE products_list SET quantity_available = quantity_available - 1 WHERE id = ?", (product_id,))

                # Insert transaction into records
                cursor.execute("INSERT INTO records (user_id, product_claimed, cc_point_on_transaction) VALUES (?, ?, ?)",
                               (user_id, product_name, product_cost))

                conn.commit()  # Commit all changes
                return jsonify({"status": "success", "message": "Transaction successful"})

            return jsonify({"status": "error", "message": "Insufficient CC points or product out of stock"}), 400

        return jsonify({"status": "error", "message": "User or product not found"}), 404

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# 8. Power unit saved calculation
@app.route("/power_unit_saved", methods=["GET"])
def power_unit_saved():
    result = execute_query("SELECT SUM(unit_saved) FROM power_unit", fetch=True, fetchone=True)
    return jsonify({"status": "success", "total_power_saved": result[0] if result else 0})


# ------------------- ADMIN MANAGEMENT ------------------- #

# 9. View user management
@app.route("/view_user_management", methods=["GET"])
def view_user_management():
    users = execute_query("SELECT user_id, username FROM user_management", fetch=True)
    
    # Convert the tuples into dictionaries
    user_list = [{"user_id": user[0], "username": user[1]} for user in users]
    
    return jsonify({"status": "success", "users": user_list})


# 10. CRUD User Management
@app.route("/crud_user_management", methods=["POST"])
def crud_user_management():
    data = request.json
    action = data.get("action")
    user_id = data.get("user_id")
    username = data.get("username")
    password = data.get("password")
    
    if action == "create":
        insert_user(username=username, password=password, cc_point=0, demerits=0, no_of_products_claimed=0, check_in_status=None, check_in_area=None, check_out_status=None, source=None)
    elif action == "update":
        update_user(user_id, username=username, password=password)
    elif action == "delete":
        delete_user(user_id)
    return jsonify({"status": "success", "message": f"User {action}d successfully"})

# 11. Show records
@app.route("/show_records", methods=["GET"])
def show_records():
    records = execute_query("SELECT * FROM records", fetch=True)
    
    # Convert records into a list of dictionaries
    formatted_records = [
        {
            "user_id": record[1],  
            "product_claimed": record[2],  
            "cc_point_on_transaction": record[3]
        }
        for record in records
    ]
    
    return jsonify({"status": "success", "records": formatted_records})

# 12. Show map page
@app.route("/show_map", methods=["GET"])
def show_map():
    return render_template("map.html")

# 13. Show power unit table
@app.route("/show_power_unit_table", methods=["GET"])
def show_power_unit_table():
    power_units = execute_query("SELECT * FROM power_unit", fetch=True)

    # Convert tuples into dictionaries
    formatted_power_units = [
        {
            "id": unit[0],  
            "unit_saved": unit[1],  
            "no_of_logged": unit[2],  
            "status": unit[3],  
            "no_of_false_count": unit[4],  
            "current_in_count": unit[5],  
            "current_out_count": unit[6]
        }
        for unit in power_units
    ]

    return jsonify({"status": "success", "power_units": formatted_power_units})


# 14. Alert message system
@app.route("/alert_msg", methods=["POST"])
def alert_msg():
    data = request.json
    message = data.get("message")
    return jsonify({"status": "success", "alert": message})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=3838)
