import openpyxl

FILES = {
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx'
}

try:
    wb = openpyxl.load_workbook(FILES['TEMPOS'], data_only=True)
    ws = wb['RESUMO']
    
    for row in ws.iter_rows(min_row=1, max_row=30):
        nome = row[0].value
        if nome and "MARIANA MACIEL" in str(nome).upper():
            print(f"--- Found {nome} in row {row[0].row} ---")
            for i, cell in enumerate(row):
                color = cell.font.color
                print(f"Col {i} ({cell.coordinate}): val={cell.value}, type={color.type if color else 'None'}, rgb={color.rgb if color else 'None'}")
except Exception as e:
    print(f"Error: {e}")
