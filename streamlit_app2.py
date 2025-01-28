import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Função para carregar os dados
@st.cache_data
def load_data():
    # Lê o arquivo CSV diretamente
    data = pd.read_csv('data.csv', sep=';', parse_dates=['date'])
    # Extrai apenas a data (sem a hora)
    data['date_only'] = data['date'].dt.date
    return data

# Carregar os dados
data = load_data()

# Agrupar os dados por dia e pegar o último valor do dia
grouped_data = data.groupby('date_only').last().reset_index()

# Calcular o valor total acumulado em MWh
total_energy_mwh = data['total'].iloc[-1]  # Pega o último valor da coluna 'total'

# Título da página
st.title('📊 Dados de Geração de Energia')
st.markdown('⚡ Dados de geração de energia no IFMG Campus Ponte Nova')

# Exibir o valor total acumulado em MWh com destaque
st.markdown(
    f"""
    <div style="
        background-color: #0E1117;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    ">
        <h2 style="color: #FFFFFF; margin: 0;">📈 Total Gerado desde a implantação</h2>
        <h1 style="color: #00FF00; margin: 0;">{total_energy_mwh:.2f} MWh</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Primeira figura: Gráfico de barras por date e today
st.header('📅 Geração de energia por dia')
fig_bar = px.bar(
    grouped_data,
    x='date_only',
    y='today',
    title=' ',
    labels={'date_only': 'Data', 'today': 'Geração de Energia (kWh)'},
    text='today'  # Exibe os valores de 'today' dentro das barras
)

# Ajustar o tamanho da fonte e o estilo do texto nas barras
fig_bar.update_traces(
    textfont_size=16,  # Tamanho da fonte dos valores
    textposition='inside',  # Posiciona o texto dentro das barras
    insidetextanchor='middle',  # Centraliza o texto dentro das barras
    textfont_color='white'  # Cor do texto (branco para contraste)
)

# Ajustar o layout do gráfico de barras
fig_bar.update_layout(
    title_font_size=24,  # Título maior
    xaxis_title_font_size=20,  # Título do eixo X maior
    yaxis_title_font_size=20,  # Título do eixo Y maior
    xaxis_tickfont_size=16,  # Valores do eixo X maiores
    yaxis_tickfont_size=16,  # Valores do eixo Y maiores
    uniformtext_minsize=12,  # Tamanho mínimo do texto
    uniformtext_mode='hide'  # Esconde texto que não couber
)

st.plotly_chart(fig_bar)

# Segunda figura: Gráfico de linhas por date, co2 e trees
st.header('🌍 Redução na Emissão de CO2 e Árvores plantadas por dia')
fig_line = go.Figure()

# Adiciona a linha para CO2
fig_line.add_trace(go.Scatter(
    x=grouped_data['date_only'],
    y=grouped_data['co2'],
    mode='lines',
    name='CO2',
    line=dict(width=3)  # Linha mais grossa
))

# Adiciona a linha para Trees
fig_line.add_trace(go.Scatter(
    x=grouped_data['date_only'],
    y=grouped_data['trees'],
    mode='lines',
    name='Árvores',
    line=dict(width=3)  # Linha mais grossa
))

# Configura o layout do gráfico de linhas
fig_line.update_layout(
    title='',
    title_font_size=24,  # Título maior
    xaxis_title='Data',
    xaxis_title_font_size=20,  # Título do eixo X maior
    yaxis_title='Valor',
    yaxis_title_font_size=20,  # Título do eixo Y maior
    xaxis_tickfont_size=16,  # Valores do eixo X maiores
    yaxis_tickfont_size=16,  # Valores do eixo Y maiores
    legend_font_size=18,  # Legenda maior
)

# Exibe o gráfico de linhas
st.plotly_chart(fig_line)