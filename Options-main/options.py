import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from pandas.tseries.offsets import BDay
from datetime import datetime
import time
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import math
import scipy.stats as stats
from scipy.stats import norm
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
import io  
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, timedelta
import scipy.stats as si


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.subplots as sp
import streamlit as st

# Função para carregar e transformar os dados
@st.cache
def load_and_transform_data(file_path):
    df = pd.read_excel(file_path)
    
    df['Oferta Moeda Brasileira - M2'] = df['Oferta Moeda Brasileira - M2'] / 1000
    df['Juros Brasileiros(%)'] = df['Juros Brasileiros(%)'] / 100
    df['Juros Americanos(%)'] = df['Juros Americanos(%)'] / 100

    df_transformed = df.copy()
    df_transformed['Razao_Juros'] = df['Juros Americanos(%)'] / df['Juros Brasileiros(%)']
    df_transformed['Log_Razao_Juros'] = np.log(df_transformed['Razao_Juros'])
    df_transformed['Dif_Prod_Industrial'] = df['Prod Industrial Americana'] - df['Prod Industrial brasileira']
    df_transformed['Dif_Oferta_Moeda'] = df['Oferta Moeda Americana - M2'] - df['Oferta Moeda Brasileira - M2']

    df_transformed = df_transformed[['Data', 'Log_Razao_Juros', 'Dif_Prod_Industrial', 'Dif_Oferta_Moeda', 'Taxa de Câmbio']]
    df_transformed.set_index('Data', inplace=True)

    return df_transformed

# Função para prever a taxa de câmbio com base nas premissas do usuário
def prever_taxa_cambio(model, juros_br, juros_eua, prod_ind_br, prod_ind_eua, oferta_moeda_br, oferta_moeda_eua):
    razao_juros = juros_eua / juros_br
    log_razao_juros = np.log(razao_juros)
    dif_prod_industrial = prod_ind_eua - prod_ind_br
    dif_oferta_moeda = oferta_moeda_eua - (oferta_moeda_br / 1000)
    X_novo = np.array([[log_razao_juros, dif_prod_industrial, dif_oferta_moeda]])
    taxa_cambio_prevista = model.predict(X_novo)
    return taxa_cambio_prevista[0]

# Função principal
def regressaoDolar():

    st.title("Previsão da Taxa de Câmbio")
    st.write("Insira as premissas abaixo e clique em 'Gerar Regressão' para prever a taxa de câmbio.")

    # Inputs do usuário
    juros_br_proj = st.number_input("Taxa de Juros Brasileira (%)", value=10.56) / 100
    juros_eua_proj = st.number_input("Taxa de Juros Americana (%)", value=5.33) / 100
    prod_ind_br_proj = st.number_input("Produção Industrial Brasileira", value=103.8)
    prod_ind_eua_proj = st.number_input("Produção Industrial Americana", value=103.3)
    oferta_moeda_br_proj = st.number_input("Oferta de Moeda Brasileira - M2 (em milhões)", value=5014000)
    oferta_moeda_eua_proj = st.number_input("Oferta de Moeda Americana - M2 (em bilhões)", value=20841)

    # Botão para gerar a regressão
    if st.button("Gerar Regressão"):
        df_transformed = load_and_transform_data('dadosReg.xls')

        X = df_transformed[['Log_Razao_Juros', 'Dif_Prod_Industrial', 'Dif_Oferta_Moeda']]
        y = df_transformed['Taxa de Câmbio']

        model = LinearRegression()
        model.fit(X, y)

        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        coefficients = model.coef_
        intercept = model.intercept_

        X_with_const = sm.add_constant(X)
        model_sm = sm.OLS(y, X_with_const).fit()
        p_values = model_sm.pvalues
        feature_importance = np.abs(coefficients)


        taxa_cambio_prevista = prever_taxa_cambio(model, juros_br_proj, juros_eua_proj, prod_ind_br_proj, prod_ind_eua_proj, oferta_moeda_br_proj, oferta_moeda_eua_proj)
        st.write(f'Taxa de câmbio prevista: {taxa_cambio_prevista:.4f}')

        # Visualizando a matriz de correlação
        df_with_target = X.copy()
        df_with_target['Taxa de Câmbio'] = y
        corr_matrix = df_with_target.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
        st.pyplot(fig)

        # Gráficos de dispersão
        fig = sp.make_subplots(rows=1, cols=3, subplot_titles=["Log_Razao_Juros vs Taxa de Câmbio", "Dif_Prod_Industrial vs Taxa de Câmbio", "Dif_Oferta_Moeda vs Taxa de Câmbio"])

        scatter1 = go.Scatter(x=df_with_target['Log_Razao_Juros'], y=df_with_target['Taxa de Câmbio'], mode='markers', name='Log_Razao_Juros vs Taxa de Câmbio')
        fig.add_trace(scatter1, row=1, col=1)
        scatter2 = go.Scatter(x=df_with_target['Dif_Prod_Industrial'], y=df_with_target['Taxa de Câmbio'], mode='markers', name='Dif_Prod_Industrial vs Taxa de Câmbio')
        fig.add_trace(scatter2, row=1, col=2)
        scatter3 = go.Scatter(x=df_with_target['Dif_Oferta_Moeda'], y=df_with_target['Taxa de Câmbio'], mode='markers', name='Dif_Oferta_Moeda vs Taxa de Câmbio')
        fig.add_trace(scatter3, row=1, col=3)

        fig.update_layout(height=400, width=1200, title_text="Gráficos de Dispersão: Taxa de Câmbio vs Variáveis Remanescentes")
        st.plotly_chart(fig)

        # Gráfico com valor predito e valor real
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_transformed.index, y=y, mode='lines', name='Valor Real'))
        fig.add_trace(go.Scatter(x=df_transformed.index, y=y_pred, mode='lines', name='Valor Predito'))

        fig.update_layout(title='Valor Real vs Valor Predito', xaxis_title='Data', yaxis_title='Taxa de Câmbio')
        st.plotly_chart(fig)









@st.cache_data
def load_dados():
    df = pd.read_excel('Historico Impurezas.xlsx')
    df = df.dropna()
    df['Impureza Total'] = df['Impureza Vegetal'] + df['Impureza Mineral']
    return df

def treinar_modelos(df):
    X = df[['Impureza Total', 'Pureza', 'Preciptação']]
    y = df['ATR']
    
    models = {
        "Regressão Linear": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Ridge": Ridge(alpha=1.0)
    }
    
    resultados = {}
    for nome, model in models.items():
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        resultados[nome] = {'model': model, 'R²': r2, 'RMSE': rmse, 'y_pred': y_pred}
    
    return resultados

def calcular_pureza_necessaria(ATR_desejado, estimativa_precipitacao, estimativa_impurezas, model):
    coef = model.coef_
    intercept = model.intercept_
    pureza_necessaria = (ATR_desejado - intercept - coef[0] * estimativa_impurezas - coef[2] * estimativa_precipitacao) / coef[1]
    return pureza_necessaria

def plotar_graficos_dispersao(df):
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Impureza Total vs ATR', 'Pureza vs ATR', 'Preciptação vs ATR'))
    
    fig.add_trace(go.Scatter(x=df['Impureza Total'], y=df['ATR'], mode='markers', marker=dict(color='blue'), name='Impureza Total vs ATR'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Pureza'], y=df['ATR'], mode='markers', marker=dict(color='red'), name='Pureza vs ATR'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['Preciptação'], y=df['ATR'], mode='markers', marker=dict(color='green'), name='Preciptação vs ATR'), row=1, col=3)
    
    fig.update_layout(
        title_text='Gráficos de Dispersão Comparativos',
        height=600,
        width=1200,
        showlegend=False
    )
    
    st.plotly_chart(fig)

def plotar_heatmap(df):
    cols = ['ATR', 'Impureza Total', 'Pureza', 'Preciptação']
    corr = df[cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, annot_kws={"size": 8}, cbar_kws={"shrink": 0.8})
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    st.pyplot(fig)

def atr():
    st.title("Análise de ATR e Impurezas")
    
    df = load_dados()
    
    ATR_desejado = st.number_input("ATR Desejado:", min_value=0.0, value=130.0)
    estimativa_precipitacao = st.number_input("Estimativa de Preciptação:", min_value=0.0, value=100.0)
    estimativa_impurezas = st.number_input("Estimativa de Impurezas Totais:", min_value=0.0, value=18.0)
    
    if st.button("Calcular"):
        resultados = treinar_modelos(df)
        
        st.subheader("Resultados dos Modelos")
        for nome, resultado in resultados.items():
            st.write(f"**{nome}** - R²: {resultado['R²']:.2f}, RMSE: {resultado['RMSE']:.2f}")
        
        model_lr = resultados["Regressão Linear"]['model']
        pureza_necessaria = calcular_pureza_necessaria(ATR_desejado, estimativa_precipitacao, estimativa_impurezas, model_lr)
        st.write(f'Para alcançar um ATR de {ATR_desejado}, com preciptação de {estimativa_precipitacao} e impurezas totais de {estimativa_impurezas}, é necessário uma pureza de aproximadamente {pureza_necessaria:.2f}.')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['ATR'], mode='lines', name='Real', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=resultados['Random Forest']['y_pred'], mode='lines', name='Predito Random Forest', line=dict(dash='dash')))
        fig.update_layout(title='Valores Reais vs Preditos do ATR', xaxis_title='Índice', yaxis_title='ATR')
        st.plotly_chart(fig)
        
        st.subheader("Gráficos de Dispersão Comparativos")
        plotar_graficos_dispersao(df)
        
        st.subheader("Heatmap de Correlação")
        plotar_heatmap(df)
        
        st.subheader("Explicabilidade das Variáveis")
        st.markdown("""
        <span style='color: red'>Explicabilidade de 'Impureza Total': baixa</span><br>
        <span style='color: green'>Explicabilidade de 'Pureza': alta</span><br>
        <span style='color: yellow'>Explicabilidade de 'Preciptação': moderada</span>
        """, unsafe_allow_html=True)







