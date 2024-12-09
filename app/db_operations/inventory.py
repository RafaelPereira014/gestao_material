
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

def get_schools_same_island(escola_id):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try:
        # Fetch the ilha_id of the given escola_id
        cursor.execute("""
            SELECT ilha_id 
            FROM ilha_escola 
            WHERE escola_id = %s
        """, (escola_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"No ilha found for escola_id {escola_id}")
            return []
        
        ilha_id = result[0]
        
        # Fetch all schools in the same ilha
        cursor.execute("""
            SELECT e.id, e.nome 
            FROM escolas e
            JOIN ilha_escola ie ON e.id = ie.escola_id
            WHERE ie.ilha_id = %s
        """, (ilha_id,))
        
        schools = cursor.fetchall()
        
        # Return list of school names
        return [school[1] for school in schools]
    
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
        cursor.execute("SELECT * FROM equipamentos ORDER BY data_aquisicao DESC")
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
        cursor.execute("SELECT * FROM equipamentos WHERE escola_id = %s ORDER BY data_aquisicao DESC", (escola_id,))
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
    
def get_documents_by_equipment_and_school(equip_id, escola_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        # Query documents for the specified equipment and school
        cursor.execute("""
            SELECT nome_arquivo, caminho_arquivo, data_upload
            FROM documentos
            WHERE equipamento_id = %s AND escola_id = %s
            ORDER BY data_upload DESC
        """, (equip_id, escola_id))
        
        # Fetch the results and convert each row into a dictionary
        documents = cursor.fetchall()
        document_list = []
        for doc in documents:
            document_list.append({
                'nome_arquivo': doc[0],
                'caminho_arquivo': doc[1],
                'data_upload': doc[2]
            })
        return document_list
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []
    finally:
        cursor.close()
        connection.close()