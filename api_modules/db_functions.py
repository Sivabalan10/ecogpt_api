import sqlite3

DB_NAME = "energy_saving.db"

# Create tables
def execute_query(query, params=(), fetch=False, fetchone=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetch:
        result = cursor.fetchone() if fetchone else cursor.fetchall()
    else:
        conn.commit()
    conn.close()
    return result


# CRUD Operations for power_unit
def insert_power_unit(**kwargs):
    columns = ', '.join(kwargs.keys())
    placeholders = ', '.join(['?'] * len(kwargs))
    values = tuple(kwargs.values())
    query = f"INSERT INTO power_unit ({columns}) VALUES ({placeholders})"
    execute_query(query, values)

def update_power_unit(record_id, **kwargs):
    updates = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = tuple(kwargs.values()) + (record_id,)
    query = f"UPDATE power_unit SET {updates} WHERE id = ?"
    execute_query(query, values)

def delete_power_unit(record_id):
    query = "DELETE FROM power_unit WHERE id = ?"
    execute_query(query, (record_id,))

def get_power_units():
    query = "SELECT * FROM power_unit"
    return execute_query(query, fetch=True)

# CRUD Operations for user_management
def insert_user(**kwargs):
    columns = ', '.join(kwargs.keys())
    placeholders = ', '.join(['?'] * len(kwargs))
    values = tuple(kwargs.values())
    query = f"INSERT INTO user_management ({columns}) VALUES ({placeholders})"
    execute_query(query, values)

def update_user(user_id, **kwargs):
    updates = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = tuple(kwargs.values()) + (user_id,)
    query = f"UPDATE user_management SET {updates} WHERE user_id = ?"
    execute_query(query, values)

def delete_user(user_id):
    query = "DELETE FROM user_management WHERE user_id = ?"
    execute_query(query, (user_id,))

def get_users():
    query = "SELECT * FROM user_management"
    return execute_query(query, fetch=True)

# Insert operation for records table (no update or delete)
def insert_record(user_id, product_claimed, cc_point_on_transaction):
    query = '''
        INSERT INTO records (user_id, product_claimed, cc_point_on_transaction)
        VALUES (?, ?, ?)
    '''
    execute_query(query, (user_id, product_claimed, cc_point_on_transaction))

# CRUD Operations for products_list
def insert_product(**kwargs):
    columns = ', '.join(kwargs.keys())
    placeholders = ', '.join(['?'] * len(kwargs))
    values = tuple(kwargs.values())
    query = f"INSERT INTO products_list ({columns}) VALUES ({placeholders})"
    execute_query(query, values)

def update_product(product_id, **kwargs):
    updates = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = tuple(kwargs.values()) + (product_id,)
    query = f"UPDATE products_list SET {updates} WHERE id = ?"
    execute_query(query, values)

def delete_product(product_id):
    query = "DELETE FROM products_list WHERE id = ?"
    execute_query(query, (product_id,))

def get_products():
    query = "SELECT * FROM products_list"
    return execute_query(query, fetch=True)

def make_transaction(user_id,product_name,cc_points):
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
                return print({"status": "success", "message": "Transaction successful"})

            return print({"status": "error", "message": "Insufficient CC points or product out of stock"}), 400

        return print({"status": "error", "message": "User or product not found"}), 404

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return print({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

def demo():
    print("Creating demo entries...")

    # Insert a power unit record
    insert_power_unit(unit_saved=10.5, no_of_logged=2, status="active", no_of_false_count=0, current_in_count=5, current_out_count=3)
    
    # Fetch and print power units
    power_units = get_power_units()
    print("Power Units:", power_units)

    # Update a power unit
    if power_units:
        update_power_unit(power_units[0][0], unit_saved=20.0)
        print("Updated Power Unit:", get_power_units())

    # Insert a user
    insert_user(username="john_doe", password="secure123", cc_point=50, demerits=0, no_of_products_claimed=1, check_in_status="checked_in", check_in_area="Zone A", check_out_status="not_checked_out", source="mobile")
    
    # Fetch and print users
    users = get_users()
    print("Users:", users)

    # Update a user
    if users:
        update_user(users[0][0], cc_point=100)
        print("Updated User:", get_users())

    # Insert a product
    insert_product(product_name="Energy Saver", actual_cost=200.0, cc_cost=30, quantity_available=10)
    
    # Fetch and print products
    products = get_products()
    print("Products:", products)

    # Update a product
    if products:
        update_product(products[0][0], quantity_available=15)
        print("Updated Product:", get_products())

    # Perform a transaction
    if users and products:
        make_transaction(users[0][0], "Energy Saver", 30)

    # Delete entries
    if power_units:
        delete_power_unit(power_units[0][0])
    if users:
        delete_user(users[0][0])
    if products:
        delete_product(products[0][0])

    print("All operations completed!")

if __name__ == "__main__":
    demo()