from datetime import datetime
from flask import Flask, flash, render_template, redirect, url_for, request
import mysql.connector
from app.db_operations.edit_equip import *
from app.db_operations.inventory import *
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    year = datetime.now().year
    return render_template('index.html',year=year)


@app.route('/inventory')
def inventory():
    equipamentos = get_all_equip()
    per_page = 10  # Number of items per page
    page = int(request.args.get('page', 1))  # Get the current page, default to 1 if not specified
    
    total_pages = (len(equipamentos) + per_page - 1) // per_page  # Calculate total pages
    start = (page - 1) * per_page
    end = start + per_page
    equipamentos_paginated = equipamentos[start:end]  # Slice the equipment list for the current page

    return render_template('inventory.html', equipamentos=equipamentos_paginated, page=page, total_pages=total_pages)

@app.route('/adicionar_equipamento', methods=['GET', 'POST'])
def add_equip():
    escolas = get_escolas()  # Ensure this function returns a list of school objects
    success = False

    if request.method == 'POST':
        numero_serie = request.form['itemSerialNo']
        tipo = request.form['itemName']
        escola_id = request.form['location']
        #user_id = request.form['assignedTo'] if request.form.get('assignedTo') else None
        cc_aluno = request.form['assignedTo'] if request.form.get('assignedTo') else None
        data_aquisicao = datetime.now().date()  # Get the current date
        data_ultimo_movimento = data_aquisicao
        status = 'Em uso' if cc_aluno else 'Disponivel'

        # Insert equipment into the database
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            print("Preparing to insert equipment...")  # Debugging print
            cursor.execute(
                """
                INSERT INTO equipamentos (serial_number, tipo, status, aluno_CC, escola_id, data_aquisicao, data_ultimo_movimento)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (numero_serie, tipo, status, cc_aluno, escola_id, data_aquisicao, data_ultimo_movimento)
            )
            connection.commit()  # Commit changes to the database
            flash("Equipment added successfully", "success")
            print("Equipment inserted successfully!")  # Debugging print
            success = True  # Set this based on your actual success condition
        except mysql.connector.Error as e:
            flash(f"An error occurred: {e}", "danger")
            print(f"Error: {e}")  # Print error for debugging
        finally:
            cursor.close()  # Close cursor
            connection.close()  # Close connection

        return redirect(url_for('add_equip'))

    return render_template('add_equipment.html', escolas=escolas,sucess=success)

@app.route('/editar_equipamento', methods=['GET', 'POST'])
def edit_equip():
    if request.method == 'POST':
        # Capture form data
        serial_number = request.form.get('SerialNo')
        equipment_type = request.form.get('item')
        from_location = request.form.get('fromLocation')
        status = request.form.get('status')
        assigned_to = request.form.get('assignedTo')
        to_location = request.form.get('toLocation') if request.form.get('toggleCedido') else None
        id_escola = get_school_id_by_name(to_location)
        document = request.files.get('document')
        
        # Check if the "returned" checkbox is checked
        if request.form.get('returned'):
            id_escola = None  # Set cedido_a_escola to NULL
        else:
            to_location = request.form.get('toLocation') if request.form.get('toggleCedido') else None
            id_escola = get_school_id_by_name(to_location)


        # Process the document file if provided
        if document:
            document_path = f'static/uploads/{document.filename}'
            document.save(document_path)  # Save the uploaded document to a specified path
        else:
            document_path = None

        # Call a function to update the equipment in the database
        update_equipment(serial_number,equipment_type,status,assigned_to,datetime.now(),id_escola)

        
        
        return redirect(url_for('inventory'))
    
    # GET request: Render the edit form with the existing equipment data
    all_schools = get_escolas()
    serial_number = request.args.get('serial_number')
    equipment_data = get_equipment_by_serial(serial_number)
    
    return render_template('edit_equipment.html', equipment=equipment_data, all_schools=all_schools)

@app.route('/item_page')
def item_page():
    serial_number = request.args.get('serial_number')
    # Retrieve equipment details by ID
    equipment = get_equipment_by_serial(serial_number)
    return render_template('item_page.html', equipment=equipment)


if __name__ == '__main__':
    app.run(debug=True)