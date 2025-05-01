import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

# --- Database Configuration ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "booklens"
DB_CHARSET = "utf8"

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_CHARSET,
            database=DB_NAME
        )
        return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
        return None

def get_user_details(username):
    """Fetches user details from the database by username."""
    connection = get_db_connection()
    if not connection:
        return None

    user = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user_detail WHERE username=%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to fetch user details: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return user
