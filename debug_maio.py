import pandas as pd

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    df = pd.read_excel(FILES['META'], sheet_name='METAS MAIO2026', header=3)
    print("--- METAS MAIO2026 Columns ---")
    print(df.columns.tolist())
    
    print("\n--- Data for first 15 agents ---")
    cols_to_show = ['Agente', 'H.O', 'COMISSÃO']
    # Filter columns that exist
    actual_cols = [c for c in df.columns if any(x in str(c).upper() for x in ['AGENTE', 'H.O', 'COMISS'])]
    print(df[actual_cols].head(15).to_string())
    
except Exception as e:
    print(f"Error: {e}")
