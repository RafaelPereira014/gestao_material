from datetime import datetime
import mysql.connector
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

from collections import namedtuple

def get_equipment_by_serial(serial_number):
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)  # Enable dictionary cursor
    
    try:
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s", (serial_number,))
        row = cursor.fetchone()
        
        if row:
            return row  # Directly return the row as a dictionary
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
        
def update_equipment(serial_number, tipo=None, status=None, aluno_CC=None, data_ultimo_movimento=None, cedido_a_escola=None):
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        serial_number = serial_number.strip()  # Remove any leading/trailing spaces

        # Check if the equipment exists
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s", (serial_number,))
        existing_equipment = cursor.fetchone()
        if not existing_equipment:
            print(f"No equipment found with serial_number: {serial_number}")
            return False

        # Start constructing the SQL statement
        sql = "UPDATE equipamentos SET "
        params = []

        # Append fields to update dynamically
        if tipo is not None:
            sql += "tipo = %s, "
            params.append(tipo)

        if status is not None:
            sql += "status = %s, "
            params.append(status)

        sql += "aluno_CC = %s, "
        params.append(aluno_CC)

        # If no value is provided for data_ultimo_movimento, set to now
        if data_ultimo_movimento is None:
            data_ultimo_movimento = datetime.now()
        sql += "data_ultimo_movimento = %s, "
        params.append(data_ultimo_movimento)

        # Handle cedido_a_escola, allowing it to be None
        sql += "cedido_a_escola = %s, "
        params.append(cedido_a_escola)

        # Remove trailing comma and finalize SQL with WHERE clause
        sql = sql.rstrip(", ") + " WHERE serial_number = %s"
        params.append(serial_number)

        # Debugging output
        print("Executing SQL:", sql)
        print("With parameters:", params)

        # Execute the SQL statement
        cursor.execute(sql, tuple(params))
        connection.commit()

        # Check how many rows were affected
        if cursor.rowcount == 0:
            print("No rows were updated. Check if the serial_number exists.")
            return False

        print("Equipment updated successfully.")
        return True

    except Exception as e:
        print(f"An error occurred while updating the equipment: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
        
def get_school_id_by_name(school_name):
    connection = connect_to_database()  # Replace with your actual database connection function
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch the school ID based on the name
        cursor.execute("SELECT id FROM escolas WHERE nome = %s", (school_name,))
        result = cursor.fetchone()
        
        # Check if a result was found and return the school ID
        if result:
            return result[0]  # Return the first column which is the ID
        else:
            return None  # Return None if no match is found
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
        
def get_school_name_by_id(school_id):
    connection = connect_to_database()  # Replace with your actual database connection function
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch the school ID based on the name
        cursor.execute("SELECT nome  FROM escolas WHERE id = %s", (school_id,))
        result = cursor.fetchone()
        
        # Check if a result was found and return the school ID
        if result:
            return result[0]  # Return the first column which is the ID
        else:
            return None  # Return None if no match is found
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()