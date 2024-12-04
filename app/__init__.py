import csv
from datetime import datetime
from io import BytesIO, StringIO, TextIOWrapper
import mimetypes
import os
from urllib.parse import unquote
import bcrypt
from flask import Flask, flash, jsonify, render_template, redirect, send_file, send_from_directory, session, url_for, request
from flask_limiter import Limiter
import pymysql
from app.db_operations.edit_equip import *
from app.db_operations.inventory import *
from app.db_operations.profile import *
from app.db_operations.statistics import *
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
    equipment_counts = get_equipment_counts(user_data.get('escola_id'))
    total_equipm = total_equip(user_data.get('escola_id'))
    
    return render_template('index.html',year=year,is_admin=is_admin(session['user_id']),equipment_counts=equipment_counts,total_equipm=total_equipm)


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
    print(user_data)
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

    # Filter the equipment based on the search query
    if search_query:
        equipamentos = [e for e in equipamentos if search_query.lower() in e['serial_number'].lower()]

    per_page = 10  # Number of items per page
    page = int(request.args.get('page', 1))  # Get the current page, default to 1 if not specified

    total_pages = (len(equipamentos) + per_page - 1) // per_page  # Calculate total pages
    start = (page - 1) * per_page
    end = start + per_page
    equipamentos_paginated = equipamentos[start:end]  # Slice the equipment list for the current page

    
    for equipamento in equipamentos_paginated:
        escola_name_from = get_school_name_by_id(equipamento['escola_id'])  
        equipamento['escola_name_from'] = escola_name_from  
        escola_name_to = get_school_name_by_id(equipamento['cedido_a_escola']) 
        equipamento['escola_name_to'] = escola_name_to 

    return render_template('inventory.html', 
                           equipamentos=equipamentos_paginated, 
                           page=page, 
                           total_pages=total_pages, 
                           search_query=search_query,
                           is_admin=is_admin(session['user_id']))


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
                tipo = request.form['itemName']

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
                csv_reader = csv.reader(TextIOWrapper(csv_file, encoding='utf-8'), delimiter=';')

                # Skip header row if present
                next(csv_reader, None)

                row_count = 0  # Track number of rows processed
                for row in csv_reader:
                    if len(row) < 3 or not all(row[:3]):  # Check if required fields are filled
                        print(f"Skipping incomplete row: {row}")  
                        continue
                    
                    numero_serie = row[0]
                    tipo = row[1]
                    cc_aluno = row[3] if len(row) > 3 and row[3] else None  
                    data_aquisicao = datetime.now().date()
                    data_ultimo_movimento = data_aquisicao
                    status = 'Em uso' if cc_aluno else 'Disponivel'

                    # Use the escola_id from the user instead of the CSV
                    escola_id = user_details.get('escola_id')

                    # Check if the serial number already exists
                    if is_serial_number_exists(numero_serie, escola_id):
                        print(f"Skipping duplicate serial number: {numero_serie}")
                        continue

                    print(f"Inserting bulk equipment row: {numero_serie}, {tipo}, {status}, {cc_aluno}, {escola_id}")

                    # Insert bulk equipment data into the database
                    cursor.execute(
                        """
                        INSERT INTO equipamentos (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, serial_number, aluno_CC)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (tipo, status, escola_id, data_aquisicao, data_ultimo_movimento, numero_serie, cc_aluno)
                    )
                    row_count += 1

                connection.commit()
                flash(f"{row_count} equipment entries added successfully in bulk!", "success")
                print(f"Bulk equipment insertion complete. Rows added: {row_count}")  
                success = True

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

@app.route('/editar_equipamento', methods=['GET', 'POST'])
def edit_equip():
    if request.method == 'POST':
        serial_number = request.form.get('SerialNo')
        equipment_type = request.form.get('item')
        from_location = request.form.get('fromLocation')
        escola_id = get_school_id_by_name(from_location)
        status = request.form.get('status')
        assigned_to = request.form.get('assignedTo')
        to_location = request.form.get('toLocation') if request.form.get('toggleCedido') else None
        id_escola = get_school_id_by_name(to_location)
        document = request.files.get('document')

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
        update_equipment(serial_number, escola_id, equipment_type, status, assigned_to, datetime.now(), id_escola)

        return redirect(url_for('inventory'))

    # Fetch equipment details
    serial_number = request.args.get('serial_number')
    id_escola = request.args.get('escola_id')
    
    if session['user_type'] == 'admin':
        all_schools = get_escolas()
    else:
        all_schools = get_schools_same_island(id_escola)
        
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
    

@app.route('/item_page')
def item_page():
    serial_number = request.args.get('serial_number')
    id_escola = request.args.get('escola_id')
    equipment = get_equipment_by_serial(serial_number, id_escola)
    
    school_id = equipment['cedido_a_escola'] if equipment['cedido_a_escola'] is not None else equipment['escola_id']
    escola_nome = get_school_name_by_id(school_id)
    acessorios = get_equipment_acessories(equipment['id'])
    
    # Fetch documents for the equipment and school
    documents = get_documents_by_equipment_and_school(equipment['id'], id_escola)
    print(documents)
    
    return render_template(
        'item_page.html',
        equipment=equipment,
        escola_nome=escola_nome,
        is_admin=is_admin(session['user_id']),
        acessorios=acessorios,
        documents=documents
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


if __name__ == '__main__':
    app.run(debug=True)