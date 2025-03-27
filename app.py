
import streamlit as st
import requests
import pandas as pd
import os

# Título
st.title("Gerenciador de Pagamentos Agendados - Nibo")

# Token seguro via Streamlit Secrets
API_TOKEN = st.secrets["NIBO_API_KEY"]
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "ApiToken": API_TOKEN
}
BASE_URL = "https://api.nibo.com.br/empresas/v1/schedules/debit"

# Buscar agendamentos
def listar_pagamentos(data_inicio=None, data_fim=None):
    try:
        
    params = {}
    if data_inicio and data_fim:
        filtro = f"dueDate ge {data_inicio} and dueDate le {data_fim}"
        params["$filter"] = filtro
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
        st.code(f"Status: {response.status_code}")
        st.code(f"Resposta: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        st.error("Erro ao buscar pagamentos agendados:")
        st.text(e)
        return []

# Atualizar pagamento
def atualizar_pagamento(schedule_id, dados):
    url = f"{BASE_URL}/{schedule_id}"
    try:
        response = requests.put(url, headers=HEADERS, json=dados)
        st.code(f"Status: {response.status_code}")
        st.code(f"Resposta: {response.text}")
        response.raise_for_status()
        st.success("Pagamento atualizado com sucesso!")
    except requests.exceptions.RequestException as e:
        st.error("Erro ao atualizar pagamento:")
        st.text(e)

# Interface

st.subheader("Filtrar por período")
col1, col2 = st.columns(2)
data_inicio = col1.date_input("Data início")
data_fim = col2.date_input("Data fim")

pagamentos = []
if st.button("Buscar agendamentos"):
    pagamentos = listar_pagamentos(data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d"))

if pagamentos:
    df = pd.DataFrame(pagamentos)
    st.dataframe(df)

    st.header("Selecionar e Editar Agendamento")
    ids = df['scheduleId'].tolist()
    escolha = st.selectbox("Escolha um agendamento", ids)

    ag = df[df['id'] == escolha].iloc[0]
    valor = st.number_input("Valor", value=float(ag["value"]))
    descricao = st.text_input("Descrição", value=ag.get("description", ""))
    due = st.date_input("Vencimento")
    schedule = st.date_input("Data prevista")
    accrual = st.date_input("Competência")
    referencia = st.text_input("Referência", value=ag.get("reference", ""))

    st.header("Upload de Rateio (Excel com 'costCenterId' e 'value')")
    arquivo = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    if arquivo:
        rateio_df = pd.read_excel(arquivo)
        rateio_df.columns = ["id", "value"]
        rateio_df["value"] = rateio_df["value"].astype(str).str.replace(".", "", regex=False)
        rateio_df["value"] = rateio_df["value"].str.replace(",", ".", regex=False).astype(float)
        st.dataframe(rateio_df)

    if st.button("Atualizar agendamento"):
        if not arquivo:
            st.warning("Você precisa enviar o arquivo de rateio.")
        else:
            payload = {
                "stakeholderId": ag["stakeholder"]["id"],
                "dueDate": due.isoformat(),
                "scheduleDate": schedule.isoformat(),
                "accrualDate": accrual.isoformat(),
                "reference": referencia,
                "description": descricao,
                "isFlagged": ag.get("isFlagged", False),
                "categories": [{"id": ag["categories"][0]["id"]}],
                "costCenterValueType": "0",
                "costcenters": rateio_df.to_dict(orient="records")
            }
            atualizar_pagamento(escolha, payload)
else:
    st.warning("Nenhum agendamento encontrado.")
