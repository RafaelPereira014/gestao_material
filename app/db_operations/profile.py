import pymysql
from config import DB_CONFIG

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)

def get_user_fields(user_id):
    
    conn = connect_to_database()
    cursor = conn.cursor()

    # Define the query
    query = "SELECT id, username, email, escola_id, role,cc FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))

    # Fetch the user data
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    # If user data was found, return it as a dictionary
    if user_data:
        user_fields = {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "escola_id": user_data[3],
            "role": user_data[4],
            "cc": user_data[5]
            
        }
        return user_fields

    # Return None if the user was not found
    return None

def is_admin(user_id):
    """Checks if the user is an Admin"""
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    user_type = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_type and user_type[0] == 'admin':  # Check if user_type is not None and compare the first element of the tuple
        return True
    else:
        return False