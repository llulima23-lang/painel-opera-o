import pandas as pd

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    xls = pd.ExcelFile(FILES['META'])
    sheet_name = [s for s in xls.sheet_names if 'REGRAS' in s.upper()][0]
    df = pd.read_excel(xls, sheet_name=sheet_name)
    print(f"--- {sheet_name} ---")
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
