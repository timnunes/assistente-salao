import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
from io import StringIO

HORARIO_ABERTURA = 8
HORARIO_FECHAMENTO = 18

INSTANCE_ID = "COLE_SEU_INSTANCE_ID_AQUI"
TOKEN = "COLE_SEU_TOKEN_AQUI"

def enviar_whatsapp_real(numero_com_ddd, mensagem):
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-messages"
    payload = {"phone": f"55{numero_com_ddd}", "message": mensagem}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except:
        return False

def enviar_whatsapp(cliente, mensagem, telefone):
    sucesso = enviar_whatsapp_real(telefone, mensagem)
    if sucesso:
        st.success(f"WhatsApp enviado para {cliente}.")
    else:
        st.error("Erro ao enviar mensagem pelo WhatsApp.")

def conectar_planilha():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais_json = st.secrets["credenciais"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(credenciais_json, escopo)
    cliente = gspread.authorize(credenciais)
    return cliente.open("Agenda_Salao").sheet1

def obter_horarios_disponiveis(planilha, data):
    registros = planilha.get_all_records()
    ocupados = {row["Hora"] for row in registros if row["Data"] == data and row["Status"] == "Confirmado"}
    horarios = [f"{h:02d}:00" for h in range(HORARIO_ABERTURA, HORARIO_FECHAMENTO)]
    return [h for h in horarios if h not in ocupados]

def adicionar_agendamento(planilha, cliente, telefone, data, hora):
    try:
        hora_int = int(hora.split(":")[0])
        if hora_int < HORARIO_ABERTURA or hora_int >= HORARIO_FECHAMENTO:
            st.warning("Fora do horário de funcionamento.")
            return False
    except:
        st.warning("Horário inválido.")
        return False

    registros = planilha.get_all_records()
    for row in registros:
        if row["Data"] == data and row["Hora"] == hora and row["Status"] == "Confirmado":
            st.warning("Horário já ocupado.")
            return False

    planilha.append_row([cliente, data, hora, "Confirmado", telefone])
    return True

st.title("💇‍♀️ Agendamento - Salão Beleza Viva")
aba = st.sidebar.selectbox("Ação", ["Agendar", "Ver Horários Disponíveis"])
planilha = conectar_planilha()

if aba == "Agendar":
    with st.form("form_agendar"):
        cliente = st.text_input("Nome do cliente")
        telefone = st.text_input("Telefone (com DDD)")
        data = st.date_input("Data", min_value=datetime.date.today()).isoformat()
        horarios = obter_horarios_disponiveis(planilha, data)
        hora = st.selectbox("Horário", horarios)
        submitted = st.form_submit_button("Agendar")

        if submitted:
            if adicionar_agendamento(planilha, cliente, telefone, data, hora):
                st.success(f"Agendado para {data} às {hora}")
                mensagem = f"Olá {cliente}, seu agendamento foi confirmado para {data} às {hora}. ✨"
                enviar_whatsapp(cliente, mensagem, telefone)

elif aba == "Ver Horários Disponíveis":
    data = st.date_input("Escolha a data", min_value=datetime.date.today()).isoformat()
    horarios = obter_horarios_disponiveis(planilha, data)
    if horarios:
        st.info("Horários disponíveis:")
        st.write("\n".join(horarios))
    else:
        st.warning("Nenhum horário disponível nessa data.")