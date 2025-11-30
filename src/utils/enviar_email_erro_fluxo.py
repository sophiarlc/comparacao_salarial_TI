import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def enviar_email_erro(flow, flow_run, state):
    """
    Envia um e-mail de notificação quando um fluxo do Prefect falha.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_user = "sophialeite32@gmail.com"
    email_password = getenv("SENHA_APP")
    recipient_email = "sophialeite32@gmail.com"

    subject = f"Falha no Fluxo do Prefect: {flow_run.name}"
    
    try:
        error_message = state.result(raise_on_failure=False)
    except Exception as e:
        error_message = f"Não foi possível extrair a mensagem de erro específica: {e}"

    body = f"""
    <p>O fluxo <strong>{flow.name}</strong> falhou.</p>
    <p><strong>Nome da Execução:</strong> {flow_run.name}</p>
    <p><strong>Estado:</strong> Falha</p>
    <p><strong>Mensagem de Erro:</strong></p>
    <pre>{error_message}</pre>
    <p>Por favor, verifique os logs para mais detalhes.</p>
    """

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, recipient_email, text)
        server.quit()
        print("E-mail de notificação de falha enviado com sucesso.")
    except Exception as e:
        print(f"Falha ao enviar o e-mail de notificação: {e}")