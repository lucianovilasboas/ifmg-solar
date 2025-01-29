import streamlit as st

admin_page = st.Page("Admin.py", title="Admin", icon=":material/login:")
user_page  = st.Page("User.py", title="User", icon=":material/person:")

home = st.Page("streamlit_app.py", title="Home", icon=":material/dashboard:", default=True)

# pg = st.navigation(
#     {
#         "Home": [home],
#         "Admin": [admin_page],
#     }
# )
# pg.run()


print(st.query_params)

# Adicionar uma lógica para verificar se a URL é diretamente acessada
if "Admin" in st.query_params:
    pg = st.navigation(
        {
            "Admin": [admin_page],
        }
    )

elif "User" in st.query_params:
    pg = st.navigation(
        {
            "User": [user_page],
        }
    )
else:
    pg = st.navigation(
        {
            "Home": [home],
        }
    )



pg.run()
