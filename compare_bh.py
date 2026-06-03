import json
import os

bh_path = r'C:\Users\sup.luciana\Desktop\AntiGravity\BANCO DE HORAS\data.json'
po_path = r'C:\Users\sup.luciana\Desktop\AntiGravity\PAINEL OPERAÇÃO\data_embedded.js'

def fmt(s):
    neg = s < 0
    s = abs(int(s))
    h = s // 3600
    m = (s % 3600) // 60
    return ('-' if neg else '') + f"{h:02d}:{m:02d}:{s%60:02d}"

print('=== COMPARISON: BANCO DE HORAS ===')
if os.path.exists(bh_path):
    with open(bh_path, 'r', encoding='utf-8') as f:
        bh_data = json.load(f)
    
    for target in ['ANA LAYS', 'IZALI', 'YURI ANDREWS']:
        cred, defic, p_total, tempo = 0, 0, 0, 0
        for r in bh_data['records']:
            if target in str(r['agente']).upper() and r['data'] >= '2026-03-16':
                cred += r.get('credito', 0) or 0
                defic += r.get('deficit', 0) or 0
                p_total += r.get('pausas_total', 0) or 0
                tempo += r.get('tempo_logado', 0) or 0
        
        comp_dates = [d for d in bh_data.get('data_compensa', []) if target in str(d['nome']).upper() and d.get('data')]
        comp_sec = len(comp_dates) * 25920
        
        print(f'{target}:')
        print(f'  Credito: {fmt(cred)}')
        print(f'  Deficit: {fmt(defic)}')
        print(f'  Compensa: {len(comp_dates)}x ({fmt(comp_sec)})')
        print(f'  Saldo (C-D-Comp): {fmt(cred - defic - comp_sec)}')
        print(f'  Pausa %: {round(p_total/tempo*100, 2) if tempo > 0 else 0}%')
else:
    print("BANCO DE HORAS/data.json not found")

