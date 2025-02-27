import pymysql
from config import DB_CONFIG

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)

def get_user_fields(user_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    # Define the query
    query = "SELECT id, username, email, escola_id, role, cc, password FROM users WHERE id = %s"
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
            "cc": user_data[5],
            "password": user_data[6],  # Include the password
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
    
def update_password(user_id, new_password_hash):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_password_hash, user_id)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error updating password: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

def update_password_with_email(email, new_password_hash):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (new_password_hash, email)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error updating password: {e}")
        raise
    finally:
        cursor.close()
        connection.close()