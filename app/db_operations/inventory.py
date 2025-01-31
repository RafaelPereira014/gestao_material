
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
        
def get_all_requisicoes():
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM requisicoes WHERE estado='Pendente' ORDER BY data_criacao DESC")
        columns = [column[0] for column in cursor.description]  # Get column names
        requisicoes = []

        # Fetch all rows and convert them into dictionaries
        for row in cursor.fetchall():
            requisicao_dict = dict(zip(columns, row))  # Create a dictionary
            requisicoes.append(requisicao_dict)

        return requisicoes
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_all_requisicoes_ativas():
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM requisicoes WHERE estado='ativa' ORDER BY data_criacao DESC")
        columns = [column[0] for column in cursor.description]  # Get column names
        requisicoes = []

        # Fetch all rows and convert them into dictionaries
        for row in cursor.fetchall():
            requisicao_dict = dict(zip(columns, row))  # Create a dictionary
            requisicoes.append(requisicao_dict)

        return requisicoes
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_cameras():
    connection = connect_to_database() 
    cursor = connection.cursor()
    cursor.execute("SELECT id,marca_modelo,cod_nit FROM cameras WHERE estado = 'Disponivel' ")
    result = cursor.fetchall()
    cameras = [{'id': row[0],'marca_modelo': row[1], 'cod_nit': row[2]} for row in result]
    cursor.close()
    connection.close()
    
    return cameras

def get_computadores():
    connection = connect_to_database()  
    cursor = connection.cursor()
    
    # Execute SQL query to fetch both modelo and n_serie
    cursor.execute("SELECT id,nome_ad, n_serie FROM computadores WHERE estado = 'Disponivel'")
    result = cursor.fetchall()  # List of tuples with (modelo, n_serie)
    
    # Convert the result into a list of dictionaries
    computadores = [{'id': row[0],'nome_ad': row[1], 'n_serie': row[2]} for row in result]
    
    cursor.close()
    connection.close()
    
    return computadores

def get_headset():
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT id,marca_modelo,cod_nit FROM headset WHERE estado = 'Disponivel' ")
    result = cursor.fetchall()
    headsets = [{'id': row[0],'marca_modelo': row[1], 'cod_nit': row[2]} for row in result]
    cursor.close()
    connection.close()
    
    return headsets

def get_voip():
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT id,marca_modelo,cod_nit FROM voip WHERE estado = 'Disponivel' ")
    result = cursor.fetchall()
    voips = [{'id': row[0],'marca_modelo': row[1], 'cod_nit': row[2]} for row in result]
    cursor.close()
    connection.close()
    
    return voips

def get_monitores():
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT id,marca_modelo,n_serie FROM monitores WHERE estado = 'Disponivel' ")
    result = cursor.fetchall()
    monitores = [{'id': row[0],'marca_modelo': row[1], 'n_serie': row[2]} for row in result]
    cursor.close()
    connection.close()
    
    return monitores

def get_outros():
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT id,marca_modelo,n_serie FROM monitores WHERE estado = 'Disponivel' ")
    result = cursor.fetchall()
    monitores = [{'id': row[0],'marca_modelo': row[1], 'n_serie': row[2]} for row in result]
    cursor.close()
    connection.close()
    
    return monitores
