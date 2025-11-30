# Comparação Salarial em TI - Brasil vs São Paulo

![Fluxo Prefect](images/fluxo%20prefect.png)

![Relatório por E-mail](images/email.png)

Este projeto automatiza a extração, análise e envio de relatórios sobre salários na área de Tecnologia da Informação, comparando dados do Brasil e do estado de São Paulo.

## 📋 Descrição

O sistema realiza web scraping de dados salariais de profissionais de TI, calcula KPIs (Key Performance Indicators) relevantes e envia um relatório executivo por e-mail com os principais insights do mercado.

### Principais Funcionalidades

- **Extração Automatizada**: Coleta dados salariais de sites especializados usando Selenium
- **Análise de KPIs**: Calcula métricas estratégicas sobre o mercado de TI
- **Relatório Executivo**: Gera e envia e-mail HTML estilizado com os resultados
- **Orquestração com Prefect**: Gerenciamento de fluxo de trabalho com logging e tratamento de erros

## 🏗️ Estrutura do Projeto

```
Comparacao Salarial em TI/
├── src/
│   ├── main.py                          # Orquestrador principal do fluxo
│   ├── extrair_dados.py                 # Extração de dados via web scraping
│   ├── medir_kpis.py                    # Cálculo de KPIs e geração de Excel
│   ├── enviar_email.py                  # Envio de relatório por e-mail
│   ├── .env                             # Variáveis de ambiente (não versionado)
│   └── utils/
│       └── enviar_email_erro_fluxo.py   # Notificação de erros no fluxo
├── data/                                # Dados extraídos e resultados
│   ├── salarios_ti_brasil.csv
│   ├── salarios_ti_sp.csv
│   └── resultado_kpis.xlsx
├── images/                              # Imagens do projeto
├── .gitignore
└── README.md
```

## 📊 KPIs Calculados

O sistema gera as seguintes análises:

1. **Top 5 Maiores Salários BR**: Cargos com maiores remunerações no Brasil
2. **Top 5 Maiores Salários SP**: Cargos com maiores remunerações em São Paulo
3. **Top 5 Diferença BR vs SP**: Cargos com maior disparidade salarial entre Brasil e SP
4. **Top 5 Vantagem PJ (%)**: Cargos onde a modalidade PJ oferece maior ganho percentual sobre CLT
5. **Ranking Linguagens**: Ranking salarial de Analistas de Sistemas por especialidade/linguagem
6. **Média Gestão vs Técnico**: Comparação de salários médios entre cargos de gestão e técnicos em SP

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- Conta Gmail com senha de aplicativo configurada

### Instalação

1. Clone o repositório ou baixe os arquivos do projeto

2. Instale as dependências:
```bash
pip install pandas selenium webdriver-manager prefect xlsxwriter python-dotenv
```

3. Configure as variáveis de ambiente:

Crie um arquivo `.env` na pasta `src/` com o seguinte conteúdo:
```
SENHA_APP=sua_senha_de_aplicativo_gmail
```

> **Nota**: Para gerar uma senha de aplicativo do Gmail, acesse: [Senhas de app do Google](https://myaccount.google.com/apppasswords)

4. Ajuste os caminhos dos arquivos:

Edite os seguintes arquivos para ajustar os caminhos conforme seu ambiente:
- `extrair_dados.py`: Linhas 40, 76 (caminhos de saída dos CSVs)
- `medir_kpis.py`: Linhas 5-7 (caminhos dos CSVs e Excel de saída)
- `enviar_email.py`: Linhas 13-14 (e-mails), linha 17 (caminho do Excel)

### Execução

Execute o fluxo principal:

```bash
cd src
python main.py
```

O sistema irá:
1. Extrair dados salariais do Brasil e São Paulo
2. Calcular os KPIs e gerar arquivo Excel
3. Enviar e-mail com relatório executivo

## 📧 Configuração de E-mail

O projeto utiliza SMTP do Gmail para envio de e-mails. Configure:

1. **E-mail Remetente**: Altere em `enviar_email.py` (linha 13)
2. **E-mail Destinatário**: Altere em `enviar_email.py` (linha 14)
3. **Senha de App**: Configure no arquivo `.env`

## 🔧 Tecnologias Utilizadas

- **Python 3**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **Selenium**: Web scraping automatizado
- **Prefect**: Orquestração de workflows e logging
- **XlsxWriter**: Geração de arquivos Excel formatados
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **smtplib**: Envio de e-mails

## 📝 Fontes de Dados

Os dados são extraídos dos seguintes sites:
- Brasil: https://www.apinfo2.com/apinfo/informacao/p12sal-br.cfm
- São Paulo: https://www.apinfo2.com/apinfo/informacao/p25sal-sp.cfm

## ⚠️ Observações Importantes

- O arquivo `.env` contém informações sensíveis e **não deve ser versionado**
- Os caminhos dos arquivos estão configurados para o ambiente local e devem ser ajustados
- O web scraping é executado em modo headless (sem interface gráfica)
- Em caso de falha no fluxo, um e-mail de erro é enviado automaticamente

## 🐛 Tratamento de Erros

O sistema possui tratamento de erros integrado:
- Erros durante a execução do fluxo disparam notificação por e-mail via `enviar_email_erro_fluxo.py`
- Logs detalhados são gerados pelo Prefect para debugging
- Validações de existência de arquivos antes do processamento

## 📄 Licença

Este é um projeto interno para análise de mercado de TI.

---
