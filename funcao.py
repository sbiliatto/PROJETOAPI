import threading
import smtplib
from email.mime.text import MIMEText
from flask_bcrypt import generate_password_hash, check_password_hash

def validar_senha(senha: str):
    if not senha:
        return False

    maiuscula = minuscula = numero = especial = False

    for s in senha:
        if s.isupper():
            maiuscula = True
        elif s.islower():
            minuscula = True
        elif s.isdigit():
            numero = True
        elif not s.isalnum():
            especial = True

    if len(senha) < 8 or len(senha) > 12:
        return False

    if not (maiuscula and minuscula and numero and especial):
        return False
    return True

def enviando_email(destinatario, assunto, mensagem):
    user = "laisrcurso@gmail.com"
    senha = "fkvh zoyg pujv zpdp"

    msg = MIMEText(mensagem)
    msg['Subject'] = assunto
    msg['From'] = user
    msg['To'] = destinatario

    server = smtplib.SMTP('smpt.gmail', 587)
    server.starttls()
    server.login(user, senha)
    server.send_message(msg)
    server.quit()