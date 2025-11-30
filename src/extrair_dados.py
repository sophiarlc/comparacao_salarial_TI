import os
import time
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from prefect import task, flow, get_run_logger

def formatar_moeda_br(valor):

    if pd.isna(valor) or str(valor).strip() == '':
        return "-"
    
    str_val = str(valor).strip()
    
    try:
        # Lógica para tratar os dados vindos do CSV:
        limpo = str_val.replace('R$', '').strip()
        if ',' in limpo:
            limpo = limpo.replace('.', '').replace(',', '.')
        else:
            limpo = limpo.replace('.', '')
            
        numero = float(limpo)

        formatado_us = f"{numero:,.2f}"

        formatado_br = formatado_us.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return formatado_br
        
    except ValueError:
        return str_val

@task(name="Extrair Dados Brasil")
def extrair_dados_brasil():
    logger = get_run_logger()
    output_path = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\salarios_ti_brasil.csv"
    
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.apinfo2.com/apinfo/informacao/p12sal-br.cfm"
        logger.info(f"Acessando: {url}")
        driver.get(url)
        time.sleep(3)

        xpath_tabela = "/html/body/div[5]/div[1]/div/section/div/div/center/table"
        element_tabela = driver.find_element(By.XPATH, xpath_tabela)
        html_content = element_tabela.get_attribute('outerHTML')

        df = pd.read_html(StringIO(html_content), header=0, converters={2: str, 3: str})[0]

        logger.info(f"Brasil: {len(df)} linhas extraídas.")
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        logger.info(f"Salvo em: {output_path}")

    except Exception as e:
        logger.error(f"Erro Brasil: {e}")
        raise e
    finally:
        driver.quit()

@task(name="Extrair Dados SP")
def extrair_dados_sp():
    logger = get_run_logger()
    output_path = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\salarios_ti_sp.csv"
    
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.apinfo2.com/apinfo/informacao/p25sal-sp.cfm"
        logger.info(f"Acessando: {url}")
        driver.get(url)
        time.sleep(3)

        xpath_tabela = "/html/body/div[5]/div[1]/div/section/div/div/center/table"
        element_tabela = driver.find_element(By.XPATH, xpath_tabela)
        html_content = element_tabela.get_attribute('outerHTML')

        df = pd.read_html(StringIO(html_content), header=0, converters={2: str, 3: str})[0]

        logger.info(f"SP: {len(df)} linhas extraídas.")
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        logger.info(f"Salvo em: {output_path}")

    except Exception as e:
        logger.error(f"Erro SP: {e}")
        raise e
    finally:
        driver.quit()



