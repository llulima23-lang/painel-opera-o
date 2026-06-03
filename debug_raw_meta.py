import pandas as pd

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    df_raw = pd.read_excel(FILES['META'], sheet_name='METAS MAIO2026', header=None, nrows=10)
    print("--- First 10 rows (header=None) ---")
    print(df_raw.to_string())
except Exception as e:
    print(f"Error: {e}")
