from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/inventory')
def inventory():
    return render_template('inventory.html')


@app.route('/adicionar_equipamento')
def add_equip():
    return render_template('add_equipment.html')

@app.route('/transferir_equipamento')
def transfer_equip():
    return render_template('transfer_equipment.html')


if __name__ == '__main__':
    app.run(debug=True)