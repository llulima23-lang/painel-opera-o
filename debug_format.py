import openpyxl
import sys
sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx', data_only=False)
ws = wb['BASE']

print("=== ANA LAYS Row Formatting Analysis ===")
for row in ws.iter_rows(min_row=2):
    agente = row[3].value # Column D
    if agente and 'ANA LAYS' in str(agente).upper():
        data = row[0].value
        deficit_cell = row[11] # Column L
        color = None
        if deficit_cell.font and deficit_cell.font.color:
            color = deficit_cell.font.color.rgb
        print(f"Data: {data}, Deficit: {deficit_cell.value}, Color: {color}")
