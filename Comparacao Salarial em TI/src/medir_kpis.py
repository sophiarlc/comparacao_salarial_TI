import pandas as pd
import os
from prefect import task, flow, get_run_logger

PATH_SP = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\salarios_ti_sp.csv"
PATH_BR = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\salarios_ti_brasil.csv"
PATH_OUT = r"C:\Users\Sophia - Documentos\Comparacao Salarial em TI\data\resultado_kpis.xlsx"

df_sp = pd.DataFrame()
df_br = pd.DataFrame()

@task(name="Carregar e Tratar Dados", description="Lê CSVs com ; e trata pontos/vírgulas")
def carregar_dados_globais():
    logger = get_run_logger()
    global df_sp, df_br
    
    def ler_e_limpar(path):
        try:
            # Lê com delimitador ponto e vírgula, forçando string para não perder zeros
            df = pd.read_csv(path, sep=';', encoding='utf-8', dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(path, sep=';', encoding='latin1', dtype=str)
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {path}: {e}")
            return pd.DataFrame()

        # Tratamento de Nulos
        df['Especialidade'] = df['Especialidade'].fillna('-')
        
        # Converte colunas numéricas (Remove ponto de milhar, troca vírgula por ponto)
        cols_num = ['CLT', 'PJ']
        for col in cols_num:
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace('R$', '', regex=False).str.strip()
            df[col] = df[col].str.replace('.', '', regex=False)
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Cria coluna auxiliar de Maior Salário
        df['Maior_Salario'] = df[cols_num].max(axis=1)
        return df

    logger.info("Iniciando carregamento dos CSVs...")
    df_sp = ler_e_limpar(PATH_SP)
    df_br = ler_e_limpar(PATH_BR)
    
    logger.info(f"Dados carregados. SP: {len(df_sp)} linhas, BR: {len(df_br)} linhas.")

@task(name="KPI: Top 5 Salários BR")
def kpi_top_5_maiores_salarios_br():
    logger = get_run_logger()
    logger.info("Calculando Top 5 Salários BR")
    
    top5 = df_br.sort_values(by='Maior_Salario', ascending=False).head(5)
    return top5[['Cargo', 'Especialidade', 'CLT', 'PJ', 'Maior_Salario']]

@task(name="KPI: Top 5 Salários SP")
def kpi_top_5_maiores_salarios_sp():
    logger = get_run_logger()
    logger.info("Calculando Top 5 Salários SP")
    
    top5 = df_sp.sort_values(by='Maior_Salario', ascending=False).head(5)
    return top5[['Cargo', 'Especialidade', 'CLT', 'PJ', 'Maior_Salario']]

@task(name="KPI: Top 5 Diferença BR vs SP")
def kpi_top_5_diferenca_br_sp():
    logger = get_run_logger()
    logger.info("Calculando Diferença Salarial BR vs SP")
    
    df_merge = pd.merge(
        df_br[['Cargo', 'Especialidade', 'Maior_Salario']], 
        df_sp[['Cargo', 'Especialidade', 'Maior_Salario']], 
        on=['Cargo', 'Especialidade'], 
        suffixes=('_BR', '_SP'),
        how='inner'
    )
    
    df_merge['Diferenca_Absoluta'] = (df_merge['Maior_Salario_BR'] - df_merge['Maior_Salario_SP']).abs()
    top5_diff = df_merge.sort_values(by='Diferenca_Absoluta', ascending=False).head(5)
    
    return top5_diff

@task(name="KPI: Top 5 Vantagem PJ (%)")
def kpi_top_5_vantagem_pj_percentual_br():
    logger = get_run_logger()
    logger.info("Calculando Vantagem PJ Percentual")
    
    df_calc = df_br[df_br['CLT'] > 0].copy()
    df_calc['Vantagem_PJ_Perc'] = ((df_calc['PJ'] - df_calc['CLT']) / df_calc['CLT'])
    top5_pj = df_calc.sort_values(by='Vantagem_PJ_Perc', ascending=False).head(5)
    
    return top5_pj[['Cargo', 'Especialidade', 'CLT', 'PJ', 'Vantagem_PJ_Perc']]

@task(name="KPI: Ranking Linguagens (Devs)")
def kpi_ranking_linguagens_analista_br():
    logger = get_run_logger()
    logger.info("Calculando Ranking de Linguagens")
    
    df_devs = df_br[df_br['Cargo'].str.contains('Analista de sistemas', case=False, na=False)].copy()
    ranking_devs = df_devs.sort_values(by='Maior_Salario', ascending=False)
    
    return ranking_devs[['Cargo', 'Especialidade', 'Maior_Salario']]

@task(name="KPI: Média Gestão vs Técnico")
def kpi_media_salarial_gestao_vs_tecnico_sp():
    logger = get_run_logger()
    logger.info("Calculando Média Gestão vs Técnico em SP")
    
    def categorizar(row):
        texto = str(row['Cargo']).lower()
        if any(x in texto for x in ['agile', 'master', 'coach', 'adm']):
            return 'Gestão/Liderança'
        elif any(x in texto for x in ['analista', 'suporte', 'dev']):
            return 'Técnico/Operacional'
        else:
            return 'Outros'

    df_sp_cat = df_sp.copy()
    df_sp_cat['Categoria'] = df_sp_cat.apply(categorizar, axis=1)
    
    resumo = df_sp_cat.groupby('Categoria')['Maior_Salario'].mean().reset_index()
    resumo = resumo.sort_values(by='Maior_Salario', ascending=False)
    return resumo

@task(name="Salvar Excel", description="Consolida todos os DataFrames em um xlsx")
def salvar_resultados(res_br, res_sp, res_diff, res_pj, res_ling, res_cat):
    logger = get_run_logger()
    
    # Cria diretório se não existir
    pasta = os.path.dirname(PATH_OUT)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        
    try:
        with pd.ExcelWriter(PATH_OUT, engine='xlsxwriter') as writer:
            res_br.to_excel(writer, sheet_name='Top 5 BR', index=False)
            res_sp.to_excel(writer, sheet_name='Top 5 SP', index=False)
            res_diff.to_excel(writer, sheet_name='Top 5 Diferença', index=False)
            res_pj.to_excel(writer, sheet_name='Top 5 Vantagem PJ', index=False)
            res_ling.to_excel(writer, sheet_name='Ranking Linguagens', index=False)
            res_cat.to_excel(writer, sheet_name='Media Gestao vs Tec', index=False)
            
            # Formatação de Moeda (R$) e Porcentagem
            workbook = writer.book
            fmt_currency = workbook.add_format({'num_format': 'R$ #,##0.00'})
            fmt_pct = workbook.add_format({'num_format': '0.00%'})

            # 1. Top 5 BR (Cols C, D, E -> CLT, PJ, Maior_Salario)
            ws_br = writer.sheets['Top 5 BR']
            ws_br.set_column('C:E', 15, fmt_currency)

            # 2. Top 5 SP (Cols C, D, E -> CLT, PJ, Maior_Salario)
            ws_sp = writer.sheets['Top 5 SP']
            ws_sp.set_column('C:E', 15, fmt_currency)

            # 3. Top 5 Diferença (Cols C, D, E -> Salario_BR, Salario_SP, Diferenca)
            ws_diff = writer.sheets['Top 5 Diferença']
            ws_diff.set_column('C:E', 15, fmt_currency)

            # 4. Top 5 Vantagem PJ (Cols C, D -> CLT, PJ) e (Col E -> %)
            ws_pj = writer.sheets['Top 5 Vantagem PJ']
            ws_pj.set_column('C:D', 15, fmt_currency)
            ws_pj.set_column('E:E', 12, fmt_pct)

            # 5. Ranking Linguagens (Col C -> Maior_Salario)
            ws_ling = writer.sheets['Ranking Linguagens']
            ws_ling.set_column('C:C', 15, fmt_currency)

            # 6. Media Gestao vs Tec (Col B -> Maior_Salario)
            ws_cat = writer.sheets['Media Gestao vs Tec']
            ws_cat.set_column('B:B', 15, fmt_currency)

        logger.info(f"Arquivo salvo com sucesso em: {PATH_OUT}")
    except Exception as e:
        logger.error(f"Erro ao salvar Excel: {e}")

@task(name="Medir KPIs", log_prints=True)
def medir_kpis():
    logger = get_run_logger()
    logger.info("Iniciando Fluxo Medir KPIs...")
    
    # 1. Carrega dados para variaveis globais
    carregar_dados_globais()
    
    # Verificação de segurança se o carregamento falhou
    if df_br.empty or df_sp.empty:
        logger.error("DataFrames vazios. Abortando cálculo de KPIs.")
        return

    r_br = kpi_top_5_maiores_salarios_br()
    r_sp = kpi_top_5_maiores_salarios_sp()
    r_diff = kpi_top_5_diferenca_br_sp()
    r_pj = kpi_top_5_vantagem_pj_percentual_br()
    r_ling = kpi_ranking_linguagens_analista_br()
    r_cat = kpi_media_salarial_gestao_vs_tecnico_sp()
    
    # 3. Salva Resultados
    salvar_resultados(r_br, r_sp, r_diff, r_pj, r_ling, r_cat)
    
    logger.info("Fluxo finalizado com sucesso.")

