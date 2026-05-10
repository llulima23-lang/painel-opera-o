import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
df = pd.read_excel(r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx', sheet_name='BASE', header=0)
print("=== BASE COLUMNS ===")
for c in df.columns:
    print(f"[{c}]")
