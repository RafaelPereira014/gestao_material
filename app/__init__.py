import csv
from datetime import datetime
from io import BytesIO, StringIO, TextIOWrapper
from fpdf import FPDF
import os
from urllib.parse import unquote
import bcrypt
from flask import Flask, flash, jsonify, make_response, render_template, redirect, send_file, send_from_directory, session, url_for, request
from flask_limiter import Limiter
import pymysql
from app.db_operations.edit_equip import *
from app.db_operations.inventory import *
from app.db_operations.profile import *
from app.db_operations.statistics import *
from app.db_operations.notifications import *
from app.db_operations.add_equip import *
from config import DB_CONFIG

from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    #storage_uri="redis://localhost:6379/0",  # Redis connection URI
    default_limits=["100 per minute"]  # Default rate limit for the entire app
)

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("100 per minute")  # Apply a custom rate limit specifically for the login route
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        
        if not email or not password:
            error = 'Username and password are required'
            return render_template('login.html', error=error)

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id,password,role FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()

        
        if user_data:
            stored_password = user_data[1].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session['user_id'] = user_data[0]  # Store user ID in session
                session['user_type'] = user_data[2]  # Store user type in session
                session.permanent = True
                return redirect('/index')  # Redirect to dashboard on success
            else:
                flash('Email ou password incorretos.', 'danger')

        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('login'))  # Redirect to homepage after logout


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    token = request.form.get('token')
    # Add logic to verify the token and reset the password
    flash('Intruções para recuperar a password foram enviadas para o respetivo email.', 'success')
    return redirect(url_for('login'))


@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    year = datetime.now().year
    user_data = get_user_fields(session['user_id'])
    escola_nome = get_school_name_by_id(user_data.get('escola_id'))
    equipment_counts = get_equipment_counts(user_data.get('escola_id'))
    total_equipm = total_equip(user_data.get('escola_id'))
    
    
    return render_template('index.html',year=year,is_admin=is_admin(session['user_id']),equipment_counts=equipment_counts,total_equipm=total_equipm,escola_nome=escola_nome)


