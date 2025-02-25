import sqlite3

def create_database():
    conn = sqlite3.connect("energy_saving.db")  
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS power_unit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_saved REAL,
            no_of_logged INTEGER,
            status TEXT,
            no_of_false_count INTEGER,
            current_in_count INTEGER,
            current_out_count INTEGER
        )
    ''')

    # user_management table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_management (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            cc_point INTEGER,
            demerits INTEGER,
            no_of_products_claimed INTEGER,
            check_in_status TEXT,
            check_in_area TEXT,
            check_out_status TEXT,
            source TEXT
        )
    ''')

    # records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_claimed TEXT,
            cc_point_on_transaction INTEGER,
            FOREIGN KEY (user_id) REFERENCES user_management(user_id)
        )
    ''')

    # products_list table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            actual_cost REAL,
            cc_cost INTEGER,
            quantity_available INTEGER
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and tables created successfully!")