def calcular_var(data, n_days, current_price, z_score):
    data['Returns'] = data['Adj Close'].pct_change()
    lambda_ = 0.94
    data['EWMA_Vol'] = data['Returns'].ewm(span=(2/(1-lambda_)-1)).std()
    data['Annualized_EWMA_Vol'] = data['EWMA_Vol'] * np.sqrt(n_days)
    VaR_EWMA = z_score * data['Annualized_EWMA_Vol'].iloc[-1] * current_price
    price_at_risk = current_price + VaR_EWMA
    mean_returns = data['Returns'].mean()
    std_returns = data['Returns'].std()
    return VaR_EWMA, price_at_risk, mean_returns, std_returns

def calcular_dias_uteis(data_inicio, data_fim):
    dias_uteis = np.busday_count(data_inicio.date(), data_fim.date())
    return dias_uteis

def VaR():
    st.title("Análise de Risco")

    escolha = st.selectbox('Selecione o ativo:', ['USDBRL=X', 'SB=F'])

    data = yf.download(escolha, start='2013-01-01', end='2025-01-01')

    
    current_price = data['Adj Close'][-1]

    data_fim = st.date_input('Selecione a data final:', datetime.now())
    n_days = calcular_dias_uteis(data.index[-1], data_fim)

    # Input para selecionar o nível de confiança
    confianca = st.slider('Selecione o nível de confiança (%):', min_value=90, max_value=99, step=1)
    z_score = norm.ppf((100 - confianca) / 100)  # Calcula o z-score correspondente ao nível de confiança

    if st.button('Calcular'):
        data = data[data.index >= '2013-01-01']
        VaR_EWMA, price_at_risk, mean_returns, std_returns = calcular_var(data, n_days, current_price, z_score)

        # Exibir KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("VaR", f"{VaR_EWMA:.2f}")
        col2.metric("Preço em risco", f"{price_at_risk:.2f}")
        col3.metric("Média dos Retornos Diários", f"{mean_returns:.2%}")
        col4.metric("Volatilidade Histórica Diária", f"{std_returns:.2%}")
        col5.metric("Z-Score Utilizado", f"{z_score:.2f}")

        # Gráfico de distribuição
        hist_data = data['Returns'].dropna()
        hist, bins = np.histogram(hist_data, bins=100, density=True)
        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        pdf = 1/(std_returns * np.sqrt(2 * np.pi)) * np.exp(-(bin_centers - mean_returns)**2 / (2 * std_returns**2))

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=hist_data, nbinsx=100, name='Histograma', histnorm='probability density'))
        fig.add_trace(go.Scatter(x=bin_centers, y=pdf, mode='lines', name='Distribuição Normal', line=dict(color='red')))

        st.plotly_chart(fig)

import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# Função para realizar a simulação Monte Carlo
def simulacao_monte_carlo_alternativa(valores_medios, perc_15, perc_85, num_simulacoes):    
    faturamentos = []
    custos = []

    for _ in range(num_simulacoes):
        # Gerar valores aleatórios para cada variável de acordo com a distribuição normal
        moagem_total_simulado = np.random.normal(valores_medios['Moagem Total']['Valor Médio'], (perc_85['Moagem Total']['Percentil 85'] - perc_15['Moagem Total']['Percentil 15']) / 2, 1)[0]
        atr_simulado = np.random.normal(valores_medios['ATR']['Valor Médio'], (perc_85['ATR']['Percentil 85'] - perc_15['ATR']['Percentil 15']) / 2, 1)[0]
        vhp_total_simulado = np.random.normal(valores_medios['VHP Total']['Valor Médio'], (perc_85['VHP Total']['Percentil 85'] - perc_15['VHP Total']['Percentil 15']) / 2, 1)[0]
        ny_simulado = np.random.normal(valores_medios['NY']['Valor Médio'], (perc_85['NY']['Percentil 85'] - perc_15['NY']['Percentil 15']) / 2, 1)[0]
        cambio_simulado = np.random.normal(valores_medios['Câmbio']['Valor Médio'], (perc_85['Câmbio']['Percentil 85'] - perc_15['Câmbio']['Percentil 15']) / 2, 1)[0]
        preco_cbios_simulado = np.random.normal(valores_medios['Preço CBIOS']['Valor Médio'], (perc_85['Preço CBIOS']['Percentil 85'] - perc_15['Preço CBIOS']['Percentil 15']) / 2, 1)[0]
        preco_etanol_simulado = np.random.normal(valores_medios['Preço Etanol']['Valor Médio'], (perc_85['Preço Etanol']['Percentil 85'] - perc_15['Preço Etanol']['Percentil 15']) / 2, 1)[0]

        # Calcular o faturamento líquido com os valores simulados
        faturamento_simulado = calcular_faturamento(vhp_total_simulado, ny_simulado, cambio_simulado, preco_cbios_simulado, preco_etanol_simulado)
        faturamentos.append(faturamento_simulado)

        # Calcular o custo com os valores simulados
        custo_simulado = calcular_custo(faturamento_simulado, moagem_total_simulado, atr_simulado, preco_cbios_simulado)
        custos.append(custo_simulado)

    return faturamentos, custos

# Função para calcular o faturamento líquido
def calcular_faturamento(vhp_total, ny, cambio, preco_cbios, preco_etanol):
    acucar = ((ny - 0.19) * 22.0462 * 1.04 * cambio) * vhp_total + 17283303
    etanol = preco_etanol * 35524
    cjm = 24479549
    cbios = preco_cbios * 31616
    return acucar + etanol + cjm + cbios

# Função para calcular o custo
def calcular_custo(faturamento, moagem_total, atr, preco_cbios):
    atr_mtm = 0.6 * (faturamento - preco_cbios) / (moagem_total * atr)
    cana_acucar_atr = atr_mtm * moagem_total * atr
    gastos_variaveis = 32947347 + cana_acucar_atr
    gastos_fixos =  109212811 
    return gastos_fixos + gastos_variaveis

# Função para plotar o histograma
def plot_histograma(resultados, titulo, cor):
    plt.figure(figsize=(10, 6))
    sns.histplot(resultados, bins=50, kde=True, color=cor)
    plt.xlabel('Valor (R$)')
    plt.ylabel('Frequência')
    plt.title(titulo)
    plt.grid(True)
    plt.xticks(np.arange(200_000_000, 600_000_001, 100_000_000))
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: 'R$ {:,.0f}M'.format(x/1_000_000)))
    plt.tight_layout()
    st.pyplot()

