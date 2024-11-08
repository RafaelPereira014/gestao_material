from datetime import datetime
import pymysql
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)



def get_equipment_by_serial(serial_number, id_escola):
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # Use DictCursor
    
    try:
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s AND escola_id = %s", (serial_number, id_escola))
        result = cursor.fetchone()  # This will return a dictionary, not a tuple
        
        return result  # Return equipment as a dictionary
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_equipment_acessories(equip_id):
    connection = connect_to_database()
    cursor = connection.cursor()  # You can use the default cursor here
    
    try:
        cursor.execute("SELECT tipo_acessorio FROM acessorios WHERE equipamento_id = %s", (equip_id,))
        rows = cursor.fetchall()  # This will return a list of tuples
        
        if rows:
            # Extract the first element from each tuple to get a flat list
            accessories = [row[0] for row in rows]
            return accessories  # Return the flat list of accessory names
        else:
            return []  # Return an empty list if no accessories are found
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def update_equipment(serial_number,escola_id, tipo=None, status=None, aluno_CC=None, data_ultimo_movimento=None, cedido_a_escola=None):
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        serial_number = serial_number.strip()  # Remove any leading/trailing spaces

        # Check if the equipment exists
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s and escola_id=%s ", (serial_number,escola_id,))
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
        
def is_serial_number_exists(serial_number, escola_id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM equipamentos WHERE serial_number = %s AND escola_id = %s
    """, (serial_number, escola_id))
    
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    return result[0] > 0  # Returns True if the serial number exists, else False