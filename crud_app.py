import streamlit as st
import sqlite3
import pandas as pd

# Função para criar/conectar ao banco de dados
def criar_bd():
    conn = sqlite3.connect('dados_energia.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registros
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE,
                  co2 REAL,
                  arvores INTEGER,
                  total_energia REAL,
                  energia_diaria REAL)''')
    conn.commit()
    return conn

# Funções CRUD
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

# Interface Streamlit
def main():
    st.title("📊 Sistema de Monitoramento de Energia e CO₂")
    conn = criar_bd()

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
                'total_energia': '{:.2f} MWh',
                'energia_diaria': '{:.2f} kWh/day'
            }), use_container_width=True)
            
            # Mostrar métricas resumidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total CO₂ Compensado", f"{df['co2'].iloc[-1]:.2f} ton")
            with col2:
                st.metric("Total de Árvores", f"{df['arvores'].iloc[-1]:,}")
            with col3:
                st.metric("Energia Total Produzida", f"{df['total_energia'].iloc[-1]:,.2f} kWh")
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

    conn.close()

if __name__ == '__main__':
    main()