# Função principal para a página "Risco"
def risco():
    st.title("IBEA - Simulações de Desempenho SF 2024/2025")

    st.subheader("Premissas Assumidas")
    premissas = [
        "Moagem",
        "ATR",
        "Prod VHP (Inclui CJM)",
        "Prod Etanol",
        "Dólar",
        "Preço Açúcar",
        "Preço Etanol",
        "Gastos Fixos",
        "Gastos Cana (Variável)"
    ]
    st.write(premissas)

    st.subheader("Orçamento Base")
    orcamento_base = [
        "Faturamento",
        "Custos Cana",
        "Custo Fixo",
        "Ebtida",
        "Margem Cana %"
    ]
    st.write(orcamento_base)

    st.subheader("Inputs")
    st.write("Por favor, insira os seguintes valores médios, percentil 15 e percentil 85:")

    inputs = {
        'Moagem Total': {'Valor Médio': st.sidebar.number_input('Moagem Total - Valor Médio', value=1300000), 'Percentil 15': st.sidebar.number_input('Moagem Total - Percentil 15', value=1100000), 'Percentil 85': st.sidebar.number_input('Moagem Total - Percentil 85', value=1500000)},
        'ATR': {'Valor Médio': st.sidebar.number_input('ATR - Valor Médio', value=125), 'Percentil 15': st.sidebar.number_input('ATR - Percentil 15', value=120), 'Percentil 85': st.sidebar.number_input('ATR - Percentil 85', value=130)},
        'VHP Total': {'Valor Médio': st.sidebar.number_input('VHP Total - Valor Médio', value=97000), 'Percentil 15': st.sidebar.number_input('VHP Total - Percentil 15', value=94000), 'Percentil 85': st.sidebar.number_input('VHP Total - Percentil 85', value=100000)},
        'NY': {'Valor Médio': st.sidebar.number_input('NY - Valor Médio', value=21), 'Percentil 15': st.sidebar.number_input('NY - Percentil 15', value=18), 'Percentil 85': st.sidebar.number_input('NY - Percentil 85', value=24)},
        'Câmbio': {'Valor Médio': st.sidebar.number_input('Câmbio - Valor Médio', value=5.1), 'Percentil 15': st.sidebar.number_input('Câmbio - Percentil 15', value=4.9), 'Percentil 85': st.sidebar.number_input('Câmbio - Percentil 85', value=5.3)},
        'Preço CBIOS': {'Valor Médio': st.sidebar.number_input('Preço CBIOS - Valor Médio', value=90), 'Percentil 15': st.sidebar.number_input('Preço CBIOS - Percentil 15', value=75), 'Percentil 85': st.sidebar.number_input('Preço CBIOS - Percentil 85', value=105)},
        'Preço Etanol': {'Valor Médio': st.sidebar.number_input('Preço Etanol - Valor Médio', value=3000), 'Percentil 15': st.sidebar.number_input('Preço Etanol - Percentil 15', value=2500), 'Percentil 85': st.sidebar.number_input('Preço Etanol - Percentil 85', value=3500)}
    }

    for variavel, valores in inputs.items():
        st.write(f"{variavel} - Valor Médio:", valores['Valor Médio'], "\t", f"{variavel} - Percentil 15:", valores['Percentil 15'], "\t", f"{variavel} - Percentil 85:", valores['Percentil 85'])

    # Botão para simular
    if st.button("Simular"):
        # Realizar a simulação Monte Carlo
        num_simulacoes = 1000000
        faturamentos, custos = simulacao_monte_carlo_alternativa(inputs, inputs, inputs, num_simulacoes)

        # Plotar o histograma do faturamento
        st.subheader("Faturamento")
        plot_histograma(faturamentos, "Distribuição de Frequência do Faturamento Total", "skyblue")

        # Calcular os percentis e faturamento médio
        percentis_desejados = [1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 85, 90, 95, 98, 99]
        valores_percentis = {p: np.percentile(faturamentos, p) for p in percentis_desejados}
        faturamento_medio = np.mean(faturamentos)

        st.markdown("**Faturamento Médio:** R$ <span style='color:green'>{:.2f}</span>".format(round(faturamento_medio, 2)), unsafe_allow_html=True)
        st.subheader("Tabela de Percentis e Valores Correspondentes para Faturamento")
        st.write("| Percentil | Faturamento |")
        st.write("|-----------|-------------|")
        for percentil in percentis_desejados:
            st.write(f"| {percentil}% | R$ {valores_percentis[percentil]:,.2f} |")

        # Plotar o histograma dos custos
        st.subheader("Custo")
        plot_histograma(custos, "Distribuição de Frequência do Custo Total", "orange")

        # Calcular os percentis e custo médio
        valores_percentis_custos = {p: np.percentile(custos, p) for p in percentis_desejados}
        custo_medio = np.mean(custos)

        st.markdown("**Custo Médio:** R$ <span style='color:red'>{:.2f}</span>".format(round(custo_medio, 2)), unsafe_allow_html=True)
        st.subheader("Tabela de Percentis e Valores Correspondentes para Custos")
        st.write("| Percentil | Custo |")
        st.write("|-----------|-------|")
        for percentil in percentis_desejados:
            st.write(f"| {percentil}% | R$ {valores_percentis_custos[percentil]:,.2f} |")

        # Calcular Ebtida Ajustado
        ebtida_ajustado = [faturamento - custo + 7219092 for faturamento, custo in zip(faturamentos, custos)]

        # Plotar o histograma do Ebtida Ajustado
        st.subheader("Ebtida Ajustado")
        plot_histograma(ebtida_ajustado, "Distribuição de Frequência do Ebtida Ajustado", "lightgreen")
        # Definindo os x-ticks específicos para o gráfico do Ebtida Ajustado
        plt.xticks(np.arange(-30000000, 85000001, 15000000))
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: 'R$ {:,.0f}M'.format(x/1000000)))

        # Calcular os percentis e o Ebtida Ajustado médio
        valores_percentis_ebtida_ajustado = {p: np.percentile(ebtida_ajustado, p) for p in percentis_desejados}
        ebtida_ajustado_medio = np.mean(ebtida_ajustado)

        st.markdown("**Ebtida Ajustado Médio:** R$ <span style='color:blue'>{:.2f}</span>".format(round(ebtida_ajustado_medio, 2)), unsafe_allow_html=True)
        st.subheader("Tabela de Percentis e Valores Correspondentes para Ebtida Ajustado")
        st.write("| Percentil | Ebtida Ajustado |")
        st.write("|-----------|-----------------|")
        for percentil in percentis_desejados:
            st.write(f"| {percentil}% | R$ {valores_percentis_ebtida_ajustado[percentil]:,.2f} |")

        # Calcular a influência média do preço do VHP, Etanol e Dólar sobre o faturamento
        influencia_media_vhp = (inputs['VHP Total']['Valor Médio'] * 97000) / faturamento_medio * 100
        influencia_media_etanol = (inputs['Preço Etanol']['Valor Médio'] * 35524) / faturamento_medio * 100
        influencia_media_dolar = (inputs['NY']['Valor Médio'] * 22.0462 * 1.04 * inputs['Câmbio']['Valor Médio']) / faturamento_medio * 100

        # Criar DataFrame com as informações de influência média
        df_influencia_media = pd.DataFrame({
            'Variável': ['Preço VHP', 'Preço Etanol', 'Dólar'],
            'Influência Média (%)': [influencia_media_vhp, influencia_media_etanol, influencia_media_dolar]
        })

        # Mostrar DataFrame
        st.subheader("Influência Média sobre o Faturamento")
        st.write(df_influencia_media)









import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText

def calcular_MACD(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, min_periods=1, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, min_periods=1, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, min_periods=1, adjust=False).mean()
    histograma = macd - signal_line
    return macd, signal_line, histograma

def calcular_CCI(data, window=20):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    mean_deviation = typical_price.rolling(window=window).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    cci = (typical_price - typical_price.rolling(window=window).mean()) / (0.015 * mean_deviation)
    return cci

