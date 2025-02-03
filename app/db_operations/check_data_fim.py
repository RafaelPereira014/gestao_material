from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'db',
    'user': 'root',
    'password': 'dpf37ek>N49E',
    'database': 'gestao_material'
}

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)

def send_email(to_emails, subject, message, attachments=[]):
    try:
        # SMTP server configuration
        smtp_server = 'pegasus.azores.gov.pt'
        smtp_port = 587
        user = 's0204gestmaterial'
        password = 'jioa3UUz3utcnKXH'
        from_email = 'noreply@azores.gov.pt'

        # Create a secure SSL context
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(user, password)
            print(f"Sending email to: {to_emails}")  # Debugging statement

            for to_email in to_emails:
                print(f"Sending email to: {to_email}")  # Debugging statement

                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject

                # Attach the message body
                msg.attach(MIMEText(message, 'html'))

                # Attach files if provided
                for attachment_path in attachments:
                    try:
                        filename = os.path.basename(attachment_path)  # Extract filename from path
                        # Open the file in binary mode
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{filename}"',  # Correctly set the filename here
                            )
                            msg.attach(part)
                    except Exception as e:
                        print(f"Failed to attach file {attachment_path}: {e}")

                # Send the email
                server.sendmail(from_email, to_email, msg.as_string())

        print("Emails sent successfully")

    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check requisitions and send reminders
def check_due_requisitions():
    today_date = datetime.today().date()
    print(f"Today's date: {today_date}")
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Modify the SQL query to extract the date part of `data_fim`
    query = """
        SELECT id, email, data_fim, tipo_equipamento, nome,ticket_id
        FROM requisicoes
        WHERE DATE(data_fim) = %s AND estado = 'ativa'
    """
    
    cursor.execute(query, (today_date,))
    overdue_requisitions = cursor.fetchall()

    cursor.close()
    connection.close()
    
    

    return overdue_requisitions


def get_equip_details(equipment_type, nome, requisicao_id):
    table_mapping = {
    "computador": "computadores",
    "monitor": "monitores",
    "camera": "cameras",
    "voip": "voip",
    "headset": "headset"
    }

    table_name = table_mapping.get(equipment_type.lower())
    if not table_name:
        return {"error": "Tipo de equipamento inválido"}
    
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = f"SELECT * FROM {table_name} WHERE atribuido_a=%s AND id_requisicao=%s"
    cursor.execute(query, (nome, requisicao_id))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result

# Function to send reminders for overdue requisitions
def send_reminders():
    overdue_requisitions = check_due_requisitions()
    
    
    if not overdue_requisitions:
        print("No overdue requisitions found.")
        return

    for requisition in overdue_requisitions:
        requisicao_id = requisition['id']
        user_email = [requisition['email'], 'srec.nit.edu@azores.gov.pt']
        material_type = requisition['tipo_equipamento']
        name = requisition['nome']
        due_date = requisition['data_fim']
        ticket_id= requisition['ticket_id']
        details = get_equip_details(material_type,name,requisicao_id)
        nome_equipamento = details[2]
        
        subject = f"Requisição de material #{ticket_id} - Devolução pendente"
        message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .email-container {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }}
                .header {{ font-size: 18px; font-weight: bold; color: #333; }}
                .content {{ margin-top: 10px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">Atenção: Devolução de material pendente</div>
                <div class="content">
                    <p>Caro(a) utilizador(a) {name} ,</p>
                    <p>O material referente à sua requisição <strong>#{ticket_id}</strong> deve ser devolvido até hoje, <strong>{due_date}</strong>. Até ao momento, não foi registada qualquer devolução.</p>
                    <p>Detalhes do material:</p>
                    <ul>
                        <li>Tipo de equipamento: <strong>{material_type}</strong></li>
                        <li>Equipamento: <strong>{nome_equipamento}</strong></li>
                    </ul>
                    <p>Por favor, devolva o material o mais breve possível. Para mais informações, consulte a plataforma através do seguinte link: <a href="https://helpdesk.edu.azores.gov.pt/{ticket_id}">Consulta de Requisição</a></p>
                </div>
                <div class="footer">
                    <p>Obrigado,<br>A Equipa REDA</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_email(user_email, subject, message)
        

send_reminders()