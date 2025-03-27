
# Nibo App - Editor de Agendamentos

Este app em Streamlit permite:

✅ Buscar agendamentos via API do Nibo  
✅ Editar dados (valor, descrição, datas)  
✅ Fazer upload de um Excel com rateio por centro de custo  
✅ Enviar atualização para o Nibo

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura esperada do Excel

| costCenterId | value   |
|--------------|---------|
| UUID1        | 729,20  |
| UUID2        | 1000,00 |

## Variáveis secretas (no Streamlit Cloud)

Em `.streamlit/secrets.toml`:

```
NIBO_API_KEY = "SUA_CHAVE_API_DO_NIBO"
```
