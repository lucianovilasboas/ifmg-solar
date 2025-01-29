import streamlit as st
import sqlite3
import pandas as pd
import hashlib

st.set_page_config(page_title="Admin", page_icon=":earth_americas:", layout="wide")

# Função para criar/conectar ao banco de dados
def criar_bd():
    conn = sqlite3.connect('dados_energia.db')
    c = conn.cursor()
    
    # Tabela de registros de energia
    c.execute('''CREATE TABLE IF NOT EXISTS registros
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE,
                  co2 REAL,
                  arvores INTEGER,
                  total_energia REAL,
                  energia_diaria REAL)''')
    
    # Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    conn.commit()
    return conn

# Função para criar hash da senha
def criar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para verificar credenciais
def verificar_usuario(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT password FROM usuarios WHERE username = ?', (username,))
    resultado = c.fetchone()
    if resultado and resultado[0] == criar_hash(password):
        return True
    return False

# Função para cadastrar novo usuário
def cadastrar_usuario(conn, username, password):
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)',
                  (username, criar_hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

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

# Interface de autenticação
def tela_login(conn):
    st.subheader("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if verificar_usuario(conn, username, password):
            st.session_state['autenticado'] = True
            st.session_state['username'] = username
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# Interface de cadastro de usuário
def tela_cadastro(conn):
    st.subheader("Cadastro de Usuário")
    username = st.text_input("Escolha um nome de usuário")
    password = st.text_input("Escolha uma senha", type="password")
    confirmar_senha = st.text_input("Confirme a senha", type="password")
    
    if st.button("Cadastrar"):
        if password == confirmar_senha:
            if cadastrar_usuario(conn, username, password):
                st.success("Usuário cadastrado com sucesso! Faça login.")
            else:
                st.error("Nome de usuário já existe.")
        else:
            st.error("As senhas não coincidem.")

# Interface principal do sistema
def tela_principal(conn):
    st.title("📊 Sistema de Monitoramento de Energia e CO₂")
    
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

# Função principal
def main():
    conn = criar_bd()
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    if not st.session_state['autenticado']:
        st.sidebar.title("Autenticação")
        opcao = st.sidebar.radio("Escolha uma opção", ["Login", "Cadastrar"])
        
        if opcao == "Login":
            tela_login(conn)
        elif opcao == "Cadastrar":
            tela_cadastro(conn)
    else:
        st.sidebar.title(f"Bem-vindo, {st.session_state['username']}!")
        if st.sidebar.button("Logout"):
            st.session_state['autenticado'] = False
            st.session_state['username'] = None
            st.rerun()
        tela_principal(conn)
    
    conn.close()


main()



# if __name__ == '__main__':
#     main()