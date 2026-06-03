import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

content = open('data_embedded.js', 'r', encoding='utf-8').read()
data = json.loads(content.replace('const EMBEDDED_DATA = ', '').rstrip().rstrip(';'))

adm_norms = set(a['nome_norm'] for a in data['adm'])
tempo_norms = set(t['nome_norm'] for t in data['tempos'])
comp_norms = set(data.get('compensa', {}).keys())

print('=== NAME MATCHING ISSUES ===')
print('\nIn ADM but NOT in TEMPOS:')
for n in sorted(adm_norms - tempo_norms):
    print(f'  {n}')

print('\nIn TEMPOS but NOT in ADM:')
for n in sorted(tempo_norms - adm_norms):
    print(f'  {n}')

print('\nIn COMPENSA but NOT in ADM:')
for n in sorted(comp_norms - adm_norms):
    print(f'  {n}')

print('\n=== SPECIFIC OPERATORS ===')
for a in data['adm']:
    if any(k in a['nome_norm'] for k in ['CELIANE', 'IZALI', 'NATALIA', 'MILENA', 'GABRIEL', 'CARLA', 'HENRIQUE', 'ROMARIO', 'ERIKA']):
        print(f"  ADM: {a['nome']:45} norm={a['nome_norm']}")

print()
for t in data['tempos']:
    if any(k in t['nome_norm'] for k in ['CELIANE', 'IZALI', 'NATALIA', 'MILENA', 'GABRIEL', 'CARLA', 'HENRIQUE', 'ROMARIO', 'ERIKA']):
        print(f"  TEMPO: {t['nome']:45} norm={t['nome_norm']}  mes={t['mes']}")

# Check Pausa column values
print('\n=== PAUSA VALUES CHECK ===')
for t in sorted(data['tempos'], key=lambda x: x['nome']):
    if t['mes'] == '2026-04':
        print(f"  {t['nome'][:35]:35} pausa={t['media_pausa_pct']}")
