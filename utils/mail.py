"""Optional SMTP delivery for password reset messages."""
from email.message import EmailMessage
import smtplib
from flask import current_app


def send_password_reset_email(recipient, reset_url):
    server = current_app.config.get('MAIL_SERVER')
    sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    if not server or not sender:
        return False

    message = EmailMessage()
    message['Subject'] = 'Apex EMS password reset'
    message['From'] = sender
    message['To'] = recipient
    message.set_content(
        'Use this secure Apex EMS link to set a new password. '
        f'The link expires soon and can be used once:\n\n{reset_url}'
    )
    with smtplib.SMTP(server, current_app.config.get('MAIL_PORT', 587), timeout=10) as smtp:
        if current_app.config.get('MAIL_USE_TLS', True):
            smtp.starttls()
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)
    return True
