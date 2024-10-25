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
    return render_template('index.html')


@app.route('/inventory')
def inventory():
    equipamentos = get_all_equip()
    
    return render_template('inventory.html',equipamentos=equipamentos)


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

@app.route('/editar_equipamento')
def edit_equip():
    serial_number = request.args.get('serial_number')
    all_schools = get_escolas()
    
    # Fetch the equipment data based on serial_number
    equipment_data = get_equipment_by_serial(serial_number)
    print(equipment_data)  # Check if the data is loaded correctly

    return render_template('edit_equipment.html', equipment=equipment_data, all_schools=all_schools)


if __name__ == '__main__':
    app.run(debug=True)