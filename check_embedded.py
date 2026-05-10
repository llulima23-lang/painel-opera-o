import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

content = open('data_embedded.js', 'r', encoding='utf-8').read()
data = json.loads(content.replace('const EMBEDDED_DATA = ', '').rstrip().rstrip(';'))

tempos = data['tempos']
print('=== EMBEDDED TEMPOS DATA ===')
for t in sorted(tempos, key=lambda x: x['nome_norm']+x['mes']):
    print(f"  {t['nome'][:35]:35} | {t['mes']} | cred={t['credito_sec']:>7} | def={t['deficit_sec']:>7} | pausa={t['media_pausa_pct']:>6} | dias={t['dias_trabalhados']}")

print('\n=== EMBEDDED COMPENSA DATA ===')
comp = data.get('compensa', {})
for k, v in comp.items():
    print(f"  {k}: {v}")

print('\n=== KEY OPERATORS CHECK ===')
# Sum credito/deficit by operator across all months
from collections import defaultdict
ops = defaultdict(lambda: {'credito': 0, 'deficit': 0})
for t in tempos:
    ops[t['nome_norm']]['credito'] += t['credito_sec']
    ops[t['nome_norm']]['deficit'] += t['deficit_sec']
    ops[t['nome_norm']]['nome'] = t['nome']

for n in sorted(ops.keys()):
    d = ops[n]
    saldo = d['credito'] - d['deficit']
    neg = '-' if saldo < 0 else ''
    s = abs(saldo)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    print(f"  {d['nome'][:35]:35} | cred={d['credito']:>7}s | def={d['deficit']:>7}s | saldo={neg}{h:02d}:{m:02d}:{sec:02d}")