def calcular_estocastico(data, window=14):
    low_min = data['Low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    stoch = ((data['Close'] - low_min) / (high_max - low_min)) * 100
    return stoch

def calcular_estocastico_lento(data, window=14, smooth_k=3):
    stoch = calcular_estocastico(data, window)
    stoch_slow = stoch.rolling(window=smooth_k).mean()
    return stoch_slow

def calcular_volatilidade_ewma_percentual(retornos_diarios_absolutos, span=20):
    return (retornos_diarios_absolutos.ewm(span=span).std()) * 100

def calcular_bollinger_bands(data, window=20, num_std_dev=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    data['Bollinger High'] = rolling_mean + (rolling_std * num_std_dev)
    data['Bollinger Low'] = rolling_mean - (rolling_std * num_std_dev)
    return data

def calcular_RSI(data, window=14):
    delta = data['Close'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = ganho / perda
    rsi = 100 - (100 / (1 + rs))
    return rsi


def enviar_alerta(email, ativo, cci_status, rsi_status, estocastico_status, bb_status):
    # Configurar servidor SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "guilherme.araujo.0798@gmail.com"
    sender_password = "12345678"

    # Conteúdo do e-mail
    message = f"""
    Alerta para o ativo {ativo}:

    CCI: {cci_status}
    RSI: {rsi_status}
    Estocástico: {estocastico_status}
    Bandas de Bollinger: {bb_status}
    """
    msg = MIMEText(message)
    msg['Subject'] = f"Alerta de Mercado - {ativo}"
    msg['From'] = sender_email
    msg['To'] = email

    # Enviar e-mail
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        st.success(f"Alerta enviado para {email}")
    except Exception as e:
        st.error(f"Erro ao enviar o e-mail: {e}")

def mercado():
    st.title("Mercado")

    ativo = st.selectbox("Selecione o ativo", ["SBV24.NYB", "SBH25.NYB", "USDBRL=X", "SB=F"])

    data = yf.download(ativo, start="2014-01-01", end="2024-12-12")

    filtro_datas = st.sidebar.date_input("Selecione um intervalo de datas:", value=[pd.to_datetime('2023-01-01'), pd.to_datetime('2025-01-01')])
    filtro_datas = [pd.Timestamp(date) for date in filtro_datas]

    indicador_selecionado = st.selectbox("Selecione o indicador", ["EWMA", "CCI", "Estocástico", "Bandas de Bollinger", "MACD", "RSI"])

    if indicador_selecionado == "CCI":
        sobrecompra = st.slider("Selecione o nível de sobrecompra do CCI", 100, 250, step=50, value=100)

    if st.button("Calcular"):
        data_filtrado = data[(data.index >= filtro_datas[0]) & (data.index <= filtro_datas[1])]

        # Inicialização das variáveis para KPIs
        quantidade_entradas = 0
        soma_fechamentos_entradas = 0

        if indicador_selecionado == "EWMA":
            data_filtrado['Daily Returns'] = data_filtrado['Close'].pct_change()
            data_filtrado['EWMA Volatility'] = calcular_volatilidade_ewma_percentual(data_filtrado['Daily Returns'])
            data_filtrado.dropna(subset=['Daily Returns', 'EWMA Volatility'], inplace=True)
            data_filtrado['Abs Daily Returns'] = data_filtrado['Daily Returns'].abs() * 100
            data_filtrado['Entry Points'] = data_filtrado['Daily Returns'] * 100 > data_filtrado['EWMA Volatility']

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Abs Daily Returns'], mode='lines', name='Retornos Diários Absolutos'))
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['EWMA Volatility'], mode='lines', name='Volatilidade EWMA'))
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Abs Daily Returns'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Retornos Diários Absolutos & Volatilidade EWMA', xaxis_title='Data', yaxis_title='Valor')
            st.plotly_chart(fig)

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Close'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Preço de Fechamento com Pontos de Entrada', xaxis_title='Data', yaxis_title='Preço de Fechamento')
            st.plotly_chart(fig)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['EWMA Volatility'], mode='lines', name='Volatilidade EWMA'))
            fig.update_layout(title='Volatilidade EWMA', xaxis_title='Data', yaxis_title='Volatilidade')
            st.plotly_chart(fig)

            # Criar arquivo Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                data_ewma = data_filtrado[['Close', 'Abs Daily Returns', 'EWMA Volatility']].reset_index()
                data_ewma.to_excel(writer, sheet_name='EWMA', index=False)

            excel_buffer.seek(0)
            st.download_button(
                label="Baixar Arquivo Excel",
                data=excel_buffer,
                file_name="dados_ewma.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


        elif indicador_selecionado == "CCI":
            data_filtrado['CCI'] = calcular_CCI(data_filtrado)
            data_filtrado['Entry Points'] = (data_filtrado['CCI'] > sobrecompra) & \
                                            (data_filtrado['CCI'].shift(-1) < data_filtrado['CCI']) & \
                                            (data_filtrado['CCI'].shift(1) < data_filtrado['CCI'])

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Close'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Preço de Fechamento com Pontos de Entrada', xaxis_title='Data', yaxis_title='Preço de Fechamento')
            st.plotly_chart(fig)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['CCI'], mode='lines', name='CCI'))
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['CCI'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='CCI', xaxis_title='Data', yaxis_title='Valor do CCI')
            st.plotly_chart(fig)

        elif indicador_selecionado == "Estocástico":
            data_filtrado['Estocástico'] = calcular_estocastico_lento(data_filtrado)
            data_filtrado['Entry Points'] = (data_filtrado['Estocástico'] > 80) & \
                                            (data_filtrado['Estocástico'].shift(-1) < data_filtrado['Estocástico']) & \
                                            (data_filtrado['Estocástico'].shift(1) < data_filtrado['Estocástico'])

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Close'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Preço de Fechamento com Pontos de Entrada', xaxis_title='Data', yaxis_title='Preço de Fechamento')
            st.plotly_chart(fig)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Estocástico'], mode='lines', name='Estocástico'))
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Estocástico'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Estocástico', xaxis_title='Data', yaxis_title='Valor do Estocástico')
            st.plotly_chart(fig)

        elif indicador_selecionado == "Bandas de Bollinger":
            data_filtrado = calcular_bollinger_bands(data_filtrado)
            data_filtrado['Entry Points'] = (data_filtrado['Close'] > data_filtrado['Bollinger High']) & (data_filtrado['Close'].shift(-1) < data_filtrado['Close'])

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            
            # Adiciona a linha da média móvel
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Close'].rolling(window=20).mean(), mode='lines', name='Média Móvel', line=dict(color='orange')))

            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Bollinger High'], mode='lines', name='Bollinger High'))
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Bollinger Low'], mode='lines', name='Bollinger Low'))

            # Adiciona uma área azul translúcida entre as bandas superior e inferior
            fig.add_trace(go.Scatter(
                x=data_filtrado.index.tolist() + data_filtrado.index[::-1].tolist(),
                y=data_filtrado['Bollinger High'].tolist() + data_filtrado['Bollinger Low'][::-1].tolist(),
                fill='toself',
                fillcolor='rgba(173, 216, 230, 0.3)',  # cor azul translúcida
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
            ))

            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Close'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Bandas de Bollinger', xaxis_title='Data', yaxis_title='Preço de Fechamento')
            st.plotly_chart(fig)


        elif indicador_selecionado == "MACD":
            data_filtrado = calcular_MACD(data_filtrado)
            data_filtrado['Entry Points'] = (data_filtrado['MACD'] > data_filtrado['Signal Line']) & (data_filtrado['MACD'].shift(-1) < data_filtrado['Signal Line'].shift(-1))

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['MACD'], mode='lines', name='MACD'))
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['Signal Line'], mode='lines', name='Signal Line'))
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['MACD'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='MACD', xaxis_title='Data', yaxis_title='Valor')
            st.plotly_chart(fig)

        elif indicador_selecionado == "RSI":
            data_filtrado['RSI'] = calcular_RSI(data_filtrado)
            data_filtrado['Entry Points'] = (data_filtrado['RSI'] > 70) & (data_filtrado['RSI'].shift(-1) < data_filtrado['RSI'])

            quantidade_entradas = data_filtrado['Entry Points'].sum()
            if quantidade_entradas > 0:
                soma_fechamentos_entradas = data_filtrado[data_filtrado['Entry Points']]['Close'].mean()

            fig = go.Figure(data=[go.Candlestick(x=data_filtrado.index,
                                                 open=data_filtrado['Open'],
                                                 high=data_filtrado['High'],
                                                 low=data_filtrado['Low'],
                                                 close=data_filtrado['Close'],
                                                 increasing_line_color='green',
                                                 decreasing_line_color='red')])
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['Close'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='Preço de Fechamento com Pontos de Entrada', xaxis_title='Data', yaxis_title='Preço de Fechamento')
            st.plotly_chart(fig)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_filtrado.index, y=data_filtrado['RSI'], mode='lines', name='RSI'))
            entry_points = data_filtrado[data_filtrado['Entry Points']]
            fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points['RSI'], mode='markers', marker=dict(color='blue', symbol='x', size=10), name='Pontos de Entrada'))
            fig.update_layout(title='RSI', xaxis_title='Data', yaxis_title='Valor do RSI')
            st.plotly_chart(fig)

        # Calcular média de todos os candles (fechamento)
        media_fechamentos = data_filtrado['Close'].mean()

        # Formatar os KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Quantidade de Entradas", quantidade_entradas, "")
        col2.metric("Média dos Fechamentos das Entradas", f"{soma_fechamentos_entradas:.2f}", "")
        col3.metric("Média de Todos os Candles (Fechamento)", f"{media_fechamentos:.2f}", "")

        st.write("")


        # Botão para gerar alerta
        st.write("")
        gerar_alerta = st.checkbox("Gerar Alerta")
        if gerar_alerta:
            email = st.text_input("Digite seu e-mail para receber o alerta")
            if email:
                cci_status = "Normal"
                rsi_status = "Normal"
                estocastico_status = "Normal"
                bb_status = "Normal"

                if data_filtrado['CCI'].iloc[-1] > sobrecompra:
                    cci_status = "Sobrecomprado"
                elif data_filtrado['CCI'].iloc[-1] < -100:
                    cci_status = "Sobrevendido"

                if data_filtrado['RSI'].iloc[-1] > 70:
                    rsi_status = "Sobrecomprado"
                elif data_filtrado['RSI'].iloc[-1] < 30:
                    rsi_status = "Sobrevendido"

                if data_filtrado['Estocástico'].iloc[-1] > 80:
                    estocastico_status = "Sobrecomprado"
                elif data_filtrado['Estocástico'].iloc[-1] < 20:
                    estocastico_status = "Sobrevendido"

                if data_filtrado['Close'].iloc[-1] > data_filtrado['Bollinger High'].iloc[-1]:
                    bb_status = "Sobrecomprado"
                elif data_filtrado['Close'].iloc[-1] < data_filtrado['Bollinger Low'].iloc[-1]:
                    bb_status = "Sobrevendido"

                enviar_alerta(email, ativo, cci_status, rsi_status, estocastico_status, bb_status)







# Função para calcular o número de dias úteis entre duas datas
def calcular_dias_uteis(data_inicial, data_final):
    datas_uteis = pd.date_range(start=data_inicial, end=data_final, freq=BDay())
    return len(datas_uteis)

# Função para simulação Monte Carlo
def simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior):
    retornos_diarios_simulados = np.random.normal(media_retornos_diarios, desvio_padrao_retornos_diarios, (dias_simulados, num_simulacoes))

    preco_inicial = data['Close'].iloc[-1]
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial

    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_diarios_simulados[dia - 1, :])
        precos_simulados[dia, :] = np.maximum(np.minimum(precos_simulados[dia, :], limite_superior), limite_inferior)

    return precos_simulados[1:, :]

