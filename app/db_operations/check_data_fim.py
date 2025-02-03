from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import pymysql
from config import DB_CONFIG



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
            print(f"Sending email to: {to_emails}")  # Add this to debug the recipient email

            for to_email in to_emails:
                # Create a MIMEMultipart object to represent the email
                print(f"Sending email to: {to_email}")  # Add this to debug the recipient email

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
    # Get today's date
    today_date = datetime.today().date()
    
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # SQL query to fetch requisitions that are due or overdue
    query = """
        SELECT id,email, data_fim, tipo_equipamento, nome
        FROM requisicoes 
        WHERE data_fim < %s AND estado == 'ativa'
    """
    
    # Execute the query to fetch overdue requisitions
    cursor.execute(query, (today_date,))
    overdue_requisitions = cursor.fetchall()

    cursor.close()
    connection.close()

    return overdue_requisitions

# Function to send reminders for overdue requisitions
def send_reminders():
    overdue_requisitions = check_due_requisitions()

    for requisition in overdue_requisitions:
        requisicao_id = requisition['id']
        user_email = requisition['email']
        material_type = requisition['tipo_equipamento']
        material_name = requisition['nome']
        due_date = requisition['data_fim']
        
        subject = f"Requisição de material #{requisicao_id} - Devolução pendente"
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
                    <p>Prezado utilizador,</p>
                    <p>O material referente à sua requisição <strong>#{requisicao_id}</strong> deveria ter sido devolvido até <strong>{due_date}</strong>. Até o momento, não foi registrado como devolvido.</p>
                    <p>Detalhes do material:</p>
                    <ul>
                        <li>Tipo de equipamento: <strong>{material_type}</strong></li>
                        <li>Equipamento: <strong>{material_name}</strong></li>
                    </ul>
                    <p>Por favor, devolva o material o mais breve possível. Para mais informações, consulte a plataforma através do seguinte link: <a href="http://helpdesk.com/{requisicao_id}">Consulta de Requisição</a></p>
                </div>
                <div class="footer">
                    <p>Obrigado,<br>A Equipa REDA</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_email(user_email, subject, message)
        print(f"Reminder sent for requisition #{requisicao_id} to {user_email}.")

send_reminders()