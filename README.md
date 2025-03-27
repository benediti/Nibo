
# Editor de Agendamentos Nibo (com Rateio)

Este é um app em Streamlit para:

- Buscar agendamentos no Nibo
- Editar dados como descrição, datas, valor
- Fazer upload de um Excel com rateio por centro de custo
- Enviar a atualização via API Nibo

## Como rodar

1. Instale as dependências:
```
pip install streamlit pandas openpyxl requests
```

2. Rode o app:
```
streamlit run app.py
```

3. Insira seu token da API do Nibo no código (linha com `TOKEN = "Bearer SEU_TOKEN_AQUI"`)

## Estrutura esperada do Excel de Rateio

| costCenterId                          | value   |
|---------------------------------------|---------|
| 8c7586fa-8f8b-4f48-93cd-115fec84a5cb  | 729,20  |
| outro-id                              | 1000,00 |

- Use `,` como separador decimal.
