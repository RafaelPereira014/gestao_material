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