import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data_embedded.js', 'r', encoding='utf-8') as f:
    content = f.read().replace('const EMBEDDED_DATA = ', '').strip().rstrip(';')

data = json.loads(content)
tempos = data.get('tempos', [])
compensa = data.get('compensa', {})

def check_op(name_part):
    ops = [t for t in tempos if name_part in t['nome_norm']]
    print(f"\n=== Data for {name_part} ===")
    total_cred = 0
    total_def = 0
    for t in ops:
        print(f"Mes: {t['mes']}, Credito: {t['credito_sec']}s, Deficit: {t['deficit_sec']}s")
        total_cred += t['credito_sec']
        total_def += t['deficit_sec']
    
    comp_dates = []
    for k, v in compensa.items():
        if name_part in k:
            comp_dates = v
            break
            
    print(f"Total Credito: {total_cred}s")
    print(f"Total Deficit (BASE): {total_def}s")
    print(f"Compensa dates: {comp_dates} ({len(comp_dates)} days)")
    
    extra_def = len(comp_dates) * 25920
    print(f"Extra Deficit (Compensa): {extra_def}s")
    print(f"Total Saldo (C - D_base - D_comp): {total_cred - total_def - extra_def}s")

check_op('CELIANE LOURENCO')
check_op('IZALI DUTRA')