# Função para a interface gráfica da aba do Monte Carlo
def monte_carlo():
    st.title("Simulação Monte Carlo de Preços")

    # Selecionar o tipo de ativo
    tipo_ativo = st.selectbox("Selecione o tipo de ativo", ["Açúcar", "Dólar"])

    # Carregar dados do Yahoo Finance correspondente ao tipo de ativo selecionado
    if tipo_ativo == "Açúcar":
        ativo = "SB=F"
    elif tipo_ativo == "Dólar":
        ativo = "USDBRL=X"

    data = yf.download(ativo, start="2013-01-01", end="2025-01-01")

    # Calcular média e desvio padrão dos retornos diários
    data['Daily Return'] = data['Close'].pct_change()
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()

    # Selecionar a data para simulação
    data_simulacao = st.date_input("Selecione a data para simulação", value=pd.to_datetime('2024-12-31'))

    # Calcular o número de dias úteis até a data de simulação
    hoje = pd.to_datetime('today').date()
    dias_simulados = calcular_dias_uteis(hoje, data_simulacao)

    # Input para o valor desejado para a simulação
    valor_simulado = st.number_input("Qual valor deseja simular?", min_value=data['Close'].min(), max_value=data['Close'].max(), step=0.01)

    # Definir limites inferior e superior
    limite_inferior = data['Close'].iloc[-1] - 10
    limite_superior = data['Close'].iloc[-1] + 10

    # Simulação Monte Carlo
    num_simulacoes = 1000000
    simulacoes = simulacao_monte_carlo(data, media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior)

    if st.button("Simular"):
        # Restante do código para a simulação Monte Carlo...

        # Calculando os outputs
        media_simulada = np.mean(simulacoes[-1])
        percentil_20 = np.percentile(simulacoes[-1], 20)
        percentil_80 = np.percentile(simulacoes[-1], 80)
        prob_acima_valor = np.mean(simulacoes[-1] > valor_simulado) * 100
        prob_abaixo_valor = np.mean(simulacoes[-1] < valor_simulado) * 100

        # Criar lista de figuras
        fig = go.Figure()

        # Cores para as linhas
        cores = ['rgba(31,119,180,0.3)', 'rgba(255,127,14,0.3)', 'rgba(44,160,44,0.3)', 'rgba(214,39,40,0.3)', 'rgba(148,103,189,0.3)']

        # Adicionar as simulações ao gráfico
        for i in range(100):
            fig.add_trace(go.Scatter(x=np.arange(1, dias_simulados + 1), y=simulacoes[:, i], mode='lines', line=dict(width=0.8, color=cores[i % len(cores)]), name='Simulação {}'.format(i+1)))

        # Layout do gráfico
        fig.update_layout(
            xaxis_title="Dias",
            yaxis_title="Preço de Fechamento",
            yaxis_range=[data['Close'].min() - 5, data['Close'].max() + 5],
            yaxis_gridcolor='lightgrey',
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig)

        # Exibir os outputs
        st.write("Média dos valores simulados: **{:.4f}**".format(media_simulada))
        st.write("Percentil 20: **{:.4f}**".format(percentil_20))
        st.write("Percentil 80: **{:.4f}**".format(percentil_80))
        st.write("Probabilidade do ativo estar acima do valor inserido: **{:.2f}%**".format(prob_acima_valor))
        st.write("Probabilidade do ativo estar abaixo do valor inserido: **{:.2f}%**".format(prob_abaixo_valor))

        # Gerar o histograma e a curva de densidade
        hist_data = simulacoes[-1]
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Histogram(
            x=hist_data,
            nbinsx=100,
            histnorm='probability',
            name='Histograma',
            marker_color='rgba(0, 128, 128, 0.6)',
            opacity=0.75
        ))

        fig_hist.update_layout(
            xaxis_title="Preço Simulado",
            yaxis_title="Frequência",
            yaxis_gridcolor='lightgrey',
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        # Exibir o histograma no Streamlit
        st.plotly_chart(fig_hist)

        # Calcular estatísticas
        desvio_padrao_simulado = np.std(hist_data)
        media_simulada = np.mean(hist_data)
        mediana_simulada = np.median(hist_data)

        # Exibir as estatísticas
        st.write("Desvio padrão dos valores simulados: **{:.4f}**".format(desvio_padrao_simulado))
        st.write("Média dos valores simulados: **{:.4f}**".format(media_simulada))
        st.write("Mediana dos valores simulados: **{:.4f}**".format(mediana_simulada))






# Função para plotar o heatmap das metas
def plot_heatmap(meta):
    # Preço do açúcar e do dólar
    precos_acucar = np.arange(24, 19, -0.5)
    precos_dolar = np.arange(4.8, 5.3, 0.05)

    # Calculando o produto
    produto = np.zeros((len(precos_acucar), len(precos_dolar)))

    for i, acucar in enumerate(precos_acucar):
        for j, dolar in enumerate(precos_dolar):
            produto[i, j] = 22.0462 * 1.04 * acucar * dolar - meta

    # Plotando o gráfico de calor
    plt.figure(figsize=(20, 16))  # Definindo um tamanho maior para o gráfico
    plt.imshow(produto, cmap='RdYlGn', aspect='auto')

    # Adicionando os rótulos com os valores do produto dentro dos quadrados
    for i in range(len(precos_acucar)):
        for j in range(len(precos_dolar)):
            plt.text(j, i, f'\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200bR$ {produto[i, j]:.0f}/Ton\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b', ha='center', va='center', color='white', fontsize=11.5, fontweight='bold')

    plt.colorbar(label='Produto')
    plt.xticks(np.arange(len(precos_dolar)), [f'{d:.2f}' for d in precos_dolar])
    plt.yticks(np.arange(len(precos_acucar)), [f'{a:.2f}' for a in precos_acucar])
    plt.xlabel('Preço do Dólar')
    plt.ylabel('Preço do Açúcar')
    plt.title(f'Produto = 22.0462 * 1.04 * Preço do Açúcar * Preço do Dólar - Meta: {meta}')
    st.pyplot()

# Função para calcular o MTM
def calcular_mtm(meta):
    start_date = datetime(2024, 7, 8)
    end_date = datetime(2024,7,31)

    # Obtendo os dados históricos do contrato futuro de açúcar e do par de moedas USD/BRL
    sugar_data = yf.download('SB=F', start=start_date, end=end_date)['Close']
    forex_data = yf.download('USDBRL=X', start=start_date, end=end_date)['Close']

    # Calculando o MTM para cada data
    mtm = 22.0462 * 1.04 * sugar_data * forex_data

    # Criando DataFrame pandas com o MTM
    mtm_df = pd.DataFrame({'Date': mtm.index, 'MTM': mtm.values, 'Meta': meta})
    mtm_df['Date'] = mtm_df['Date'].dt.strftime('%d/%b/%Y')
    return mtm_df

import streamlit as st
import numpy as np
import plotly.graph_objs as go

def simulacao_opcoes():
    st.title("Simulador de Opções")

    min_preco_acucar = st.number_input("Preço mínimo:", min_value=0.0, max_value=100.0, step=0.01, value=0.0)
    max_preco_acucar = st.number_input("Preço máximo:", min_value=0.0, max_value=100.0, step=0.01, value=26.0)

    num_pernas = st.number_input("Quantas pernas deseja adicionar na simulação?", min_value=1, max_value=20, value=1, step=1)

    pernas = []

    for i in range(num_pernas):
        st.header(f"Perna {i+1}")
        tipo_posicao = st.radio(f"Selecione o tipo de posição para a perna {i+1}:", ("Compra", "Venda"), key=f"posicao_{i}")
        tipo_opcao = st.radio(f"Selecione o tipo de opção para a perna {i+1}:", ("Put", "Call"), key=f"opcao_{i}")
        strike = st.number_input(f"Strike para a perna {i+1}:", min_value=0.0, max_value=100.0, step=0.01, value=20.0, key=f"strike_{i}")
        lotes = st.number_input(f"Quantidade de lotes para a perna {i+1}:", min_value=1, max_value=1000000000, step=1, value=1, key=f"lotes_{i}")

        pernas.append((tipo_posicao, tipo_opcao, strike, lotes))

    if st.button("Simular"):
        precos_acucar = np.arange(min_preco_acucar, max_preco_acucar, 0.25)
        receitas = np.zeros_like(precos_acucar)

        for perna in pernas:
            tipo_posicao, tipo_opcao, strike, lotes = perna
            receitas += calcular_receita(tipo_opcao, tipo_posicao, strike, lotes, precos_acucar)

        color = '#FF5733' if receitas[-1] < 0 else '#33FF57'  # Definindo a cor com base no valor da última receita

        # Criando o gráfico de área usando Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=precos_acucar, y=receitas, fill='tozeroy', line=dict(color=color)))
        fig.update_layout(title='Simulação de Opções',
                          xaxis_title='Preço do Açúcar',
                          yaxis_title='Receita (US$)')
        st.plotly_chart(fig)

def calcular_receita(tipo_opcao, tipo_posicao, strike, lotes, preco_acucar):
    if tipo_posicao == "Venda":
        if tipo_opcao == "Put":
            return np.where(preco_acucar > strike, 0, lotes * 1120 * (preco_acucar-strike))
        elif tipo_opcao == "Call":
            return np.where(preco_acucar < strike, 0, lotes * 1120 * ( strike - preco_acucar ))
    elif tipo_posicao == "Compra":
        if tipo_opcao == "Call":
            return np.where(preco_acucar < strike, 0, lotes * 1120 * (preco_acucar - strike))
        elif tipo_opcao == "Put":
            return np.where(preco_acucar > strike, 0, lotes * 1120 * (strike - preco_acucar))



import streamlit as st
import numpy as np
import plotly.graph_objs as go

def faturamento(variavel_parametro, valor_parametro, outras_variaveis):
    if variavel_parametro in ["Prod VHP", "NY", "Câmbio", "Prod Etanol", "Preço Etanol"]:
        faturamento = ((outras_variaveis["NY"] - 0.19) * 22.0462 * 1.04 * outras_variaveis["Câmbio"] * outras_variaveis["Prod VHP"]) + ((outras_variaveis["NY"] + 1) * 22.0462 * 0.75 * outras_variaveis["Câmbio"] * 12000) + outras_variaveis["Prod Etanol"] * outras_variaveis["Preço Etanol"] + 3227430 +  22061958


    elif variavel_parametro == "ATR":
        faturamento =    22061958 + (373613190 * valor_parametro) / 125.35
    elif variavel_parametro == "Moagem":
        faturamento =   22061958 + (373613190 * valor_parametro) / 1300000
    return faturamento

def custo(variavel_parametro, valor_parametro, outras_variaveis):
    if variavel_parametro in ["Prod VHP", "NY", "Câmbio", "Prod Etanol", "Preço Etanol"]:
        custo = 0.6* ((outras_variaveis["Prod Etanol"] * outras_variaveis["Preço Etanol"]) + ((outras_variaveis["NY"] + 1) * 22.0462 * 0.75 * outras_variaveis["Câmbio"] * 12000) + ((outras_variaveis["NY"] - 0.19) * 22.0462 * 1.04 * outras_variaveis["Câmbio"] * outras_variaveis["Prod VHP"])) + 88704735 + 43732035 +  20286465
    elif variavel_parametro == "ATR":
        custo = (0.6*(380767714 * valor_parametro / 125)) + 88704735 + 43732035 +  20286465
    elif variavel_parametro == "Moagem":
        custo = (0.6* (380767714 * valor_parametro / 1300000)) + 88704735 + 43732035 +  20286465
    return custo


def breakeven():
    st.title("Break-even Analysis")
    st.write("Selecione a variável a ser usada como parâmetro:")
    variavel_parametro = st.selectbox("Variável:", ["Prod VHP", "NY", "Câmbio", "Prod Etanol", "Preço Etanol", "ATR", "Moagem"])

    outras_variaveis = {}
    for variavel in ["Prod VHP", "NY", "Câmbio", "Prod Etanol", "Preço Etanol", "ATR", "Moagem"]:
        if variavel != variavel_parametro:
            valor = st.number_input(f"{variavel}:", value=0.0)
            outras_variaveis[variavel] = valor

    # Adiciona botão para gerar o gráfico
    if st.button("Gerar Gráfico"):
        valores_parametro = np.linspace(0, 5000, 100)
        faturamentos = []
        custos = []

        # Determina o intervalo adequado de acordo com a variável selecionada
        if variavel_parametro == "NY":
            valores_parametro = np.linspace(15, 25, 100)
        elif variavel_parametro == "Câmbio":
            valores_parametro = np.linspace(4, 6, 100)
        elif variavel_parametro == "Prod VHP":
            valores_parametro = np.linspace(90000, 110000, 100)
        elif variavel_parametro == "Moagem":
            valores_parametro = np.linspace(1000000, 1500000, 100)
        elif variavel_parametro == "ATR":
            valores_parametro = np.linspace(115, 145, 100)
        elif variavel_parametro in ["Prod Etanol", "Preço Etanol"]:
            valores_parametro = np.linspace(25000, 50000, 100) if variavel_parametro == "Prod Etanol" else np.linspace(2000, 4000, 100)

        for valor_parametro in valores_parametro:
            outras_variaveis[variavel_parametro] = valor_parametro
            faturamentos.append(faturamento(variavel_parametro, valor_parametro, outras_variaveis))
            custos.append(custo(variavel_parametro, valor_parametro, outras_variaveis))

        # Encontre o ponto de interseção entre as duas curvas
        idx_break_even = np.argmin(np.abs(np.array(faturamentos) - np.array(custos)))
        break_even_point = valores_parametro[idx_break_even]

        st.write(f"O ponto de break-even para a variável '{variavel_parametro}' é: **{break_even_point:.2f}**", unsafe_allow_html=True)

        # Plotar gráfico
        fig = go.Figure()
        
        # Adicionando as curvas de faturamento e custo ao gráfico
        fig.add_trace(go.Scatter(x=valores_parametro, y=faturamentos, mode='lines', name='Faturamento'))
        fig.add_trace(go.Scatter(x=valores_parametro, y=custos, mode='lines', name='Custo'))
        
        # Destacando o ponto de break-even
        fig.add_shape(
            type="line",
            x0=break_even_point, y0=min(min(faturamentos), min(custos)),
            x1=break_even_point, y1=max(max(faturamentos), max(custos)),
            line=dict(
                color="red",
                width=2,
                dash="dashdot",
            )
        )
        
        # Configurações do layout
        fig.update_layout(
            title="Análise de Ponto de Equilíbrio",
            xaxis_title=variavel_parametro,
            yaxis_title="Valor",
            legend=dict(x=0, y=1),
            margin=dict(l=20, r=20, t=50, b=20),
            template="plotly_white"
        )

        st.plotly_chart(fig)









def calcular_ebtida_ajustado(Moagem, Cambio, Preco_Etanol, NY):
    VHP = (89.45 * 0.8346 * Moagem) / 1000
    Etanol = (0.1654 * 80.18 * Moagem + 327.19 * 60075) / 1000

    Faturamento = (VHP - 4047) * (NY - 0.19) * 22.0462 * (1.04) * Cambio + (Etanol - 1000) * (
                Preco_Etanol + 349.83) * 0.96 +  3227430 +  22061958  + 12000 * (NY + 1) * 22.0462 * 0.75 * Cambio

    Custo = 0.6*0.93 * ((VHP - 4047) * (NY - 0.19) * 22.0462 * (1.04) * Cambio + (Etanol - 1000) * (
                Preco_Etanol + 349.83) * 0.96 + 12000 * (NY + 1) * 22.0462 * 0.75 * Cambio) + 88704735 + 43732035 +  20286465

    Ebtida_Ajustado = Faturamento - Custo

    return Ebtida_Ajustado

def encontrar_break_even(opcao, NY, Moagem, Cambio, Preco_Etanol):
    if opcao == "Moagem":
        while True:
            ebtida_ajustado = calcular_ebtida_ajustado(Moagem, Cambio, Preco_Etanol, NY)
            if ebtida_ajustado > 0:
                return Moagem
            else:
                Moagem += 1000
    elif opcao == "Preço Etanol":
        while True:
            ebtida_ajustado = calcular_ebtida_ajustado(Moagem, Cambio, Preco_Etanol, NY)
            if ebtida_ajustado > 0:
                return Preco_Etanol
            else:
                Preco_Etanol += 0.01
    elif opcao == "Câmbio":
        while True:
            ebtida_ajustado = calcular_ebtida_ajustado(Moagem, Cambio, Preco_Etanol, NY)
            if ebtida_ajustado > 0:
                return Cambio
            else:
                Cambio += 0.01
    elif opcao == "NY":
        while True:
            ebtida_ajustado = calcular_ebtida_ajustado(Moagem, Cambio, Preco_Etanol, NY)
            if ebtida_ajustado > 0:
                return NY
            else:
                NY += 0.01
    else:
        return "Opção inválida"

def probabilidade_abaixo_break_even(valor, media, percentil):
    desvio_padrao = (percentil - media) / stats.norm.ppf(0.8)  # Assumindo que o percentil 80 corresponde a 1 desvio padrão
    probabilidade = stats.norm.cdf(valor, loc=media, scale=desvio_padrao)
    return probabilidade

# Função para calcular os percentis
def calcular_percentis(break_even, media, desvio_padrao):
    percentis = []
    for i in range(5, 101, 5):
        valor_percentil = stats.norm.ppf(i/100, loc=media, scale=desvio_padrao)
        percentis.append((i, valor_percentil))
    return percentis

# Função para plotar o gráfico de distribuição
def plotar_grafico_distribuicao(break_even, media, desvio_padrao):
    plt.figure(figsize=(10, 6))
    sns.set(style="whitegrid")

    # Gerando uma amostra da distribuição normal para o plot
    x = np.linspace(media - 3*desvio_padrao, media + 3*desvio_padrao, 1000)
    y = stats.norm.pdf(x, loc=media, scale=desvio_padrao)

    # Plotando o gráfico da distribuição
    plt.plot(x, y, color='blue', label='Distribuição de Probabilidade')

    # Adicionando uma linha vertical para indicar o ponto de breakeven
    plt.axvline(x=break_even, color='black', linestyle='--', label='Break-even')

    # Preenchendo a área abaixo do ponto de breakeven em vermelho
    plt.fill_between(x, y, where=(x < break_even), color='red', alpha=0.3)

    # Preenchendo a área acima do ponto de breakeven em verde
    plt.fill_between(x, y, where=(x >= break_even), color='green', alpha=0.3)

    # Adicionando título e rótulos aos eixos
    plt.title('Distribuição de Probabilidade')
    plt.xlabel('Valor')
    plt.ylabel('Densidade')
    plt.legend()

    # Exibindo o gráfico
    st.pyplot(plt)



def cenarios():
    st.title("Cenários")
    st.write("Insira as premissas:")

    opcao = st.selectbox("Opção desejada", ("Moagem", "Preço Etanol", "Câmbio", "NY"))

    if opcao == "Moagem":
        NY = st.number_input("Valor de NY", value=20.0)
        Preco_Etanol = st.number_input("Valor da Preço Etanol")
        Cambio = st.number_input("Preço do Cambio")
        if st.button("Simular"):
            Moagem_break_even = encontrar_break_even(opcao, NY, 0, Cambio, Preco_Etanol)
            probabilidade = probabilidade_abaixo_break_even(Moagem_break_even, 1300000, (1400000 - 1300000) / stats.norm.ppf(0.8))
            st.write("Premissas:")
            st.write(f"Moagem: {Moagem_break_even:.2f} Ton")
            st.write(f"NY: {NY:.2f} cents/LB")
            st.write(f"Preço Etanol: {Preco_Etanol:.2f} R$/m³")
            st.write("Valor do Breakeven:", round(Moagem_break_even, 2))
            st.write("Risco segundo a simulação Monte Carlo:", round(probabilidade * 100, 2), "%")
            plotar_grafico_distribuicao(Moagem_break_even, 1300000, (1400000 - 1300000) / stats.norm.ppf(0.8))
            percentis = calcular_percentis(Moagem_break_even, 1300000, (1400000 - 1300000) / stats.norm.ppf(0.8))
            df = pd.DataFrame(percentis, columns=["Percentil", "Valor"])
            df["Cor"] = np.where(df["Valor"] >= Moagem_break_even, "green", "red")
            st.write("Tabela de Percentis")
            st.dataframe(df.set_index("Percentil"))

    elif opcao == "Preço Etanol":
        NY = st.number_input("Valor de NY", value=20.0)
        Moagem = st.number_input("Valor da Moagem")
        Cambio = st.number_input("Preço do Cambio")
        if st.button("Simular"):
            Preco_Etanol_break_even = encontrar_break_even(opcao, NY, Moagem, Cambio, 0)
            probabilidade = probabilidade_abaixo_break_even(Preco_Etanol_break_even, 2768.90, 3000.28)
            st.write("Premissas:")
            st.write(f"Moagem: {Moagem:.2f} Ton")
            st.write(f"NY: {NY:.2f} cents/LB")
            st.write(f"Preço Etanol: {Preco_Etanol_break_even:.2f} R$/m³")
            st.write("Valor do Breakeven:", round(Preco_Etanol_break_even, 2))
            st.write("Risco segundo a simulação Monte Carlo:", round(probabilidade * 100, 2), "%")
            plotar_grafico_distribuicao(Preco_Etanol_break_even, 2768.90, (3000.28 - 2768.90) / stats.norm.ppf(0.7))
            percentis = calcular_percentis(Preco_Etanol_break_even, 2768.90, (3000.28 - 2768.90) / stats.norm.ppf(0.7))
            df = pd.DataFrame(percentis, columns=["Percentil", "Valor"])
            df["Cor"] = np.where(df["Valor"] >= Preco_Etanol_break_even, "green", "red")
            st.write("Tabela de Percentis")
            st.dataframe(df.set_index("Percentil"))

    elif opcao == "Câmbio":
        NY = st.number_input("Valor de NY", value=20.0)
        Moagem = st.number_input("Valor da Moagem")
        Preco_Etanol = st.number_input("Preço do Preço do Etanol")
        if st.button("Simular"):
            Cambio_break_even = encontrar_break_even(opcao, NY, Moagem, 0, Preco_Etanol)
            probabilidade = probabilidade_abaixo_break_even(Cambio_break_even, 5.2504, 5.4293)
            st.write("Premissas:")
            st.write(f"Moagem: {Moagem:.2f} Ton")
            st.write(f"NY: {NY:.2f} cents/LB")
            st.write(f"Preço Etanol: {Preco_Etanol:.2f} R$/m³")
            st.write("Valor do Breakeven:", round(Cambio_break_even, 2))
            st.write("Risco segundo a simulação Monte Carlo:", round(probabilidade * 100, 2), "%")
            plotar_grafico_distribuicao(Cambio_break_even, 5.2504, (5.4293 - 5.1904) / stats.norm.ppf(0.8))
            percentis = calcular_percentis(Cambio_break_even, 5.2504, (5.4293 - 5.2504) / stats.norm.ppf(0.8))
            df = pd.DataFrame(percentis, columns=["Percentil", "Valor"])
            df["Cor"] = np.where(df["Valor"] >= Cambio_break_even, "green", "red")
            st.write("Tabela de Percentis")
            st.dataframe(df.set_index("Percentil"))

    elif opcao == "NY":
        Moagem = st.number_input("Valor da Moagem")
        Cambio = st.number_input("Preço do Cambio")
        Preco_Etanol = st.number_input("Preço do Preço do Etanol")
        if st.button("Simular"):
            NY_break_even = encontrar_break_even(opcao, 0, Moagem, Cambio, Preco_Etanol)
            probabilidade = probabilidade_abaixo_break_even(NY_break_even, 20.5572, 22.3796)
            st.write("Premissas:")
            st.write(f"Moagem: {Moagem:.2f} Ton")
            st.write(f"NY: {NY_break_even:.2f} cents/LB")
            st.write(f"Preço Etanol: {Preco_Etanol:.2f} R$/m³")
            st.write("Valor do Breakeven:", round(NY_break_even, 2))
            st.write("Risco segundo a simulação Monte Carlo:", round(probabilidade * 100, 2), "%")
            plotar_grafico_distribuicao(NY_break_even, 20.5572, (22.3796 - 20.5572) / stats.norm.ppf(0.8))
            percentis = calcular_percentis(NY_break_even, 20.5572, (22.3796 - 20.5572) / stats.norm.ppf(0.8))
            df = pd.DataFrame(percentis, columns=["Percentil", "Valor"])
            df["Cor"] = np.where(df["Valor"] >= NY_break_even, "green", "red")
            st.write("Tabela de Percentis")
            st.dataframe(df.set_index("Percentil"))

    else:
        st.write("Opção inválida")


def black_scholes(S, K, T, r, sigma, option_type):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        return S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    elif option_type == 'put':
        return K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0)
    else:
        raise ValueError("Tipo de opção inválido. Use 'call' ou 'put'.")

