from datetime import datetime
import pymysql
from config import DB_CONFIG

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)


def get_marcas():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM marcas ORDER BY nome ASC")
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
        
def get_modelos():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM modelos ORDER BY nome ASC")
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
        
def get_processadores():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM processadores ORDER BY nome ASC")
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
        
def get_rams():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM rams ORDER BY nome ASC")
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
        
def get_discos():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM discos ORDER BY nome ASC")
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
        
def get_tipo_monitores():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM tipo_monitor ORDER BY nome ASC")
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

def get_polegadas():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM polegadas ORDER BY nome ASC")
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
        
def get_tipo_voips():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM tipo_voip ORDER BY nome ASC")
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
        
def get_sistemas_operativos():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM sistema_operativo ORDER BY nome ASC")
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
        
def get_offices():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM office ORDER BY nome ASC")
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
        
def get_firmas():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM firma ORDER BY nome ASC")
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
        
def get_garantias():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM garantia ORDER BY nome ASC")
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
        
def get_tipos_camera():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM tipo_camera ORDER BY nome ASC")
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
        
def get_tipos_headset():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM tipo_headset ORDER BY nome ASC")
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
        
def get_atribuidos_a():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM users_a_atribuir ORDER BY nome ASC")
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

def get_diversos():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM diversos ORDER BY nome ASC")
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

def get_dominios():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Execute the query to fetch school names
        cursor.execute("SELECT nome FROM dominios ORDER BY nome ASC")
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