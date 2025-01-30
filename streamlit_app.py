import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
# from PIL import Image

# img = Image.open("logo_ifmg_campus_pn.png")
# # Redimensiona a imagem (largura, altura)
# img_resized = img.resize((300, 100))


# Função para carregar os dados
# @st.cache_data
def load_data():
    # Lê o arquivo CSV diretamente
    data = pd.read_csv('data.csv', sep=';', parse_dates=['date'])
    # Extrai apenas a data (sem a hora)
    # data['date_only'] = data['date'].dt.date
    data['date_only'] = data['date'].dt.strftime('%d-%m-%Y')
    return data

# Carregar os dados
data = load_data()

last_update = data['date'].iloc[-1].strftime('%d/%m/%Y às %H:%M:%S')

# Agrupar os dados por dia e pegar o último valor do dia
grouped_data = data.groupby('date_only').last().reset_index()

# Calcular o valor total acumulado em MWh
total_energy_mwh = data['total'].iloc[-1]  # Pega o último valor da coluna 'total'
co2_last = grouped_data['co2'].iloc[-1]  # Último valor de CO2
trees_last = grouped_data['trees'].iloc[-1]  # Último valor de Árvores



# st.image(img_resized, use_container_width=False)
# Título da página
st.title('📊 Dados de Geração de Energia')
st.markdown('⚡ Acompanhe em tempo real a geração de energia da usina solar 🌞 no IFMG Campus Ponte Nova.' ) 

# Exibir o valor total acumulado em MWh com destaque
st.markdown(
    f"""
    <div style="
        background-color: #0E1117;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
    ">
        <h2 style="color: #FFFFFF; margin: 0;">📈 Total Gerado desde a implantação</h2>
        <h1 style="color: #00FF00; margin: 0;">{total_energy_mwh:.2f} MWh</h1>
        <p style="color: #FFFFFF; margin: 0; font-size: 12px;">Última atualização em {last_update}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('---')

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
    xaxis_tickfont_size=14,  # Valores do eixo X maiores
    yaxis_tickfont_size=14,  # Valores do eixo Y maiores
    uniformtext_minsize=12,  # Tamanho mínimo do texto
    uniformtext_mode='hide',  # Esconde texto que não couber
    xaxis_tickformat='%d-%m-%Y'  # Formata o eixo X para exibir apenas a data
)

st.plotly_chart(fig_bar)


st.markdown('---')

# Exibir os últimos valores de CO₂ Compensado e Árvores com fundo customizado
st.header('🌍 Últimos valores')

# Card para CO₂ Compensado
st.markdown(
    f"""
    <div style="
        background-color: #F0F8FF;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Cloud_icon.svg/512px-Cloud_icon.svg.png');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        padding: 50px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    ">
        <h2 style="color: #000000; margin: 0;">☁️ CO₂ Compensado</h2>
        <h1 style="color: #FF4500; margin: 0;">{co2_last:.2f} toneladas</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Card para Árvores
st.markdown(
    f"""
    <div style="
        background-color: #E8F5E9;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Tree_font_awesome.svg/512px-Tree_font_awesome.svg.png');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        padding: 50px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    ">
        <h2 style="color: #000000; margin: 0;">🌳 Árvores Plantadas</h2>
        <h1 style="color: #228B22; margin: 0;">{trees_last:.0f}</h1>
    </div>
    """,
    unsafe_allow_html=True
)
