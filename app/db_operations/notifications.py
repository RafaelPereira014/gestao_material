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
        
        
def send_email_on_material_assign(ticket_id, username,recipient_emails,material_type,material_name,material_link):
    subject = f"Requisição de material: #{ticket_id}."
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
            <div class="header">Material atribuído ao utilizador <strong>{username}</strong></div>
            <div class="content">
                <p>Foi-lhe atribuído o seguinte material, referente ao pedido de requisicao #{ticket_id}.</p>
                <p>Detalhes do material:</p>
                <ul>
                    <li>Tipo de equipamento:<strong></strong> {material_type}</li>
                    <li>Equipamento:<strong></strong> {material_name}</li>
                </ul>
                <p>Para mais informações ou esclarecimentos, pode consultar a plataforma através do seguinte link: <a href="{material_link}">{material_link}</a>.</p>
            </div>
            <div class="footer">
                <p>Obrigado,<br>NIT</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(recipient_emails, subject, message)
    
def send_email_on_material_return_due(ticket_id, username, recipient_emails, material_type, material_name, return_date, material_link):
    subject = f"Devolução de material: #{ticket_id} - Prazo de entrega atingido"
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
            <div class="header">Lembrete: Devolução de material atribuído</div>
            <div class="content">
                <p>Caro(a) {username},</p>
                <p>Este email serve como lembrete de que o prazo para a devolução do material atribuído está a terminar.</p>
                <p>Detalhes do material:</p>
                <ul>
                    <li><strong>Pedido de requisição:</strong> #{ticket_id}</li>
                    <li><strong>Tipo de equipamento:</strong> {material_type}</li>
                    <li><strong>Equipamento:</strong> {material_name}</li>
                    <li><strong>Data limite para devolução:</strong> {return_date}</li>
                </ul>
                <p>Por favor, garanta que o material é devolvido até à data indicada. Para mais informações ou esclarecimentos, pode consultar a plataforma através do seguinte link: <a href="{material_link}">{material_link}</a>.</p>
            </div>
            <div class="footer">
                <p>Obrigado,<br>Equipa NIT</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(recipient_emails, subject, message)
    
def send_email_on_material_closure(ticket_id,recipient_emails,material_link):
    subject = f"Requisição de material: #{ticket_id}."
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
            <div class="header">Encerramento do pedido de requisição.</strong></div>
            <div class="content">
                <p>Este email confirma o encerramento da requisição e a entrega do material associado ao pedido <strong>#{ticket_id}</strong>.</p>
                <p>Para mais informações ou esclarecimentos, pode consultar a plataforma através do seguinte link: <a href="{material_link}">{material_link}</a>.</p>
            </div>
            <div class="footer">
                <p>Obrigado,<br>NIT</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(recipient_emails, subject, message)