import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    html = f.read()

ids_to_check = [
    'filterOp', 'filterQuartilHO', 'filterQuartilPromessa', 'searchAgent',
    'kpiTotalAgentes', 'kpiMediaHO', 'kpiMediaPromessas', 'kpiTotalOperacoes',
    'q1Count', 'q2Count', 'q3Count', 'q4Count', 'agentsGrid',
    'q4TotalOperadores', 'q4MediaDispersao', 'q4StatusMeta', 'q4StatusMetaSub',
    'q4ImpactoEstimado', 'q4OperatorsTableBody', 'carteirasGrid'
]

for id_str in ids_to_check:
    found = f'id="{id_str}"' in html or f"id='{id_str}'" in html
    print(f"{id_str}: {'Found' if found else 'MISSING'}")
