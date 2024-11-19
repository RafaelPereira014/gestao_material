
import pymysql
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)


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
        columns = [column[0] for column in cursor.description]  # Get column names
        equipamentos = []

        # Fetch all rows and convert them into dictionaries
        for row in cursor.fetchall():
            equipamento_dict = dict(zip(columns, row))  # Create a dictionary
            equipamentos.append(equipamento_dict)

        return equipamentos
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_equip_by_escola(escola_id):
    """Fetches equipment associated with a specific escola_id."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM equipamentos WHERE escola_id = %s", (escola_id,))
        columns = [column[0] for column in cursor.description]  # Get column names
        equipamentos = []

        # Fetch all rows and convert them into dictionaries
        for row in cursor.fetchall():
            equipamento_dict = dict(zip(columns, row))  # Create a dictionary from row
            equipamentos.append(equipamento_dict)

        return equipamentos
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
    