def blackscholes():
    # Parâmetros iniciais
    assets = {
        'SBV24.NYB': datetime(2024, 9, 16),
        'SBH25.NYB': datetime(2025, 2, 16),
    }

    risk_free_rate = 0.053

    volatilities = {
        'SBV24.NYB': 0.2973,
        'SBH25.NYB': 0.2573
    }

    # Interface do Streamlit
    st.title("Simulador de Preços de Opções - Modelo Black-Scholes")

    # Seleção do ativo
    asset = st.selectbox("Selecione o ativo subjacente", list(assets.keys()))

    # Seleção do tipo de opção
    option_type = st.selectbox("Selecione o tipo de opção", ["call", "put"])

    # Entrada do preço de exercício
    strike_price = st.number_input("Digite o preço de exercício (strike): ", min_value=1.0, value=20.0, step=0.5)

    # Botão para realizar a simulação
    if st.button("Simular"):
        # Parâmetros baseados na seleção do usuário
        expiration_date = assets[asset]
        sigma = volatilities[asset]

        # Calcula o tempo até a expiração em anos
        current_date = datetime.now()
        days_to_expiration = (expiration_date - current_date).days
        T = days_to_expiration / 365

        # Obtém o preço atual do ativo
        asset_data = yf.Ticker(asset)
        S = asset_data.history(period="1d")['Close'].iloc[-1]

        # Calcula o preço da opção escolhida pelo usuário
        option_price = black_scholes(S, strike_price, T, risk_free_rate, sigma, option_type)
        st.write(f"O preço da {option_type} é: {option_price:.2f}")

        # Gera um DataFrame com preços de opções para uma faixa de strikes
        strikes = np.arange(16, 22.25, 0.25)
        option_prices = {'Strike': strikes}

        # Calcula os preços das opções para cada strike no intervalo
        call_prices = [black_scholes(S, strike, T, risk_free_rate, sigma, 'call') for strike in strikes]
        put_prices = [black_scholes(S, strike, T, risk_free_rate, sigma, 'put') for strike in strikes]

        option_prices['Call Prices'] = call_prices
        option_prices['Put Prices'] = put_prices

        df_options = pd.DataFrame(option_prices)

        # Exibe a tabela com os preços das opções
        st.write("Tabela de Preços das Opções")
        st.write(round(df_options, 2))

        # Gráfico de Preços das Opções em Função do Strike
        fig_strike = go.Figure()

        if option_type == 'call':
            fig_strike.add_trace(go.Scatter(x=df_options['Strike'], y=df_options['Call Prices'], mode='lines', name='Call Prices'))
        elif option_type == 'put':
            fig_strike.add_trace(go.Scatter(x=df_options['Strike'], y=df_options['Put Prices'], mode='lines', name='Put Prices'))

        fig_strike.update_layout(title=f"Preços das Opções {option_type.upper()} - {asset}",
                          xaxis_title="Strike Price",
                          yaxis_title="Option Price",
                          template="plotly_dark")

        st.plotly_chart(fig_strike)

        # Gráfico de Preços das Opções em Função do Tempo até a Expiração
        times_to_expiration = np.linspace(0.01, T, 100)
        option_prices_vs_time = [black_scholes(S, strike_price, t, risk_free_rate, sigma, option_type) for t in times_to_expiration]

        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(x=times_to_expiration, y=option_prices_vs_time, mode='lines', name='Option Price'))

        fig_time.update_layout(title=f"Preço da {option_type.upper()} em Função do Tempo - {asset}",
                          xaxis_title="Time to Expiration (Years)",
                          yaxis_title="Option Price",
                          template="plotly_dark")

        st.plotly_chart(fig_time)

        # Gráfico de Preços das Opções em Função da Volatilidade
        volatilities_range = np.linspace(0.1, 0.5, 100)
        option_prices_vs_volatility = [black_scholes(S, strike_price, T, risk_free_rate, vol, option_type) for vol in volatilities_range]

        fig_volatility = go.Figure()
        fig_volatility.add_trace(go.Scatter(x=volatilities_range, y=option_prices_vs_volatility, mode='lines', name='Option Price'))

        fig_volatility.update_layout(title=f"Preço da {option_type.upper()} em Função da Volatilidade - {asset}",
                          xaxis_title="Volatility",
                          yaxis_title="Option Price",
                          template="plotly_dark")

        st.plotly_chart(fig_volatility)






