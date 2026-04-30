import pandas as pd
import datetime

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx',
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx',
    'ADM': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\ADM EQUIPES.xlsx'
}

print("="*60)
print("INSPECIONANDO META GERAL 2026 - METAS ABRIL2026")
print("="*60)
xls = pd.ExcelFile(FILES['META'])
print("Sheets disponíveis:", xls.sheet_names)
for sh in ['METAS JANEIRO2026', 'METAS FEVEREIRO2026', 'METAS MARÇO2026', 'METAS ABRIL2026']:
    if sh in xls.sheet_names:
        print(f"\n--- Sheet: {sh} ---")
        # Tenta sem skip
        for skip in [0, 1, 2]:
            df = pd.read_excel(xls, sheet_name=sh, skiprows=skip, nrows=5)
            print(f"  skiprows={skip}: {df.columns.tolist()}")
        # Mostra primeiras 5 linhas sem skip
        df_raw = pd.read_excel(xls, sheet_name=sh, header=None, nrows=10)
        print(f"  Primeiras 10 linhas (raw):")
        print(df_raw.to_string())

print("\n")
print("="*60)
print("INSPECIONANDO TEMPOS 2026 - BASE")
print("="*60)
xls2 = pd.ExcelFile(FILES['TEMPOS'])
print("Sheets disponíveis:", xls2.sheet_names)
if 'BASE' in xls2.sheet_names:
    for skip in [0, 1, 2]:
        df = pd.read_excel(xls2, sheet_name='BASE', skiprows=skip, nrows=3)
        print(f"  skiprows={skip}: {df.columns.tolist()}")
    df_raw = pd.read_excel(xls2, sheet_name='BASE', header=None, nrows=8)
    print("Primeiras 8 linhas (raw):")
    print(df_raw.to_string())

print("\n")
print("="*60)
print("INSPECIONANDO ADM EQUIPES - ESPELHO")
print("="*60)
xls3 = pd.ExcelFile(FILES['ADM'])
print("Sheets disponíveis:", xls3.sheet_names)
if 'ESPELHO' in xls3.sheet_names:
    df = pd.read_excel(xls3, sheet_name='ESPELHO', nrows=5)
    print("Colunas:", df.columns.tolist())
    print(df[['Agente','Admissão']].head(5).to_string() if 'Agente' in df.columns else df.head(5).to_string())
