import pandas as pd

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    df = pd.read_excel(FILES['META'], sheet_name='METAS MAIO2026', header=3)
    print("--- ALL COLUMNS for row 7 (Antônio Yuri) ---")
    row = df.iloc[6] # Antônio Yuri is index 6 in the 0-indexed df (row 7 in raw)
    for col in df.columns:
        print(f"{col}: {row[col]}")
except Exception as e:
    print(f"Error: {e}")
