from prefect import flow, get_run_logger
from utils.enviar_email_erro_fluxo import enviar_email_erro
from extrair_dados import extrair_dados_brasil, extrair_dados_sp
from medir_kpis import medir_kpis
from enviar_email import enviar_email

@flow(name="Diferenca Salarial em TI entre BR e SP", on_failure=[enviar_email_erro])
def main_flow():
    logger = get_run_logger()
    extrair_dados_brasil()
    extrair_dados_sp()
    medir_kpis()
    enviar_email()
    logger.info("Fluxo de Diferenca Salarial em TI entre BR e SP concluído com sucesso!")

if __name__ == "__main__":
    main_flow()
