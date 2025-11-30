import smtplib
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from prefect import task, flow, get_run_logger
from os import getenv
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

EMAIL_REMETENTE = "sophialeite32@gmail.com"
EMAIL_DESTINATARIO = "sophialeite32@gmail.com"
SENHA_APP = getenv("SENHA_APP") 

PATH_EXCEL = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\resultado_kpis.xlsx"

def formatar_moeda(valor):
    """Transforma float 10500.50 em 'R$ 10.500,50'"""
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(valor)

def formatar_porcentagem(valor):
    """Transforma 0.452 em '45,20%' (Multiplica por 100)"""
    try:
        val = float(valor)
        return f"{val * 100:.2f}".replace('.', ',') + "%"
    except:
        return str(valor)

@task(name="Ler e Preparar Dados Excel")
def preparar_dados_excel():
    logger = get_run_logger()
    
    if not os.path.exists(PATH_EXCEL):
        logger.error(f"Arquivo Excel não encontrado em: {PATH_EXCEL}")
        raise FileNotFoundError("Excel de KPIs não encontrado.")

    logger.info("Lendo arquivo Excel e formatando dados...")

    # --- 1. Top 5 Maiores Salários SP ---
    df_sp = pd.read_excel(PATH_EXCEL, sheet_name='Top 5 SP')
    cols_dinheiro = ['CLT', 'PJ', 'Maior_Salario']
    for col in cols_dinheiro:
        if col in df_sp.columns:
            df_sp[col] = df_sp[col].apply(formatar_moeda)

    # --- 2. Top 5 Diferença BR vs SP ---
    df_diff = pd.read_excel(PATH_EXCEL, sheet_name='Top 5 Diferença')
    cols_dinheiro_diff = ['Maior_Salario_BR', 'Maior_Salario_SP', 'Diferenca_Absoluta']
    for col in cols_dinheiro_diff:
        if col in df_diff.columns:
            df_diff[col] = df_diff[col].apply(formatar_moeda)
    
    # Renomear colunas para ficar mais legível no email
    df_diff.rename(columns={
        'Maior_Salario_BR': 'Salário BR', 
        'Maior_Salario_SP': 'Salário SP',
        'Diferenca_Absoluta': 'Diferença'
    }, inplace=True)

    # --- 3. Top 5 Vantagem PJ Percentual ---
    df_pj = pd.read_excel(PATH_EXCEL, sheet_name='Top 5 Vantagem PJ')
    for col in ['CLT', 'PJ']:
        if col in df_pj.columns:
            df_pj[col] = df_pj[col].apply(formatar_moeda)
    
    if 'Vantagem_PJ_Perc' in df_pj.columns:
        df_pj['Vantagem_PJ_Perc'] = df_pj['Vantagem_PJ_Perc'].apply(formatar_porcentagem)
    
    df_pj.rename(columns={'Vantagem_PJ_Perc': 'Vantagem (%)'}, inplace=True)

    logger.info("Dados lidos e formatados com sucesso.")
    return df_sp, df_diff, df_pj

@task(name="Gerar HTML do Email")
def gerar_corpo_html(df_sp, df_diff, df_pj):
    logger = get_run_logger()
    logger.info("Gerando HTML estilizado...")

    # CSS para alinhamento e beleza
    estilo_css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background-color: #f4f4f4; }
        .container { width: 90%; margin: 20px auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 15px; }
        h2 { color: #16a085; margin-top: 30px; font-size: 18px; }
        p { font-size: 14px; color: #555; line-height: 1.5; }
        
        /* Tabela Bonita */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 10px; 
            background-color: #fff;
        }
        th { 
            background-color: #007acc; 
            color: #ffffff; 
            padding: 12px; 
            text-transform: uppercase; 
            font-size: 12px;
            border: 1px solid #005f99;
        }
        td { 
            padding: 10px; 
            border: 1px solid #ddd; 
            font-size: 13px;
            color: #444;
        }
        
        /* ALINHAMENTO SOLICITADO */
        th, td {
            text-align: center;      /* Horizontal */
            vertical-align: middle;  /* Vertical */
        }
        
        /* Zebrado */
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #eef7ff; }
        
        .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #999; }
    </style>
    """

    # Converte DataFrames para HTML
    html_sp = df_sp.to_html(index=False, border=0)
    html_diff = df_diff.to_html(index=False, border=0)
    html_pj = df_pj.to_html(index=False, border=0)

    corpo = f"""
    <html>
    <head>{estilo_css}</head>
    <body>
        <div class="container">
            <h1>Relatório Executivo: Salários TI</h1>
            <p>Olá, Sophia.</p>
            <p>O processo de ETL foi concluído. Seguem os destaques estratégicos do mercado:</p>

            <h2>Top 5 Maiores Salários em SP</h2>
            {html_sp}

            <h2>Top 5 Diferença Salarial (Brasil vs SP)</h2>
            <p>Cargos com maior disparidade absoluta de valores.</p>
            {html_diff}

            <h2>Top 5 Vantagem PJ (%) - Brasil</h2>
            <p>Cargos onde a modalidade PJ oferece o maior ganho percentual sobre a CLT.</p>
            {html_pj}

            <div class="footer">
                <p>Relatório gerado automaticamente via Prefect Pipeline</p>
            </div>
        </div>
    </body>
    </html>
    """
    return corpo

@task(name="Disparar Email via SMTP")
def enviar_email_smtp(corpo_html):
    logger = get_run_logger()
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg['Subject'] = "Relatório KPIs: Salários TI (SP vs BR)"
    msg.attach(MIMEText(corpo_html, 'html'))

    logger.info(f"Conectando ao servidor SMTP do Gmail para enviar a: {EMAIL_DESTINATARIO}...")
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_APP)
        text = msg.as_string()
        server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, text)
        server.quit()
        logger.info("E-mail enviado com sucesso!")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail: {e}")
        logger.error("Dica: Verifique se a 'Senha de App' está correta (não é a senha de login).")
        raise e

@task(name="Fluxo Envio de Email - KPIs")
def enviar_email():
    logger = get_run_logger()
    logger.info("Iniciando fluxo de envio de e-mail...")
    
    # 1. Carregar dados
    df_sp, df_diff, df_pj = preparar_dados_excel()
    
    # 2. Gerar HTML
    html_final = gerar_corpo_html(df_sp, df_diff, df_pj)
    
    # 3. Enviar
    enviar_email_smtp(html_final)
