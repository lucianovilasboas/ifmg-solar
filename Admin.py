import streamlit as st 
import sqlite3
import hashlib
import pandas as pd

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
                  password TEXT,
                  role TEXT)''')
    
    conn.commit()
    return conn

# Função para criar hash da senha
def criar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para conectar ao banco de dados
def conectar_bd():
    return criar_bd()

# Função para listar usuários
def listar_usuarios(conn):
    return pd.read_sql('SELECT id, username, role FROM usuarios', conn)

# Função para criar usuário
def criar_usuario(conn, username, password, role):
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)',
                  (username, criar_hash(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Função para atualizar usuário
def atualizar_usuario(conn, id, username, role):
    c = conn.cursor()
    c.execute('UPDATE usuarios SET username = ?, role = ? WHERE id = ?',
              (username, role, id))
    conn.commit()

# Função para excluir usuário
def excluir_usuario(conn, id):
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()

# Função para autenticar usuário
def autenticar_usuario(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
              (username, criar_hash(password)))
    return c.fetchone()

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

# Interface de administração
def admin_page(conn):
    st.title("👨‍💻 Página de Administração")
    st.write("Bem-vindo, Administrador! Aqui você pode gerenciar os usuários do sistema.")

    # Listar usuários
    st.subheader("Lista de Usuários")
    df_usuarios = listar_usuarios(conn)
    if not df_usuarios.empty:
        st.dataframe(df_usuarios, use_container_width=True)
    else:
        st.warning("Nenhum usuário cadastrado.")

    # Adicionar novo usuário
    st.subheader("Adicionar Novo Usuário")
    with st.form(key='form_add_usuario'):
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        role = st.selectbox("Papel do usuário", ["Admin", "User"])
        if st.form_submit_button("Adicionar Usuário"):
            if criar_usuario(conn, username, password, role):
                st.success("Usuário adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao adicionar usuário. Nome de usuário já existe.")
        
    # Editar/Excluir usuário
    st.subheader("Editar ou Excluir Usuário")
    usuario_selecionado = st.selectbox(
        "Selecione um usuário para editar/excluir",
        df_usuarios['id'],
        format_func=lambda x: f"ID {x} - {df_usuarios[df_usuarios['id'] == x]['username'].values[0]}"
    )
    
    if usuario_selecionado:
        usuario = df_usuarios[df_usuarios['id'] == usuario_selecionado].iloc[0]
        with st.form(key='form_edit_usuario'):
            novo_username = st.text_input("Nome de usuário", value=usuario['username'])
            novo_role = st.selectbox("Papel do usuário", ["Admin", "User"], index=0 if usuario['role'] == "Admin" else 1)
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Atualizar Usuário"):
                    atualizar_usuario(conn, usuario_selecionado, novo_username, novo_role)
                    st.success("Usuário atualizado com sucesso!")
                    st.rerun()
            with col2:
                if st.form_submit_button("Excluir Usuário"):
                    excluir_usuario(conn, usuario_selecionado)
                    st.success("Usuário excluído com sucesso!")
                    st.rerun()

# Verificar se o usuário está autenticado
def main():
    conn = conectar_bd()
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        login_page(conn)
    else:
        if st.session_state['role'] == "Admin":
            admin_page(conn)
        else:
            st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    
    conn.close()



# Executar a função principal
main()