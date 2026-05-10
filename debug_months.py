import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
df = pd.read_excel(r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx', sheet_name='BASE', header=0)
izali = df[df['AGENTE'].astype(str).str.upper().str.contains('IZALI', na=False)]
print("=== IZALI Month Analysis ===")
for idx, row in izali.iterrows():
    print(f"Data: {row['DATA']}, Mês: {row['Mês']}, Defict: {row['DEFICT']}")