import requests
from bs4 import BeautifulSoup

# Função para obter notícias
def get_news(ativo, data):
    # Aqui vai a lógica de scraping das notícias. Isso é apenas um exemplo fictício.
    noticias = [
        {"titulo": "Dólar sobe após dados de inflação nos EUA", "url": "https://www.investing.com/news/forex-news", "sentimento": "altista", "volatilidade": 3},
        {"titulo": "Açúcar tem leve recuo após negociações no mercado internacional", "url": "https://www.investing.com/news/commodities-news", "sentimento": "baixista", "volatilidade": 2},
        {"titulo": "Etanol se mantém estável com pouca demanda", "url": "https://www.investing.com/news/commodities-news", "sentimento": "neutro", "volatilidade": 1},
    ]
    # Filtrar notícias com base no ativo e data (simplificado para o exemplo)
    return noticias

# Função para classificar a volatilidade com estrelas
def mostrar_estrelas(volatilidade):
    return "★" * volatilidade + "☆" * (3 - volatilidade)

from datetime import date  # Adicione essa importação

def noticias():
    st.image("./ibea.png", width=500)
    st.title("Notícias do Mercado")
    
    ativo = st.selectbox("Selecione o ativo:", ["Açúcar", "Etanol", "Câmbio (USDBRL=X)"])
    data = st.date_input("Selecione a data:", value=date.today())
    
    if st.button("Gerar Notícias"):
        st.write(f"Notícias para {ativo} em {data}:")
        
        noticias_filtradas = []
        
        # Exemplo de notícias para o ativo "Câmbio (USDBRL=X)"
        if ativo == "Câmbio (USDBRL=X)":
            noticias_filtradas = [
                {
                    'titulo': 'Juros mais altos não atrapalham história dos mercados acionários no Brasil - HSBC',
                    'url': 'https://br.investing.com/news/stock-market-news/juros-mais-altos-nao-atrapalham-historia-dos-mercados-acionarios-no-brasil--hsbc-1333230',
                    'imagem': 'noticia1.png',
                    'sentimento': 'baixista',
                    'volatilidade': 1  # Baixa volatilidade
                },
                {
                    'titulo': 'Dólar tem queda forte e fecha abaixo de R$5,60 após dados fracos dos EUA',
                    'url': 'https://br.investing.com/news/forex-news/dolar-a-vista-fecha-em-baixa-de-119-a-r55726-na-venda-1333337',
                    'imagem': 'noticia2.png',
                    'sentimento': 'baixista',
                    'volatilidade': 3  # Alta volatilidade
                }
            ]

        for noticia in noticias_filtradas:
            st.image(noticia['imagem'], width=100)  # Mostra a imagem associada à notícia
            st.markdown(f"[{noticia['titulo']}]({noticia['url']})")  # Exibe o título da notícia com link
            st.write(f"Sentimento: **{noticia['sentimento'].capitalize()}**")  # Exibe se é altista/baixista
            st.write(f"Volatilidade: {mostrar_estrelas(noticia['volatilidade'])}")  # Exibe estrelas de volatilidade








