import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io

def send_email(recipient, subject, body, attachment_data=None, attachment_filename=None):
    """
    Envía un correo electrónico a través del servidor SMTP de Gmail.
    
    Args:
        recipient (str): Dirección de correo electrónico del destinatario.
        subject (str): Asunto del correo electrónico.
        body (str): Cuerpo del correo electrónico.
        attachment_data (bytes, optional): Datos del archivo adjunto.
        attachment_filename (str, optional): Nombre del archivo adjunto.
    
    Raises:
        Exception: Si hay un error al enviar el correo.
    """
    # Configuración del remitente y credenciales
    sender = 'primepruebaecu@gmail.com'
    password = 'pkwm pjvf qmue imsj'

    # Crear el mensaje multipart
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Detectar si el cuerpo es HTML
    if body.strip().lower().startswith('<html') or body.strip().lower().startswith('<!doctype html'):
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Agregar archivo adjunto si se proporciona
    if attachment_data and attachment_filename:
        attachment = MIMEBase('application', 'pdf')
        attachment.set_payload(attachment_data)
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename= {attachment_filename}'
        )
        msg.attach(attachment)

    try:
        # Conexión al servidor SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Habilitar cifrado TLS
            server.login(sender, password)  # Iniciar sesión
            server.send_message(msg)  # Enviar mensaje
    except Exception as e:
        raise Exception(f"Error al enviar el correo: {e}")

def send_email_simple(recipient, subject, body):
    """
    Función simple para enviar correos sin archivos adjuntos (mantiene compatibilidad).
    """
    return send_email(recipient, subject, body)
