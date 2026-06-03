import pandas as pd

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    for skip in range(10):
        df = pd.read_excel(FILES['META'], sheet_name='METAS MAIO2026', header=skip, nrows=2)
        print(f"Header={skip} columns: {df.columns.tolist()[:5]}")
except Exception as e:
    print(f"Error: {e}")
