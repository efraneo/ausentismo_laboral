"""Envío de correos para 2FA y notificaciones."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM_NAME, ADMIN_EMAIL

def _send_email(destinatario, asunto, cuerpo_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USER}>"
    msg["To"] = destinatario
    msg.attach(MIMEText(cuerpo_html, "html"))
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False

def enviar_codigo_2fa(destinatario, nombre, codigo):
    asunto = "Tu código de verificación - Sistema Ausentismo SST"
    cuerpo = f"""
    <html><body style="font-family: Arial, sans-serif; color:#222;">
        <h2 style="color:#0d6efd;">Hola {nombre},</h2>
        <p>Tu código de verificación (2FA) es:</p>
        <h1 style="background:#0d6efd;color:#fff;padding:14px;border-radius:8px;
                   text-align:center;letter-spacing:6px;font-size:34px;">{codigo}</h1>
        <p>Este código expira en <strong>5 minutos</strong>.</p>
        <hr><small>Ausentismo Laboral 2026 By EESC</small>
    </body></html>
    """
    return _send_email(destinatario, asunto, cuerpo)

def notificar_admin_registro(nombre_nuevo, usuario_nuevo, correo_nuevo):
    if not ADMIN_EMAIL:
        return
    asunto = "🚨 Nuevo usuario pendiente de aprobación"
    cuerpo = f"""
    <html><body style="font-family: Arial, sans-serif;">
        <h3>Nuevo registro en el sistema</h3>
        <p><b>Nombre:</b> {nombre_nuevo}</p>
        <p><b>Usuario:</b> {usuario_nuevo}</p>
        <p><b>Correo:</b> {correo_nuevo}</p>
        <p>Ingresa al sistema para aprobar o rechazar la solicitud.</p>
    </body></html>
    """
    _send_email(ADMIN_EMAIL, asunto, cuerpo)
