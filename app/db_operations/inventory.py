import mysql.connector
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def get_escolas():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM escolas")
        # Fetch all results
        escolas = cursor.fetchall()
        # Return list of school names
        return [escola[0] for escola in escolas]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_all_equip():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM equipamentos")
        equipamentos = cursor.fetchall()
        
        # Create a list of dictionaries
        equipment_list = [
            {
                "id": equipamento[0],
                "tipo": equipamento[1],
                "status": equipamento[2],
                "aluno_CC": equipamento[3],
                "escola_id": equipamento[4],
                "data_aquisicao": equipamento[5],
                "data_ultimo_movimento": equipamento[6],
                "cedido_a_escola": equipamento[7],
                "serial_number": equipamento[8]
            }
            for equipamento in equipamentos
        ]
        
        return equipment_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
    