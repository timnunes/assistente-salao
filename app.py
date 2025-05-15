import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def testar_conexao():
    try:
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["credenciais"], escopo)
        gspread.authorize(creds)
        st.success("✅ Conexão com Google Sheets funcionando!")
    except Exception as e:
        st.error(f"❌ Erro: {e}")

st.title("Teste de conexão com Google Sheets")
testar_conexao()