import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Função para obter dados históricos de acordo com o símbolo selecionado
def get_historical_data(symbol, start_date):
    data = yf.download(symbol, start=start_date, end="2099-01-01")
    data['Daily Returns'] = data['Adj Close'].pct_change()
    data['EWMA Volatility'] = data['Daily Returns'].ewm(span=20).std()
    data['Abs Daily Returns'] = data['Daily Returns'].abs()
    data.dropna(inplace=True)
    return data

# Função para salvar o DataFrame em um arquivo Excel
def save_to_excel(data, filename):
    data.to_excel(filename, index=True)

# Função principal do aplicativo Streamlit
def volatilidade():
    # Configuração da interface do usuário
    st.title("Volatilidade de Preços - Açúcar e Dólar")

    # Seleção da variável a ser estudada
    variable = st.selectbox("Escolha a variável para estudar:", ["Açúcar", "Dólar"])

    # Seleção da data de início
    start_date = st.date_input("Selecione a data de início:", value=pd.to_datetime("2013-01-01"))

    # Definindo o símbolo com base na variável escolhida
    symbol = "SB=F" if variable == "Açúcar" else "USDBRL=X"

    # Botão para iniciar a simulação
    if st.button("Simular"):
        # Obtenção dos dados históricos
        data = get_historical_data(symbol, start_date.strftime('%Y-%m-%d'))

        # Verificação se há dados para exibir
        if not data.empty:
            # Gráfico interativo com Plotly
            fig = px.line(data, x=data.index, y='EWMA Volatility', title=f'Volatilidade EWMA - {variable}')
            st.plotly_chart(fig)

            # Botão para baixar o arquivo Excel
            excel_filename = f'{variable.lower()}_bi.xlsx'
            save_to_excel(data, excel_filename)

            # Botão de download
            with open(excel_filename, "rb") as file:
                st.download_button(
                    label="Baixar Excel",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("Não há dados disponíveis para a data selecionada. Por favor, tente outra data.")











import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    # Carregar apenas as colunas necessárias
    df = pd.read_excel('df_final.xlsx', usecols=['serial_medidor', 'data_hora_leitura', 'Cluster'])
    df['data_hora_leitura'] = pd.to_datetime(df['data_hora_leitura'])
    return df

def lessloss():
    # Carregar os dados
    df = load_data()

    # Título do aplicativo
    st.title('Análise de Medidores')

    # Filtros
    data_selecionada = st.selectbox('Selecione a data', df['data_hora_leitura'].dt.date.unique())
    serial_selecionado = st.selectbox('Selecione o serial do medidor', df['serial_medidor'].unique())

    # Botão para visualizar o gráfico
    if st.button('Visualizar'):
        # Filtrar os dados antes de carregar no Streamlit
        df_filtrado = df[(df['data_hora_leitura'].dt.date == data_selecionada) & (df['serial_medidor'] == serial_selecionado)]

        # Gráfico
        fig = px.line(df_filtrado, x='data_hora_leitura', y='Cluster', title='Cluster do Medidor ao Longo do Dia')
        st.plotly_chart(fig)









def login():

    # Exibindo a imagem da IBEA
    st.image("ibea.png", use_column_width=True)
    st.title("Login")
    
    # Campos de login e senha
    st.text_input("Login", key="username")
    st.text_input("Senha", type="password", key="password")
    
    if st.button("Entrar"):
        if st.session_state.username == "gestao.risco@ibea.com.br" and st.session_state.password == "Risco123$":
            st.session_state.logged_in = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Login ou senha incorretos.")

# Função principal
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.set_page_config(page_title="Gestão de Risco na Usina de Açúcar", page_icon="📈", layout="wide")
        
        st.sidebar.title("Menu")
        page = st.sidebar.radio("Selecione uma opção", ["Introdução", "ATR", "Metas", "Regressão Dólar", "Volatilidade","Simulação de Opções", "Monte Carlo", "Mercado", "Risco", "Breakeven", "Black Scholes", "Cenários", "VaR","Notícias","Less Loss" ])

        if page == "Introdução":
            st.image("./ibea.png", width=500)
            st.title("Gestão de Risco e Derivativos")
            st.write("""
                A indústria açucareira é um dos pilares da economia em muitos países, mas está sujeita a flutuações significativas nos preços do açúcar e do dólar, entre outros fatores. Nesse cenário, a gestão de riscos desempenha um papel fundamental para garantir a estabilidade e a lucratividade das operações.
                 
                **Proteção Cambial:**
                A volatilidade no mercado de câmbio pode afetar diretamente os resultados financeiros de uma usina de açúcar, especialmente em países onde a moeda local é suscetível a oscilações. A proteção cambial é uma estratégia essencial para mitigar esse risco. Uma maneira comum de proteger-se é através do uso de contratos futuros de câmbio, que permitem fixar uma taxa de câmbio para transações futuras em moeda estrangeira, garantindo assim um preço previsível para as exportações de açúcar.

                **Fixações:**
                Além da proteção cambial, as usinas de açúcar frequentemente recorrem a estratégias de fixações para garantir um preço mínimo para sua produção. Isso pode ser feito através de contratos a termo ou swaps, onde um preço é acordado antecipadamente para uma determinada quantidade de açúcar. Essas fixações fornecem uma certa segurança contra quedas abruptas nos preços do açúcar, permitindo que a usina planeje suas operações com mais confiança.

                **Mercado de Opções do Açúcar:**
                Outra ferramenta importante na gestão de riscos é o mercado de opções do açúcar. As opções oferecem às usinas de açúcar a flexibilidade de proteger-se contra movimentos desfavoráveis nos preços do açúcar, enquanto ainda se beneficiam de movimentos favoráveis. Por exemplo, uma usina pode comprar opções de venda para proteger-se contra quedas nos preços do açúcar, enquanto ainda pode aproveitar os aumentos de preço se o mercado se mover a seu favor.

                Em resumo, a gestão de riscos na indústria açucareira é essencial para garantir a estabilidade financeira e o crescimento sustentável das usinas de açúcar. Estratégias como proteção cambial, fixações e o uso inteligente do mercado de opções são fundamentais para mitigar os riscos inerentes a esse setor e maximizar os retornos sobre o investimento.
            """)

        # As outras funções do menu continuam aqui...
        elif page == "Metas":
            st.image("./ibea.png", width=500)
            st.title("Metas")
            st.write("Selecione a meta desejada:")
            meta = st.slider("Meta:", min_value=2400, max_value=2800, value=2600, step=10)
            st.write("Após selecionar a meta, clique no botão 'Calcular' para visualizar o gráfico.")
            if st.button("Calcular"):
                plot_heatmap(meta)
                mtm_data = calcular_mtm(meta)
                st.line_chart(mtm_data.set_index('Date'), use_container_width=True)
        elif page == "Simulação de Opções":
            st.image("./ibea.png", width=500)
            simulacao_opcoes()
        elif page == "ATR":
            st.image("./ibea.png", width=500)
            atr()
        elif page == "Regressão Dólar":
            st.image("./ibea.png", width=500)
            regressaoDolar()   
        elif page == "Volatilidade":
            st.image("./ibea.png", width=500)
            volatilidade()
        elif page == "Monte Carlo":
            st.image("./ibea.png", width=500)
            monte_carlo()
        elif page == "Mercado":
            st.image("./ibea.png", width=500)
            mercado()
        elif page == "Risco":
            st.image("./ibea.png", width=500)
            risco()
        elif page == "Breakeven":
            st.image("./ibea.png", width=500)
            breakeven()
        elif page == "Cenários":
            st.image("./ibea.png", width=500)
            cenarios()
        elif page == "VaR":
            st.image("./ibea.png", width=500)
            VaR()
        elif page == "Black Scholes":
            st.image("./ibea.png", width=500)
            blackscholes()

        elif page == "Notícias":
            noticias()
        if page == "Less Loss":
            lessloss()
if __name__ == "__main__":
    main()
