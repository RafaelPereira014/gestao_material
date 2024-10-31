from collections import namedtuple
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
        columns = [column[0] for column in cursor.description]  # Get column names
        Equipamento = namedtuple('Equipamento', columns)  # Create a namedtuple class
        
        # Use a list comprehension to convert rows to named tuples
        equipamentos = [Equipamento(*row) for row in cursor.fetchall()]
        
        return equipamentos
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
    