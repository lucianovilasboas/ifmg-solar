import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# Função para conectar ao banco de dados
def conectar_bd():
    return sqlite3.connect('dados_energia.db')

# Função para criar hash da senha
def criar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para autenticar usuário
def autenticar_usuario(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
              (username, criar_hash(password)))
    return c.fetchone()

# Funções CRUD para registros de energia
def criar_registro(conn, data, co2, arvores, total_energia, energia_diaria):
    c = conn.cursor()
    c.execute('''INSERT INTO registros 
              (data, co2, arvores, total_energia, energia_diaria)
              VALUES (?, ?, ?, ?, ?)''',
              (data, co2, arvores, total_energia, energia_diaria))
    conn.commit()

def ler_registros(conn):
    return pd.read_sql('SELECT * FROM registros ORDER BY data DESC', conn)

def atualizar_registro(conn, id, data, co2, arvores, total_energia, energia_diaria):
    c = conn.cursor()
    c.execute('''UPDATE registros SET
              data = ?,
              co2 = ?,
              arvores = ?,
              total_energia = ?,
              energia_diaria = ?
              WHERE id = ?''',
              (data, co2, arvores, total_energia, energia_diaria, id))
    conn.commit()

def excluir_registro(conn, id):
    c = conn.cursor()
    c.execute('DELETE FROM registros WHERE id = ?', (id,))
    conn.commit()

# Interface de login
def login_page(conn):
    st.title("🔐 Página de Login")
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Login"):
        usuario = autenticar_usuario(conn, username, password)
        if usuario:
            st.session_state['autenticado'] = True
            st.session_state['username'] = usuario[1]
            st.session_state['role'] = usuario[3]
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Nome de usuário ou senha incorretos.")

# Interface de usuário
def user_page(conn):
    st.title("📊 Página de Usuário")
    st.write(f"Bem-vindo, {st.session_state['username']}! Aqui você pode gerenciar os dados de energia.")

    menu = ["Adicionar Registro", "Visualizar Registros", "Editar/Excluir Registros"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Adicionar Registro":
        st.subheader("Novo Registro")
        data = st.date_input("Data")
        co2 = st.number_input("CO₂ (toneladas)", min_value=0.0, format="%.2f")
        arvores = st.number_input("Número de Árvores", min_value=0)
        total_energia = st.number_input("Total de Energia Produzida (kWh)", min_value=0.0, format="%.2f")
        energia_diaria = st.number_input("Energia Gerada por Dia (kWh)", min_value=0.0, format="%.2f")

        if st.button("Salvar"):
            criar_registro(conn, data, co2, arvores, total_energia, energia_diaria)
            st.success("Registro salvo com sucesso!")

    elif choice == "Visualizar Registros":
        st.subheader("Registros Armazenados")
        df = ler_registros(conn)
        if not df.empty:
            st.dataframe(df.style.format({
                'co2': '{:.2f} ton',
                'total_energia': '{:.2f} kWh',
                'energia_diaria': '{:.2f} kWh/day'
            }), use_container_width=True)
        else:
            st.warning("Nenhum registro encontrado.")

    elif choice == "Editar/Excluir Registros":
        st.subheader("Editar ou Excluir Registros")
        df = ler_registros(conn)
        
        if not df.empty:
            registro_selecionado = st.selectbox(
                "Selecione um registro para editar/excluir",
                df['id'],
                format_func=lambda x: f"ID {x} - {df[df['id'] == x]['data'].values[0]}"
            )
            
            registro = df[df['id'] == registro_selecionado].iloc[0]
            
            with st.form(key='edit_form'):
                data = st.date_input("Data", value=pd.to_datetime(registro['data']))
                co2 = st.number_input("CO₂ (toneladas)", value=registro['co2'], format="%.2f")
                arvores = st.number_input("Número de Árvores", value=registro['arvores'])
                total_energia = st.number_input("Total de Energia Produzida (kWh)", 
                                              value=registro['total_energia'], format="%.2f")
                energia_diaria = st.number_input("Energia Gerada por Dia (kWh)", 
                                               value=registro['energia_diaria'], format="%.2f")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Atualizar Registro"):
                        atualizar_registro(conn, registro_selecionado, data, co2, arvores, 
                                         total_energia, energia_diaria)
                        st.success("Registro atualizado!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Excluir Registro"):
                        excluir_registro(conn, registro_selecionado)
                        st.success("Registro excluído!")
                        st.rerun()
        else:
            st.warning("Nenhum registro encontrado para edição.")

# Função principal para gerenciar o fluxo da aplicação
def main():
    conn = conectar_bd()
    
    # Verificar se o usuário está autenticado
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        login_page(conn)
    else:
        user_page(conn)
    
    conn.close()


# Executar a aplicação
main()