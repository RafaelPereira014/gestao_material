from datetime import datetime
import mysql.connector
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

def get_equipment_by_serial(serial_number):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM equipamentos WHERE serial_number = %s", (serial_number,))
        row = cursor.fetchone()
        if row:
            # Assuming row is structured as (id, tipo, status, aluno_CC, escola_id, data_aquisicao, data_ultimo_movimento, cedido_a_escola, serial_number)
            keys = ['id', 'tipo', 'status', 'aluno_CC', 'escola_id', 'data_aquisicao', 'data_ultimo_movimento', 'cedido_a_escola', 'serial_number']
            equipment_data = dict(zip(keys, row))
            return equipment_data
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
        
def update_equipment(serial_number, tipo=None, status=None, aluno_cc=None, data_ultimo_movimento=None, cedido_a_escola=None):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Construct the SQL statement dynamically
        sql = "UPDATE equipamentos SET "
        params = []
        
        if tipo is not None:
            sql += "tipo = %s, "
            params.append(tipo)
        
        if status is not None:
            sql += "status = %s, "
            params.append(status)
        
        if aluno_cc is not None:
            sql += "aluno_CC = %s, "
            params.append(aluno_cc)
        
        if data_ultimo_movimento is None:
            data_ultimo_movimento = datetime.now()
        sql += "data_ultimo_movimento = %s, "
        params.append(data_ultimo_movimento)
        
        if cedido_a_escola is not None:
            sql += "cedido_a_escola = %s, "
            params.append(cedido_a_escola)
        
        # Finalize SQL with WHERE clause and clean up trailing comma
        sql = sql.rstrip(", ") + " WHERE serial_number = %s"
        params.append(serial_number)

        # Print SQL statement and parameters for debugging
        print("Executing SQL:", sql)
        print("With parameters:", params)

        # Execute and commit changes
        cursor.execute(sql, tuple(params))
        connection.commit()

        # Check the affected rows
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