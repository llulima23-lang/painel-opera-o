import openpyxl

FILES = {
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx'
}

try:
    wb = openpyxl.load_workbook(FILES['TEMPOS'], data_only=True)
    ws = wb['RESUMO']
    
    for row in ws.iter_rows(min_row=1, max_row=30):
        nome = row[0].value
        cell_saldo = row[5] # Coluna F
        color = cell_saldo.font.color
        if color and (color.rgb == 'FFFF0000' or color.indexed == 2):
            print(f"RED FOUND: {nome} | Val={cell_saldo.value} | RGB={color.rgb} | Indexed={color.indexed}")
except Exception as e:
    print(f"Error: {e}")
