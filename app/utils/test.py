from email_utils import send_email

try:
    send_email(
        recipient="destinatario@gmail.com",
        subject="Prueba de correo",
        body="Este es un correo de prueba enviado desde Flask."
    )
    print("Correo enviado correctamente.")
except Exception as e:
    print(f"Error: {e}")