@app.route('/adicionar_utilizador', methods=['GET', 'POST'])
def add_user():
    escolas = get_escolas()  # Retrieve available schools for selection
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        escola = request.form.get('escola')
        escola_id = get_school_id_by_name(escola)
        role = request.form.get('role')
        password = request.form.get('password')
        #print(username)

        if not username or not email or not role or not password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('add_user.html', escolas=escolas)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = connect_to_database()
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('O email já se encontra registado na plataforma.', 'danger')
            cursor.close()
            conn.close()
            return render_template('add_user.html', escolas=escolas)

        # Insert the new user
        cursor.execute(
            "INSERT INTO users (username, email, escola_id, role, password) VALUES (%s, %s, %s, %s, %s)",
            (username, email, escola_id, role, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('User added successfully', 'success')
        return redirect(url_for('index'))  # Redirect to a success page or dashboard

    return render_template('add_user.html', escolas=escolas,is_admin=is_admin(session['user_id']))

@app.route('/perfil', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_data = get_user_fields(session['user_id'])
    escola_nome = get_school_name_by_id(user_data.get('escola_id'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Validate current password
        stored_password_hash = user_data['password']
        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            return jsonify({'success': False, 'message': 'Senha atual incorreta.'}), 400

        # Hash the new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the password in the database
        update_password(session['user_id'], new_password_hash)
        return redirect(url_for('user_profile'))


    return render_template(
        'user_profile.html',
        user_data=user_data,
        is_admin=is_admin(session['user_id']),
        escola_nome=escola_nome
    )

@app.route('/inventory')
def inventory():
    user_id = session.get('user_id')  # Get the user_id from session
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated

    search_query = request.args.get('search', '')  # Get the search query from the request
    search_type = request.args.get('search_type', 'serial_number')  # Get the selected search type, default to serial_number

    if is_admin(user_id):
        equipamentos = get_all_equip()  # Fetch all equipment data
    else:
        # Fetch the user's escola_id and get equipment based on that
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT escola_id FROM users WHERE id = %s", (user_id,))
        escola_id = cursor.fetchone()
        cursor.close()
        conn.close()

        if escola_id:
            equipamentos = get_equip_by_escola(escola_id[0])  # Fetch equipment by escola_id
        else:
            equipamentos = []  # No equipment found if escola_id is not found

    # Filter the equipment based on the search query and selected type
    if search_query:
        if search_type == 'serial_number':
            equipamentos = [e for e in equipamentos if search_query.lower() in e['serial_number'].lower()]
        elif search_type == 'equipamento':
            equipamentos = [e for e in equipamentos if search_query.lower() in e['tipo'].lower()]
        elif search_type == 'cc_aluno':
            equipamentos = [e for e in equipamentos if search_query.lower() in (e['aluno_CC'] or '').lower()]
        elif search_type == 'status':
            equipamentos = [e for e in equipamentos if search_query.lower() in (e['status'] or '').lower()]

    per_page = 10  # Number of items per page
    page = int(request.args.get('page', 1))  # Get the current page, default to 1 if not specified

    # Calculate total pages
    total_pages = (len(equipamentos) + per_page - 1) // per_page

    # Calculate the start and end index for pagination
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, len(equipamentos))

    # Slice the list of equipamentos for the current page
    equipamentos_paginated = equipamentos[start_index:end_index]

    # Fetch escola names for each equipamento
    for equipamento in equipamentos_paginated:
        escola_name_from = get_school_name_by_id(equipamento['escola_id'])  
        equipamento['escola_name_from'] = escola_name_from  
        escola_name_to = get_school_name_by_id(equipamento['cedido_a_escola']) 
        equipamento['escola_name_to'] = escola_name_to 

    # Calculate pagination range (for displaying 5 pages at a time, like 1-5, 6-10, etc.)
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template('inventory.html', 
                           equipamentos=equipamentos_paginated, 
                           page=page, 
                           total_pages=total_pages, 
                           search_query=search_query,
                           search_type=search_type,
                           start_page=start_page,
                           end_page=end_page,
                           is_admin=is_admin(session['user_id']))
    
@app.route('/inventory_nit')
def inventory_nit():
    user_id = session.get('user_id')  # Get the user_id from session
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated
    
    
    return render_template('inventory_nit.html',is_admin=is_admin(session['user_id']))

@app.route('/tabelas')
def tabelas_nit():
    user_id = session.get('user_id')  # Get the user_id from session
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated
    
    
    return render_template('tabelas_nit.html',is_admin=is_admin(session['user_id']))

@app.route('/fetch_tabelas')
def fetch_tabelas():
    inventory_type = request.args.get('type', 'marcas')  # Default category
    search_query = request.args.get('search', '').strip()  # Search term
    current_page = int(request.args.get('page', 1))  # Current page
    per_page = 10  # Items per page

    query_templates = {
        key: f"SELECT * FROM {table} WHERE nome LIKE %s LIMIT %s OFFSET %s"
        for key, table in {
            "marcas": "marcas",
            "modelos": "modelos",
            "users_a_atribuir": "users_a_atribuir",
            "discos": "discos",
            "processadores": "processadores",
            "rams": "rams",
            "tipo_monitor": "tipo_monitor",
            "polegadas": "polegadas",
            "tipo_voip": "tipo_voip",
            "sistema_operativo": "sistema_operativo",
            "office": "office",
            "firma": "firma",
            "garantias": "garantia",
            "tipo_camera": "tipo_camera",
            "tipo_headset": "tipo_headset",
        }.items()
    }

    count_templates = {
        key: f"SELECT COUNT(*) AS count FROM {table} WHERE nome LIKE %s"
        for key, table in {
            "marcas": "marcas",
            "modelos": "modelos",
            "users_a_atribuir": "users_a_atribuir",
            "discos": "discos",
            "processadores": "processadores",
            "rams": "rams",
            "tipo_monitor": "tipo_monitor",
            "polegadas": "polegadas",
            "tipo_voip": "tipo_voip",
            "sistema_operativo": "sistema_operativo",
            "office": "office",
            "firma": "firma",
            "garantias": "garantia",
            "tipo_camera": "tipo_camera",
            "tipo_headset": "tipo_headset",
        }.items()
    }

    # Validate the inventory type
    if inventory_type not in query_templates:
        return "<p class='text-danger'>Categoria inválida.</p>", 400

    try:
        connection = connect_to_database()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Prepare search terms with wildcards
        search_term = f"%{search_query}%"
        

        if inventory_type == "marcas":
            cursor.execute(count_templates[inventory_type], (search_term,))
        else:
            cursor.execute(count_templates[inventory_type], (search_term,))
        total_items = cursor.fetchone().get('count', 0)

        # Calculate pagination details
        total_pages = (total_items + per_page - 1) // per_page
        offset = (current_page - 1) * per_page

        if inventory_type == "marcas":
            cursor.execute(query_templates[inventory_type], (search_term, per_page, offset))
        else:
            cursor.execute(query_templates[inventory_type], (search_term, per_page, offset))
        inventory_data = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"<p class='text-danger'>Erro ao carregar {inventory_type}: {str(e)}</p>", 500
    except KeyError as e:
        return f"<p class='text-danger'>Erro: Campo de pesquisa '{str(e)}' não encontrado. Verifique os filtros fornecidos.</p>", 400
    except Exception as e:
        return f"<p class='text-danger'>Erro inesperado: {str(e)}</p>", 500
    finally:
        if connection:
            connection.close()

    # Render the inventory table
    return render_template(
        'NIT_table.html',
        items=inventory_data,
        current_page=current_page,
        total_pages=total_pages,
        inventory_type=inventory_type,
    )
@app.route('/fetch_inventory')
def fetch_inventory():
    inventory_type = request.args.get('type', 'computadores')  # Default category
    search_query = request.args.get('search', '').strip()  # Search term
    estado_query = request.args.get('estado', '').strip()  # Estado filter
    so_query = request.args.get('so', '').strip()  # SO filter (only for computadores)
    modelo_query = request.args.get('modelo', '').strip()  # Marca/Modelo filter (only for computadores)
    current_page = int(request.args.get('page', 1))  # Current page
    per_page = 10  # Items per page

    # Query templates for counting and fetching data
    query_templates = {
        "computadores": """SELECT * FROM computadores 
                           WHERE atribuido_a LIKE %s 
                           AND (%s = '' OR estado = %s)
                           AND (%s = '' OR so LIKE %s)
                           AND (%s = '' OR modelo LIKE %s)
                           LIMIT %s OFFSET %s""",
        "monitores": """SELECT * FROM monitores 
                        WHERE atribuido_a LIKE %s 
                        AND (%s = '' OR estado = %s)
                        LIMIT %s OFFSET %s""",
        "cameras": """SELECT * FROM cameras 
                      WHERE atribuido_a LIKE %s 
                      AND (%s = '' OR estado = %s)
                      LIMIT %s OFFSET %s""",
        "voip": """SELECT * FROM voip 
                   WHERE atribuido_a LIKE %s 
                   AND (%s = '' OR estado = %s)
                   LIMIT %s OFFSET %s""",
        "headset": """SELECT * FROM headset 
                      WHERE atribuido_a LIKE %s 
                      AND (%s = '' OR estado = %s)
                      LIMIT %s OFFSET %s""",
        "outros": """SELECT * FROM outros 
                     WHERE atribuido_a LIKE %s 
                     AND (%s = '' OR estado = %s)
                     LIMIT %s OFFSET %s""",
    }

    count_templates = {
        "computadores": """SELECT COUNT(*) AS count FROM computadores 
                           WHERE atribuido_a LIKE %s 
                           AND (%s = '' OR estado = %s)
                           AND (%s = '' OR so LIKE %s)
                           AND (%s = '' OR modelo LIKE %s)""",
        "monitores": """SELECT COUNT(*) AS count FROM monitores 
                        WHERE atribuido_a LIKE %s 
                        AND (%s = '' OR estado = %s)""",
        "cameras": """SELECT COUNT(*) AS count FROM cameras 
                      WHERE atribuido_a LIKE %s 
                      AND (%s = '' OR estado = %s)""",
        "voip": """SELECT COUNT(*) AS count FROM voip 
                   WHERE atribuido_a LIKE %s 
                   AND (%s = '' OR estado = %s)""",
        "headset": """SELECT COUNT(*) AS count FROM headset 
                      WHERE atribuido_a LIKE %s 
                      AND (%s = '' OR estado = %s)""",
        "outros": """SELECT COUNT(*) AS count FROM outros 
                     WHERE atribuido_a LIKE %s 
                     AND (%s = '' OR estado = %s)""",
    }

    # Validate the inventory type
    if inventory_type not in query_templates:
        return "<p class='text-danger'>Categoria inválida.</p>", 400

    try:
        connection = connect_to_database()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Prepare search terms with wildcards
        search_term = f"%{search_query}%"
        estado_term = estado_query if estado_query else ""
        so_term = f"%{so_query}%" if so_query else ""
        modelo_term = f"%{modelo_query}%" if modelo_query else ""

        # Fetch the total count of items for pagination
        if inventory_type == "computadores":
            cursor.execute(
                count_templates[inventory_type],
                (search_term, estado_term, estado_term, so_query, so_term, modelo_query, modelo_term),
            )
        else:
            cursor.execute(count_templates[inventory_type], (search_term, estado_term, estado_term))
        total_items = cursor.fetchone().get('count', 0)

        # Calculate pagination details
        total_pages = (total_items + per_page - 1) // per_page
        offset = (current_page - 1) * per_page

        # Fetch the inventory data with pagination
        if inventory_type == "computadores":
            cursor.execute(
                query_templates[inventory_type],
                (search_term, estado_term, estado_term, so_query, so_term, modelo_query, modelo_term, per_page, offset),
            )
        else:
            cursor.execute(query_templates[inventory_type], (search_term, estado_term, estado_term, per_page, offset))
        inventory_data = cursor.fetchall()
    except pymysql.MySQLError as e:
        return f"<p class='text-danger'>Erro ao carregar {inventory_type}: {str(e)}</p>", 500
    except KeyError as e:
        return f"<p class='text-danger'>Erro: Campo de pesquisa '{str(e)}' não encontrado. Verifique os filtros fornecidos.</p>", 400
    except Exception as e:
        return f"<p class='text-danger'>Erro inesperado: {str(e)}</p>", 500
    finally:
        if connection:
            connection.close()

    # Render the inventory table
    return render_template(
        'inventory_table.html',
        items=inventory_data,
        current_page=current_page,
        total_pages=total_pages,
        inventory_type=inventory_type,
    )
@app.route('/requisicoes')
def requisicoes():
    user_id = session.get('user_id')  # Get the user_id from session
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated
    today_date = datetime.today().date()
    # Get all requisicoes (all requests)
    all_requisicoes = get_all_requisicoes()
    all_requisicoes_ativas = get_all_requisicoes_ativas()
    # Prepare a dictionary to hold the available equipment for each type
    available_equipments = {}
    
    available_equipments['Camera'] = get_cameras() 
    available_equipments['Monitor'] = get_monitores()
    available_equipments['Computador'] = get_computadores()
    available_equipments['Headset'] = get_headset()
    available_equipments['Voip'] = get_voip()
    
    return render_template('requisicoes.html', is_admin=is_admin(session['user_id']), 
                           all_requisicoes=all_requisicoes, 
                           available_equipments=available_equipments,
                           all_requisicoes_ativas=all_requisicoes_ativas,today_date=today_date)

@app.route('/update_data_fim/<int:requisicao_id>/<int:equipment_id>', methods=['POST'])
def update_data_fim(requisicao_id,equipment_id):
    data = request.get_json()
    new_data_fim = data.get('data_fim')
    if not new_data_fim:
        return jsonify({"error": "Nova data fim não fornecida"}), 400

    try:
        # Call a function to update the data_fim in the database
        update_requisicao_data_fim(requisicao_id, new_data_fim,equipment_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        print("Erro ao atualizar data_fim:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/close_requisition/<int:requisicao_id>/<int:equipment_id>', methods=['POST'])
def close_requisition(requisicao_id,equipment_id):
    # Implement the logic to close the requisition using the provided ID
    try:
        

        requisicao = get_requisicao_by_id(requisicao_id)  # Implement this function

        # Check what requisicao returns
        if not requisicao:
            return jsonify({"status": "error", "message": "Requisition not found."}), 404
        
        user_email = requisicao[2]
        ticket_id = requisicao[10]
        material_link = f'https://helpdesk.edu.azores.gov.pt/ticket_details/{ticket_id}'    
        recipients=[user_email,"srec.nit.edu@azores.gov.pt"]
        
       
        update_estado_requisicao(requisicao_id,'Resolvido',equipment_id)
        update_equipment_from_requisicao(requisicao_id)
        send_email_on_material_closure(ticket_id,recipients,material_link)
        
        return jsonify({"message": "Requisição encerrada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/reopen_requisition/<int:requisicao_id>/<int:equipment_id>', methods=['POST'])
def reopen_requisition(requisicao_id,equipment_id):
    # Implement the logic to close the requisition using the provided ID
    try:
        requisicao = get_requisicao_by_id(requisicao_id)  # Implement this function

        # Check what requisicao returns
        if not requisicao:
            return jsonify({"status": "error", "message": "Requisition not found."}), 404
        
        user_email = requisicao[2]
        ticket_id = requisicao[10]
        material_link = f'https://helpdesk.edu.azores.gov.pt/ticket_details/{ticket_id}'    
        recipients=[user_email,"srec.nit.edu@azores.gov.pt"]
        
        update_estado_requisicao(requisicao_id,'Pendente',equipment_id)
        update_equipment_from_requisicao(requisicao_id)
        
        return jsonify({"message": "Requisição encerrada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/user_page/<string:user_name>')
def user_page(user_name):
    # Fetch the equipment assigned to the user
    user_computadores = get_computadores_user(user_name)
    user_monitores = get_monitores_user(user_name)
    user_cameras = get_cameras_user(user_name)
    user_voip = get_voip_user(user_name)
    user_headset = get_headsets_user(user_name)
    user_outros = get_outros_user(user_name)

    # Combine all equipment into one list for easier handling in the template
    all_items = {
        'Computadores': user_computadores,
        'Monitores': user_monitores,
        'Cameras': user_cameras,
        'VoIP': user_voip,
        'Headsets': user_headset,
        'Outros': user_outros
    }

    return render_template('user_page.html', user_name=user_name, all_items=all_items,is_admin=is_admin(session['user_id']))

@app.route('/generate_log/<string:category>/<int:equipment_id>', methods=['GET'])
def generate_log(category, equipment_id):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        
        category = category.lower()
        print(category)
        
        if category == 'headsets':
            category = 'headset'
    
        if category == 'voips':
            category = 'voip'

        if category == 'computadores':
            category = 'computador'

        if category == 'cameras':
            category = 'camera'
        
        if category == 'monitores':
            category = 'monitor'
            
        print(category)
        print(equipment_id)
            
        query_requisicoes = """
            SELECT 
                r.id , 
                r.nome, 
                r.email, 
                r.tipo_equipamento, 
                r.quantidade, 
                r.motivo, 
                r.data_inicio, 
                r.data_fim, 
                r.estado,
                r.equipment_id
            FROM requisicoes r
            WHERE r.tipo_equipamento = %s AND r.equipment_id=%s
            ORDER BY r.data_inicio DESC
            LIMIT 10
        """
        cursor.execute(query_requisicoes, (category,equipment_id,))  # Pass as a single value
        logs = cursor.fetchall()
        print(logs)

        if not logs:
            return jsonify({"success": False, "message": "Nenhum log encontrado para as requisições associadas."}), 404

        # Generate log content
        log_lines = [
            f"Categoria: {category}",
            f"ID do Equipamento: {equipment_id}",
            "-" * 50
        ]
        for log in logs:
            log_lines.append(
            f"Requisição ID: {log[0]}\n"  # r.id
            f"Nome: {log[1]}\n"          # r.nome
            f"Email: {log[2]}\n"         # r.email
            f"Tipo de Equipamento: {log[3]}\n"  # r.tipo_equipamento
            f"Quantidade: {log[4]}\n"    # r.quantidade
            f"Motivo: {log[5]}\n"        # r.motivo
            f"Data Início: {log[6]}\n"   # r.data_inicio
            f"Data Fim: {log[7] or 'Ainda não devolvido'}\n"  # r.data_fim
            f"Estado: {log[8]}\n"        # r.estado
            "-----------------------------------------------------" 
        )

        log_content = "\n".join(log_lines)

        # Create a temporary log file
        log_file_path = f"/tmp/equipment_log_{category}_{equipment_id}.txt"
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(log_content)

        return send_file(
            log_file_path,
            as_attachment=True,
            download_name=f"log_{category}_{equipment_id}.txt",
            mimetype="text/plain"
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao gerar log: {str(e)}"}), 500
    finally:
        if connection:
            connection.close()

@app.route('/assign-equipment', methods=['POST'])
def assign_equipment():
    requisicao_id = request.form['requisicao_id']
    equipamento_id = request.form['equipamento_id']
    
    # Ensure that requisicao_id and equipamento_id are integers
    try:
        requisicao_id = int(requisicao_id)
        equipamento_id = int(equipamento_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid input data."}), 400

    # Get the requisition data to extract the name
    requisicao = get_requisicao_by_id(requisicao_id)  # Implement this function

    # Check what requisicao returns
    if not requisicao:
        return jsonify({"status": "error", "message": "Requisition not found."}), 404
    
    
    # Get the necessary fields from requisicao
    nome_requisicao = requisicao[1]  
    user_email = requisicao[2]
    material_type = requisicao[3]
    ticket_id = requisicao[10]
    
    

    update_equipment_atributo_a(requisicao_id,nome_requisicao, equipamento_id)
    update_estado_requisicao(requisicao_id, 'ativa',equipamento_id)
    details = get_equip_details(material_type,equipamento_id,requisicao_id)
    user_name = details[1]
    material_name=details[2]
    material_link = f'https://helpdesk.edu.azores.gov.pt/ticket_details/{ticket_id}'    
    recipients=[user_email,"srec.nit.edu@azores.gov.pt"]
    send_email_on_material_assign(ticket_id,user_name,recipients,material_type,material_name,material_link)
    
    return jsonify({"status": "success"}), 200

@app.route('/remove-req', methods=['POST'])
def remove_req():
    requisicao_id = request.form['requisicao_id']
    
    # Ensure that requisicao_id and equipamento_id are integers
    try:
        requisicao_id = int(requisicao_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid input data."}), 400

    remove_requisition(requisicao_id)
    
    
    return jsonify({"status": "success"}), 200

@app.route('/check_serial_number', methods=['POST'])
def check_serial_number():
    numero_serie = request.form.get('numero_serie')
    escola_id = request.form.get('escola_id')  

    if is_serial_number_exists(numero_serie, escola_id):
        return jsonify({'exists': True})
    return jsonify({'exists': False})

@app.route('/adicionar_equipamento', methods=['GET', 'POST'])
def add_equip():
    escolas = get_escolas()  # Ensure this function returns a list of school objects
    success = False
    user_details = get_user_fields(session['user_id'])

    if request.method == 'POST':
        entry_mode = request.form.get('entryMode', 'single')
        print("Entry Mode Selected:", entry_mode)  # Debugging print

        # Get the escola_id from the logged-in user
        escola_id = user_details.get('escola_id')  # This will ensure escola_id is associated with the user

        if entry_mode == 'single':
            connection = None
            cursor = None  # Ensure cursor is initialized
            try:
                numero_serie = request.form['itemSerialNo']
                tipo = request.form['itemType']
                mac_addr = request.form['MACaddr']
                use_case = request.form['itemUse']

                # Automatically associate escola_id from user details
                if not is_admin(session['user_id']):
                    # For non-admin, escola_id is from user details, so no need to select school
                    cc_aluno = request.form.get('assignedTo', None)
                    data_aquisicao = datetime.now().date()
                    data_ultimo_movimento = data_aquisicao
                    status = 'Em uso' if cc_aluno else 'Disponivel'
                    accessories = request.form.get('accessories', None)
                    
                    

                    # Check if the serial number already exists
                    if is_serial_number_exists(numero_serie, escola_id):
                        flash(f"Equipment with serial number {numero_serie} already exists.", "danger")
                        return redirect(url_for('add_equip'))  # Redirect to the add equipment page

                    print(f"Inserting single equipment: {numero_serie}, {tipo}, {status}, {cc_aluno}, {escola_id},{mac_addr},{use_case}")

                    # Insert single equipment into the database
                    connection = connect_to_database()
                    cursor = connection.cursor()  # Initialize cursor here
                    cursor.execute(
                        """
                        INSERT INTO equipamentos (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, serial_number, aluno_CC,mac_addr,use_case)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)
                        """,
                        (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, numero_serie, cc_aluno, mac_addr,use_case)
                    )
                    equipamento_id = cursor.lastrowid

                    # Insert accessories into a related table if provided
                    if accessories:
                        accessories_list = [accessory.strip() for accessory in accessories.split(',') if accessory.strip()]
                        for accessory in accessories_list:
                            print(f"Inserting accessory: {accessory} for equipment {numero_serie}")
                            cursor.execute(
                                """
                                INSERT INTO acessorios (equipamento_id, tipo_acessorio)
                                VALUES (%s, %s)
                                """,
                                (equipamento_id, accessory)
                            )

                    connection.commit()
                    flash("Equipment and accessories added successfully", "success")
                    print("Single equipment and accessories added successfully.")  # Debugging print
                    success = True
                    equipment_added = True  # Replace with actual logic
                    if equipment_added:
                        flash("Equipamento adicionado com sucesso!", "success")
                    else:
                        flash("Erro ao adicionar equipamento. Por favor, tente novamente.", "error")

                else:
                    # For admin users, still use the escola_id from the user
                    escola_nome = request.form['location']
                    cc_aluno = request.form.get('assignedTo', None)
                    data_aquisicao = datetime.now().date()
                    data_ultimo_movimento = data_aquisicao
                    status = 'Em uso' if cc_aluno else 'Disponivel'
                    accessories = request.form.get('accessories', None)
                    escola_id = get_school_id_by_name(request.form['location'])
                    print(escola_id)

                    # Check if the serial number already exists
                    if is_serial_number_exists(numero_serie, escola_id):
                        flash(f"Equipment with serial number {numero_serie} already exists.", "danger")
                        return redirect(url_for('add_equip'))  # Redirect to the add equipment page

                    print(f"Inserting single equipment: {numero_serie}, {tipo}, {status}, {cc_aluno}, {escola_id}")

                    # Insert single equipment into the database
                    connection = connect_to_database()
                    cursor = connection.cursor()  # Initialize cursor here
                    cursor.execute(
                        """
                        INSERT INTO equipamentos (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, serial_number, aluno_CC)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, numero_serie, cc_aluno)
                    )
                    equipamento_id = cursor.lastrowid

                    # Insert accessories into a related table if provided
                    if accessories:
                        accessories_list = [accessory.strip() for accessory in accessories.split(',') if accessory.strip()]
                        for accessory in accessories_list:
                            print(f"Inserting accessory: {accessory} for equipment {numero_serie}")
                            cursor.execute(
                                """
                                INSERT INTO acessorios (equipamento_id, tipo_acessorio)
                                VALUES (%s, %s)
                                """,
                                (equipamento_id, accessory)
                            )

                    connection.commit()
                    flash("Equipment and accessories added successfully", "success")
                    print("Single equipment and accessories added successfully.")  # Debugging print
                    success = True

            except Exception as e:
                flash(f"An error occurred: {e}", "danger")
                print(f"Error adding single equipment: {e}")  # Debugging print
                if connection:
                    connection.rollback()
            finally:
                # Ensure cursor is always closed, even if an error occurs
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

        # If bulk entry mode is selected
        elif entry_mode == 'bulk' and 'csvFile' in request.files:
            csv_file = request.files['csvFile']
            print("Processing bulk CSV file...")  # Debugging print
            connection = None
            cursor = None  # Initialize cursor here
            try:
                connection = connect_to_database()
                cursor = connection.cursor()  # Initialize cursor here

                # Use delimiter=';' for CSV file handling
                csv_reader = csv.reader(TextIOWrapper(csv_file, encoding='utf-8', errors='replace'), delimiter=';')
                
                # Skip header row if present
                next(csv_reader, None)

                row_count = 0  # Track number of rows processed
                for row in csv_reader:
                    if len(row) < 3 or not all(row[:3]):  # Check if required fields are filled
                        print(f"Skipping incomplete row: {row}")
                        continue

                    numero_serie = row[0]
                    tipo = row[1]
                    utilizacao = row[2]  # Assuming row[2] is the 'utilizacao' column

                    # Check if 'digitais' is in utilizacao (case-insensitive)
                    if utilizacao and "digitais" in utilizacao.lower():
                        utilizacao = "Manuais digitais"
                    else:
                        utilizacao = '-'
                        
                    mac_addr = row[3] if row[3] else '-'
                    cc_aluno = row[4]
                    accessories = row[5] if len(row) > 5 else None  # Column for accessories
                    data_aquisicao = datetime.now().date()
                    data_ultimo_movimento = data_aquisicao
                    status = 'Em uso' if cc_aluno else 'Disponivel'

                    # Use the escola_id from the user instead of the CSV
                    escola_id = user_details.get('escola_id')

                    # Check if the serial number already exists
                    if is_serial_number_exists(numero_serie, escola_id):
                        print(f"Skipping duplicate serial number: {numero_serie}")
                        continue

                    print(f"Inserting bulk equipment row: {numero_serie}, {tipo}, {status}, {cc_aluno}, {escola_id},{utilizacao},{mac_addr}")

                    # Insert bulk equipment data into the database
                    cursor.execute(
                        """
                        INSERT INTO equipamentos (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, serial_number, aluno_CC,mac_addr,use_case)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)
                        """,
                        (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, numero_serie, cc_aluno,mac_addr,utilizacao)
                    )
                    equipamento_id = cursor.lastrowid  # Get the last inserted equipamento ID

                    # Process and insert accessories if provided
                    if accessories:
                        accessories_list = [acc.strip() for acc in accessories.split(',') if acc.strip()]
                        for accessory in accessories_list:
                            print(f"Inserting accessory: {accessory} for equipment {numero_serie}")
                            cursor.execute(
                                """
                                INSERT INTO acessorios (equipamento_id, tipo_acessorio)
                                VALUES (%s, %s)
                                """,
                                (equipamento_id, accessory)
                            )

                    row_count += 1

                connection.commit()
                flash(f"{row_count} equipment entries added successfully in bulk, including accessories!", "success")
                print(f"Bulk equipment insertion complete. Rows added: {row_count}")

            except Exception as e:
                flash(f"An error occurred during bulk upload: {e}", "danger")
                print(f"Error during bulk equipment addition: {e}")
                if connection:
                    connection.rollback()
            finally:
                # Ensure cursor is always closed, even if an error occurs
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

        return redirect(url_for('add_equip'))

    return render_template('add_equipment.html', escolas=escolas, success=success, is_admin=is_admin(session['user_id']), user_details=user_details)

@app.route('/add_equipment', methods=['POST'])
def add_item():
    equipment_name = request.form.get('equipment_name')
    inventory_type = request.form.get('inventory_type')

    if equipment_name and inventory_type:
        try:
            # Add logic to insert the equipment into the database
            query = f"INSERT INTO {inventory_type} (nome) VALUES (%s)"
            
            # Connect to the database
            connection = connect_to_database()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, (equipment_name,))
            connection.commit()
            cursor.close()
            
            # Return a success response
            return jsonify({"success": True, "message": f"Item '{equipment_name}' adicionado com sucesso!"})
        except Exception as e:
            print(f"Database Error: {e}")
            return jsonify({"success": False, "message": "Erro ao adicionar o item."}), 500
        finally:
            connection.close()
    else:
        return jsonify({"success": False, "message": "Dados fornecidos incompletos."}), 400

@app.route('/adicionar_equipamento_nit/<category>', methods=['GET', 'POST'])
def add_equipment(category=None):
    if not category:
        return "Categoria não selecionada", 400  # If no category is provided, return error
    
    # List of allowed categories to prevent SQL injection
    allowed_categories = ['-','computadores', 'monitores', 'cameras', 'voip', 'headset','outros']
    
    if category not in allowed_categories:
        return "Categoria inválida", 400  # If the category is not in the allowed list, return error
    
    marcas = get_marcas()
    modelos = get_modelos()
    processadores = get_processadores()
    rams = get_rams()
    monitores = get_tipo_monitores()
    polegadas = get_polegadas()
    voips = get_tipo_voips()
    discos = get_discos()
    sistemas_operativos = get_sistemas_operativos()
    offices = get_offices()
    firmas = get_firmas()
    garantias = get_garantias()
    tipos_camera = get_tipos_camera()
    tipos_headset = get_tipos_headset()
    users = get_atribuidos_a()
    
    if request.method == 'POST':
        form_data = request.form.to_dict()  # Get all form data as a dictionary
        
        
        try:
            # Connect to the database
            connection = connect_to_database()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # Step 1: Get the list of columns for the selected category table
            cursor.execute(f"DESCRIBE {category}")
            table_columns = [column['Field'] for column in cursor.fetchall()]

            # Step 2: Filter the form data to include only the fields that exist in the table
            filtered_form_data = {key: value for key, value in form_data.items() if key in table_columns}

            if 'atribuido_a' in filtered_form_data:
                # Set 'estado' based on the value of 'atribuido_a'
                if not filtered_form_data['atribuido_a'].strip():  # Check if 'atribuido_a' is empty or whitespace
                    filtered_form_data['estado'] = 'disponivel'
                else:
                    filtered_form_data['estado'] = 'em uso'

            if not filtered_form_data:
                return "No valid data to insert.", 400  # Handle the case where no valid data is present

            # Step 3: Prepare the SQL query dynamically based on filtered form data
            fields = ', '.join([f"{key} = %s" for key in filtered_form_data.keys()])
            query = f"INSERT INTO {category} SET {fields}"

            # Step 4: Execute the query with the filtered form values
            cursor.execute(query, list(filtered_form_data.values()))
            connection.commit()
        except pymysql.MySQLError as e:
            return f"Erro ao atualizar a base de dados: {str(e)}", 500
        finally:
            if connection:
                connection.close()
        
        # Redirect back to the form with the selected category, passing 'is_admin' in session
        return redirect(url_for('add_equipment', category=category))

    # Render the template with the 'category' and 'is_admin' session data
    return render_template(
        'add_equipment_nit.html', 
        category=category, 
        is_admin=is_admin(session['user_id']),
        marcas=marcas,
        modelos=modelos,
        processadores=processadores,
        rams=rams,
        monitores=monitores,
        polegadas=polegadas,
        voips=voips,
        sistemas_operativos=sistemas_operativos,
        offices=offices,
        firmas=firmas,
        garantias=garantias,
        tipos_camera=tipos_camera,
        tipos_headset=tipos_headset,
        discos = discos,
        users=users)

@app.route('/editar_equipamento', methods=['GET', 'POST'])
def edit_equip():
    
    
    if request.method == 'POST':
        serial_number = request.form.get('SerialNo')
        equipment_type = request.form.get('itemType')
        from_location = request.form.get('fromLocation')
        escola_id = get_school_id_by_name(from_location)
        status = request.form.get('status')
        assigned_to = request.form.get('assignedTo')
        to_location = request.form.get('toLocation') if request.form.get('toggleCedido') else None
        id_escola = get_school_id_by_name(to_location)
        document = request.files.get('document')
        observacoes = request.form.get('observacoes', '')  
        mac_addr = request.form.get('macAddr')
        utilizacao = request.form.get('itemUse')
        


        # Handle "returned" checkbox
        if request.form.get('returned'):
            id_escola = None
            assigned_to = None
            status = 'Disponivel'
        else:
            # Enforce rules for "Cedido" state
            if request.form.get('toggleCedido'):
                if not to_location:
                    flash("Por favor, selecione a unidade a qual o equipamento está cedido.", "error")
                    return redirect(request.url)
                status = "Em uso"
                id_escola = get_school_id_by_name(to_location)
                
                

        # Save document file if provided
        document_path = None
        if document and document.filename:
            try:
                # Define the upload directory
                upload_dir = os.path.join('static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                # Save the document
                document_path = os.path.join(upload_dir, document.filename)
                document.save(document_path)

                # Store document details in the database
                store_document(
                    user_id=session['user_id'],
                    equipamento_id=get_equip_id_by_serial(serial_number,escola_id),
                    escola_id=escola_id,
                    nome_arquivo=document.filename,
                    caminho_arquivo=document_path
                )
                flash("Documento carregado com sucesso.", "success")
            except Exception as e:
                flash(f"Erro ao carregar o documento: {e}", "danger")
                return redirect(request.url)

        # Update the equipment
        update_equipment(serial_number, escola_id, equipment_type, status, assigned_to, datetime.now(), id_escola,observacoes,mac_addr,utilizacao)

        return redirect(url_for('inventory'))

    # Fetch equipment details
    serial_number = request.args.get('serial_number')
    id_escola = request.args.get('escola_id')
    
    # if session['user_type'] == 'admin':
    #     all_schools = get_escolas()
    # else:
    #     all_schools = get_schools_same_island(id_escola)
        
    all_schools = get_escolas()
        
    equipment_data = get_equipment_by_serial(serial_number, id_escola)
    escola_nome = get_school_name_by_id(equipment_data['escola_id'])
    cedido_status = is_cedido(serial_number, id_escola)  # Check if cedido
    cedido_a = get_school_name_by_id(equipment_data.get('cedido_a_escola'))  # Get cedido school

    return render_template(
        'edit_equipment.html',
        equipment=equipment_data,
        all_schools=all_schools,
        escola_nome=escola_nome,
        is_admin=is_admin(session['user_id']),
        cedido_status=cedido_status,
        cedido_a=cedido_a
    )

@app.route('/edit_item/<string:category>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(category, item_id):

    valid_categories = ['computadores', 'monitores', 
                        'cameras', 'voip', 
                        'headset', 'outros','marcas',
                        'modelos','processadores','rams','discos','tipo_monitor','tipo_camera','tipo_headset',
                        'tipo_voip','polegadas','garantia','office','firma','users_a_atribuir']
    
    if category not in valid_categories:
        return "Categoria inválida", 400


    marcas = get_marcas()
    modelos = get_modelos()
    processadores = get_processadores()
    rams = get_rams()
    monitores = get_tipo_monitores()
    polegadas = get_polegadas()
    voips = get_tipo_voips()
    discos = get_discos()
    sistemas_operativos = get_sistemas_operativos()
    offices = get_offices()
    firmas = get_firmas()
    garantias = get_garantias()
    tipos_camera = get_tipos_camera()
    tipos_headset = get_tipos_headset()
    users = get_atribuidos_a()
    
    if request.method == 'POST':
        # Get form data
        form_data = request.form.to_dict()

        try:
            # Connect to the database
            connection = connect_to_database()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            
            fields = ', '.join([f"{key} = %s" for key in form_data.keys()])
            query = f"UPDATE {category} SET {fields} WHERE id = %s"
            
            values = list(form_data.values()) + [item_id]
            cursor.execute(query, values)
            connection.commit()

        except pymysql.MySQLError as e:
            return f"Erro ao atualizar a base de dados: {str(e)}", 500
        finally:
            if connection:
                connection.close()

        # Redirect to another page or render success message
        return redirect(url_for('inventory_nit'))  # Replace with your desired route

    # For GET request, fetch the item data to display in the form
    try:
        connection = connect_to_database()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Fetch item details
        query = f"SELECT * FROM {category} WHERE id = %s"
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()

        if not item:
            return "Equipamento não encontrado", 404

    except pymysql.MySQLError as e:
        return f"Erro ao consultar a base de dados: {str(e)}", 500
    finally:
        if connection:
            connection.close()

    # Render the template for editing
    return render_template(
        'edit_item.html', 
        item=item, 
        category=category, 
        is_admin=is_admin(session['user_id']),
        marcas=marcas,
        modelos=modelos,
        processadores=processadores,
        rams=rams,
        monitores=monitores,
        polegadas=polegadas,
        voips=voips,
        sistemas_operativos=sistemas_operativos,
        offices=offices,
        firmas=firmas,
        garantias=garantias,
        tipos_camera=tipos_camera,
        tipos_headset=tipos_headset,
        discos = discos,
        users=users)

@app.route('/remove_equip/<serial_number>/<escola_id>', methods=['GET', 'POST'])
def remove_equip(serial_number, escola_id):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Delete the equipment and associated accessories
        cursor.execute("DELETE FROM acessorios WHERE equipamento_id = (SELECT id FROM equipamentos WHERE serial_number = %s AND escola_id = %s)", (serial_number, escola_id))
        cursor.execute("DELETE FROM equipamentos WHERE serial_number = %s AND escola_id = %s", (serial_number, escola_id))

        connection.commit()
        flash("Equipamento removido com sucesso.", "success")
    except Exception as e:
        flash(f"Erro ao remover o equipamento: {e}", "danger")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return redirect(url_for('inventory'))

@app.route('/remove_equipment/<category>/<int:equipment_id>', methods=['DELETE'])
def remove_equipment(category, equipment_id):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        query = f"DELETE FROM {category} WHERE id = %s"
        cursor.execute(query, (equipment_id,))
        connection.commit()
        return jsonify({"success": True, "message": "Equipamento removido com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao remover equipamento: {str(e)}"}), 500
    finally:
        if connection:
            connection.close()

@app.route('/item_page')
def item_page():
    serial_number = request.args.get('serial_number')
    id_escola = request.args.get('escola_id')
    equipment = get_equipment_by_serial(serial_number, id_escola)
    
    school_id = equipment['cedido_a_escola'] if equipment['cedido_a_escola'] is not None else equipment['escola_id']
    escola_nome = get_school_name_by_id(school_id)
    acessorios = get_equipment_acessories(equipment['id'])
    observacoes = equipment['observacoes']
    
    # Fetch documents for the equipment and school
    documents = get_documents_by_equipment_and_school(equipment['id'], id_escola)
    print(documents)
    
    return render_template(
        'item_page.html',
        equipment=equipment,
        escola_nome=escola_nome,
        is_admin=is_admin(session['user_id']),
        acessorios=acessorios,
        documents=documents,
        observacoes=observacoes
    )
    
@app.route('/view_document/<path:filename>', methods=['GET'])
def view_document(filename):
    try:
        # Send the file from the 'uploads' directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "File not found", 404


@app.route('/download_document/<path:filename>', methods=['GET'])
def download_document(filename):
    try:
        # Decode the filename in case of URL encoding issues
        filename = unquote(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Attempting to serve file from: {file_path}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404


@app.route('/receive-data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received data:", data)

    material_types = data.get('material_type', [])  # Safely get material_type, default to an empty list if not found

    if not material_types:
        return "Material types are required.", 400  # Return an error if material_types is empty

    # Extract other fields from the data
    ticket_id = data['ID']
    username = data['User']
    email = data['User email']
    quantity = data['quantidade']
    reason = data['motivo']
    start_date = datetime.strptime(data['data_inicio'], '%Y-%m-%d')
    # Handle 'data_fim' with None as default
    end_date_str = data.get('data_fim')  # Get the 'data_fim' value
    if end_date_str:  # If a value is provided, parse it
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:  # Use None to represent an empty date
        end_date = None

    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        
        for material_type in material_types:
            cursor.execute(
                """
                INSERT INTO requisicoes (nome, email, tipo_equipamento, quantidade, motivo, data_inicio, data_fim,ticket_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                """,
                (username, email, material_type, quantity, reason, start_date, end_date,ticket_id)
            )

        connection.commit()

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        return "Error while inserting data into the database.", 500

    finally:
        cursor.close()
        connection.close()

    return "Data received and stored successfully!", 200
    


if __name__ == '__main__':
    app.run(debug=True)