def get_requisicao_by_id(requisicao_id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM requisicoes WHERE id = %s", (requisicao_id,))
    
    # Fetch a single result (if exists)
    result = cursor.fetchone()  # Use fetchone() for a single record
    
    cursor.close()
    connection.close()
    
    return result

def update_equipment_atributo_a(requisicao_id, nome_requisicao, equipamento_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    # Get requisicao details (assuming you have already fetched requisicao details based on requisicao_id)
    requisicao = get_requisicao_by_id(requisicao_id)  # Example function to get requisicao details
    if not requisicao:
        print(f"Requisicao with ID {requisicao_id} not found!")
        return
    
    tipo_equip = requisicao[3].lower()  # Assuming tipo_equip is in column 3, adjust based on your schema

    # Debugging: Print requisicao and tipo_equip
    print(f"Requisicao: {requisicao}, Tipo Equip: {tipo_equip}")
    print(requisicao_id)
    
    # Conditional update based on the tipo_equip value
    if tipo_equip == 'camera':
        
        cursor.execute(
            "UPDATE cameras SET atribuido_a = %s,requisitado='1', estado='Em uso',id_requisicao=%s WHERE id = %s ",
            (nome_requisicao, requisicao_id,equipamento_id)
        )
    elif tipo_equip == 'computador':
        cursor.execute(
            "UPDATE computadores SET atribuido_a = %s,requisitado='1', estado='Em uso',id_requisicao=%s WHERE id = %s ",
            (nome_requisicao, requisicao_id,equipamento_id)
        )
    elif tipo_equip == 'monitor':
        cursor.execute(
            "UPDATE monitores SET atribuido_a = %s,requisitado='1', estado='Em uso',id_requisicao=%s WHERE id = %s ",
            (nome_requisicao, requisicao_id,equipamento_id)
        )
    elif tipo_equip == 'headset':
        cursor.execute(
            "UPDATE headset SET atribuido_a = %s,requisitado='1', estado='Em uso',id_requisicao=%s WHERE id = %s ",
            (nome_requisicao, requisicao_id,equipamento_id)
        )
    elif tipo_equip == 'voip':
        cursor.execute(
            "UPDATE voip SET atribuido_a = %s,requisitado='1', estado='Em uso',id_requisicao=%s WHERE id = %s ",
            (nome_requisicao, requisicao_id,equipamento_id)
        )
    else:
        print("Tipo de equipamento não encontrado ou inválido")
    
    connection.commit()  # Commit the transaction to save changes
    cursor.close()
    connection.close()

def update_equipment_from_requisicao(requisicao_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    # Get requisicao details
    requisicao = get_requisicao_by_id(requisicao_id)  # Function to fetch requisicao details
    if not requisicao:
        print(f"Requisicao with ID {requisicao_id} not found!")
        return

    tipo_equip = requisicao[3].lower()  # Assuming tipo_equip is in column 3

    # Debugging
    #print(f"Requisicao: {requisicao}, Tipo Equip: {tipo_equip}")

    # Conditional update based on the tipo_equip value
    equipamento_id = None
    if tipo_equip == 'camera':
        cursor.execute("SELECT id FROM cameras WHERE id_requisicao=%s", (requisicao_id,))
        equipamento = cursor.fetchone()
        
        equipamento_id = equipamento[0] if equipamento else None
        print(equipamento_id)
        if equipamento_id:
        # Update the equipment table to reset its state
            cursor.execute(
                "UPDATE cameras SET atribuido_a = 'NIT webcams', requisitado='0', estado='Disponivel', id_requisicao=NULL WHERE id = %s",
                (equipamento_id,)
            )
            
    elif tipo_equip == 'computador':
        cursor.execute("SELECT id FROM computadores WHERE id_requisicao=%s", (requisicao_id,))
        equipamento = cursor.fetchone()
        equipamento_id = equipamento[0] if equipamento else None
        if equipamento_id:
            cursor.execute(
                "UPDATE computadores SET atribuido_a = 'NIT portateis', requisitado='0', estado='Disponivel', id_requisicao=NULL WHERE id = %s",
                (equipamento_id,)
            )
           
    elif tipo_equip == 'monitor':
        cursor.execute("SELECT id FROM monitores WHERE id_requisicao=%s", (requisicao_id,))
        equipamento = cursor.fetchone()
        equipamento_id = equipamento[0] if equipamento else None
        if equipamento_id:
            cursor.execute(
                "UPDATE monitores SET atribuido_a = 'NIT monitores', requisitado='0', estado='Disponivel', id_requisicao=NULL WHERE id = %s",
                (equipamento_id,)
            )
            
    elif tipo_equip == 'headset':
        cursor.execute("SELECT id FROM headset WHERE id_requisicao=%s", (requisicao_id,))
        equipamento = cursor.fetchone()
        equipamento_id = equipamento[0] if equipamento else None
        print(equipamento_id)
        if equipamento_id:
            cursor.execute(
                "UPDATE headset SET atribuido_a = 'NIT headset', requisitado='0', estado='Disponivel', id_requisicao=NULL WHERE id = %s",
                (equipamento_id,)
            )
            
    elif tipo_equip == 'voip':
        cursor.execute("SELECT id FROM voip WHERE id_requisicao=%s", (requisicao_id,))
        equipamento = cursor.fetchone()
        equipamento_id = equipamento[0] if equipamento else None
        print("tou ca dentro")
        if equipamento_id:
            print("tou ca dentro")
            cursor.execute(
                "UPDATE voip SET atribuido_a = 'NIT voip', requisitado='0', estado='Disponivel', id_requisicao=NULL WHERE id = %s",
                (equipamento_id,)
            )
           
    else:
        print("Tipo de equipamento não encontrado ou inválido")

    # Commit changes to the database
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Requisition {requisicao_id} closed successfully.")
    
def update_estado_requisicao(requisicao_id, estado):
    connection = connect_to_database()
    cursor = connection.cursor()

    # Ensure estado is a valid value
    cursor.execute(
        "UPDATE requisicoes SET estado = %s WHERE id = %s",
        (estado, requisicao_id)
    )
    
    connection.commit()
    cursor.close()
    connection.close()
    
def get_cameras_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM cameras WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_monitores_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM monitores WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_computadores_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM computadores WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_headsets_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM headset WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_outros_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM outros WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_voip_user(user_name):
    connection = connect_to_database() 
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM voip WHERE atribuido_a = %s ",(user_name,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

