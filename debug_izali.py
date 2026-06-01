import pandas as pd
import sys
import unicodedata
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    if not s: return ''
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(s).upper().strip())
        if unicodedata.category(c) != 'Mn'
    )

df = pd.read_excel(r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx', sheet_name='BASE', header=0)
df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
df['_NORM'] = df['AGENTE'].apply(lambda x: normalize(str(x)))

izali = df[df['_NORM'].str.contains('IZALI', na=False)].copy()
izali = izali[izali['DATA'] >= '2026-03-16']

print("=== IZALI DUTRA - BASE ROWS (since 16/03) ===")
cols = ['DATA', 'TEMPO LOGADO', 'META', 'Crédito', 'DEFICT']
print(izali[cols].to_string())

def val_to_sec(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return 0
    if isinstance(v, (int, float)): return int(round(v * 86400))
    if isinstance(v, str):
        parts = v.strip().split(':')
        if len(parts) >= 2:
            try: return int(parts[0])*3600 + int(parts[1])*60 + (int(parts[2]) if len(parts)>2 else 0)
            except: pass
    return 0

total_cred = 0
total_def = 0
for _, row in izali.iterrows():
    c = val_to_sec(row.get('Crédito', 0))
    d = val_to_sec(row.get('DEFICT', 0))
    total_cred += c
    total_def += d

print(f"\nTotal Credit (from columns): {total_cred}s ({total_cred//3600}:{(total_cred%3600)//60:02d}:{total_cred%60:02d})")
print(f"Total Deficit (from columns): {total_def}s ({total_def//3600}:{(total_def%3600)//60:02d}:{total_def%60:02d})")

# Recalculate based on Tempo Logado vs Meta
total_cred_rec = 0
total_def_rec = 0
for _, row in izali.iterrows():
    tl = val_to_sec(row['TEMPO LOGADO'])
    m = val_to_sec(row['META'])
    if tl > m:
        total_cred_rec += (tl - m)
    else:
        total_def_rec += (m - tl)

print(f"\nTotal Credit (Recalculated TL-M): {total_cred_rec}s ({total_cred_rec//3600}:{(total_cred_rec%3600)//60:02d}:{total_cred_rec%60:02d})")
print(f"Total Deficit (Recalculated TL-M): {total_def_rec}s ({total_def_rec//3600}:{(total_def_rec%3600)//60:02d}:{total_def_rec%60:02d})")
