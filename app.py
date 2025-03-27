
import streamlit as st
import pandas as pd
import requests
import json
from io import BytesIO

# CONFIGURAÇÕES
TOKEN = "Bearer SEU_TOKEN_AQUI"
BASE_URL = "https://api.nibo.com.br/empresas/v1/schedules/debit"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": TOKEN
}

# FUNÇÃO PARA BUSCAR AGENDAMENTOS
def buscar_agendamentos(top=10):
    params = {"$top": top}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Erro ao buscar agendamentos")
        return []

# FUNÇÃO PARA MONTAR O RATEIO
def montar_rateio_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = ["costCenterId", "value"]
    df["value"] = df["value"].astype(str).str.replace(".", "", regex=False)
    df["value"] = df["value"].str.replace(",", ".", regex=False).astype(float)
    df_agrupado = df.groupby("costCenterId", as_index=False).sum()

    return [
        {"id": row["costCenterId"], "value": round(row["value"], 2)}
        for _, row in df_agrupado.iterrows()
    ]

# FUNÇÃO PARA ATUALIZAR AGENDAMENTO
def atualizar_agendamento(schedule_id, payload):
    url = f"{BASE_URL}/{schedule_id}"
    response = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    return response.status_code == 204

# INTERFACE STREAMLIT
st.title("Editor de Agendamentos Nibo")

agendamentos = buscar_agendamentos(top=20)

if agendamentos:
    opcoes = [f"{ag['description']} | Valor: R$ {ag['value']} | ID: {ag['id']}" for ag in agendamentos]
    escolha = st.selectbox("Selecione um agendamento para editar:", options=opcoes)
    idx = opcoes.index(escolha)
    ag = agendamentos[idx]

    st.subheader("Editar informações do agendamento")
    descricao = st.text_input("Descrição", value=ag.get("description", ""))
    valor = st.number_input("Valor", value=float(ag.get("value", 0)))
    due_date = st.date_input("Data de vencimento")
    schedule_date = st.date_input("Data prevista")
    accrual_date = st.date_input("Data da competência")
    referencia = st.text_input("Referência", value=ag.get("reference", ""))
    is_flagged = st.checkbox("Marcar como favorito?", value=ag.get("isFlagged", False))

    st.subheader("Upload do rateio (Excel)")
    uploaded_file = st.file_uploader("Arquivo Excel com colunas: costCenterId, value", type=["xlsx"])

    if st.button("Atualizar Agendamento"):
        if not uploaded_file:
            st.warning("Envie um arquivo Excel com os rateios.")
        else:
            rateio = montar_rateio_excel(uploaded_file)

            payload = {
                "stakeholderId": ag["stakeholder"]["id"],
                "dueDate": due_date.isoformat(),
                "scheduleDate": schedule_date.isoformat(),
                "accrualDate": accrual_date.isoformat(),
                "reference": referencia,
                "description": descricao,
                "isFlagged": is_flagged,
                "categories": [{"id": ag["categories"][0]["id"]}],
                "costCenterValueType": "0",
                "costcenters": rateio
            }

            sucesso = atualizar_agendamento(ag["id"], payload)
            if sucesso:
                st.success("Agendamento atualizado com sucesso!")
            else:
                st.error("Erro ao atualizar o agendamento.")
