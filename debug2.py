import pandas as pd
import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx',
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx',
    'ADM': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\ADM EQUIPES.xlsx'
}

print("="*60)
print("TEMPOS BASE - primeiras 8 linhas raw")
print("="*60)
xls2 = pd.ExcelFile(FILES['TEMPOS'])
df_raw = pd.read_excel(xls2, sheet_name='BASE', header=None, nrows=12)
print(df_raw.to_string())
print()
print("Colunas skiprows=0:")
df0 = pd.read_excel(xls2, sheet_name='BASE', skiprows=0, nrows=3)
print(df0.columns.tolist())
print()
print("Colunas skiprows=3:")
df3 = pd.read_excel(xls2, sheet_name='BASE', skiprows=3, nrows=5)
print(df3.columns.tolist())
print(df3.head(5).to_string())

print("="*60)
print("ADM ESPELHO")
print("="*60)
xls3 = pd.ExcelFile(FILES['ADM'])
df_adm = pd.read_excel(xls3, sheet_name='ESPELHO')
print(df_adm.columns.tolist())
print(df_adm[['Agente', 'Admissão']].head(10).to_string())
