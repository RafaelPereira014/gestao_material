from datetime import datetime
import pymysql
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)



def get_equipment_by_serial(serial_number,escola_id):
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # Enable dictionary cursor
    
    try:
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s and escola_id=%s", (serial_number,escola_id,))
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
        
def update_equipment(serial_number, escola_id, tipo=None, status=None, aluno_CC=None, data_ultimo_movimento=None, cedido_a_escola=None):
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
       
        # Check if the equipment exists
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s AND escola_id = %s", (serial_number, escola_id))
        existing_equipment = cursor.fetchone()
        if not existing_equipment:
            print(f"No equipment found with serial_number: {serial_number} and escola_id: {escola_id}")
            return False

        # Fetch current values for comparison
        cursor.execute("SELECT tipo, status, aluno_CC, data_ultimo_movimento, cedido_a_escola FROM equipamentos WHERE serial_number = %s AND escola_id = %s", (serial_number, escola_id))
        existing_values = cursor.fetchone()

        # Debugging: print existing values and new values
        print(f"Existing values: {existing_values}")
        print(f"New values: {tipo}, {status}, {aluno_CC}, {data_ultimo_movimento}, {cedido_a_escola}")

        # Check if any fields have changed
        if existing_values == (tipo, status, aluno_CC, data_ultimo_movimento, cedido_a_escola):
            print("No changes detected. Skipping update.")
            return True

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
        if cedido_a_escola is None:
            sql += "cedido_a_escola = NULL, "
        else:
            sql += "cedido_a_escola = %s, "
            params.append(cedido_a_escola)

        # Remove trailing comma and finalize SQL with WHERE clause
        sql = sql.rstrip(", ") + " WHERE serial_number = %s AND escola_id = %s"
        params.extend([serial_number, escola_id])

        # Debugging: print the final SQL query and params
        print(f"Executing SQL: {sql} with params: {params}")

        # Execute the SQL statement
        cursor.execute(sql, tuple(params))
        connection.commit()

        # Check how many rows were affected
        if cursor.rowcount == 0:
            print("No rows were updated. Check if the serial_number and escola_id exist.")
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

def get_equip_id_by_serial(serial_number, escola_id):
    connection = connect_to_database()  # Replace with your actual database connection function
    cursor = connection.cursor()

    try:
        # Debugging: Print the input values and check for any invisible characters
        serial_number = serial_number.strip()
        escola_id = str(escola_id).strip()  # Ensure escola_id is a string
        
        print(f"Fetching equipment for SerialNo: {serial_number}, Escola ID: {escola_id}")
        
        # Execute the query to fetch the equipment ID based on serial number and school ID
        query = "SELECT * FROM equipamentos WHERE serial_number = %s AND escola_id = %s"
        print(f"Executing query: {query} with parameters: {serial_number}, {escola_id}")
        cursor.execute(query, (serial_number, escola_id))
        result = cursor.fetchone()
        
        # Check if a result was found and return the equipment ID
        if result:
            return result[0]  # Return the first column which is the ID
        else:
            print(f"No equipment found for SerialNo: {serial_number} and Escola ID: {escola_id}")
            return None  # Return None if no match is found
    except Exception as e:
        print(f"An error occurred while fetching equipment ID: {e}, SerialNo: {serial_number}, Escola ID: {escola_id}")
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
        
def get_school_ilha_id(school_id):
    connection = connect_to_database()  # Replace with your actual database connection function
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch the school ID based on the name
        cursor.execute("SELECT ilha_id FROM ilha_escola WHERE escola_id = %s", (school_id,))
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

def is_cedido(serial_number,escola_id):
    
    # Assuming you have a database connection setup
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Query to check if cedido_a exists for the given serial number
        query = """
        SELECT cedido_a_escola
        FROM equipamentos
        WHERE serial_number = %s and escola_id=%s
        LIMIT 1;
        """
        cursor.execute(query, (serial_number,escola_id,))
        result = cursor.fetchone()

        # If result is not None and cedido_a is not NULL, return True
        return result is not None and result[0] is not None
    finally:
        cursor.close()
        conn.close()
        
def get_equipment_acessories(equipamento_id):
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # Enable dictionary cursor
    
    try:
        cursor.execute("SELECT tipo_acessorio FROM acessorios WHERE equipamento_id=%s", (equipamento_id,))
        rows = cursor.fetchall()  # Fetch all rows

        if rows:
            return [row['tipo_acessorio'] for row in rows]  # Return a list of 'tipo_acessorio'
        else:
            return []  # Return an empty list if no accessories are found
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
    
def store_document(user_id, equipamento_id, escola_id, nome_arquivo, caminho_arquivo):
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        # Insert the document metadata into the documentos table
        cursor.execute("""
            INSERT INTO documentos (user_id, equipamento_id, escola_id, nome_arquivo, caminho_arquivo, data_upload)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, equipamento_id, escola_id, nome_arquivo, caminho_arquivo))
        connection.commit()
    except Exception as e:
        print(f"Error storing document: {e}")
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()