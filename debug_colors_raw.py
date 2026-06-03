import openpyxl

FILES = {
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx'
}

try:
    wb = openpyxl.load_workbook(FILES['TEMPOS'], data_only=True)
    ws = wb['RESUMO']
    
    for row in ws.iter_rows(min_row=1, max_row=10):
        for cell in row:
            if cell.value:
                color = cell.font.color
                if color:
                    print(f"Cell {cell.coordinate}: val={cell.value}, type={color.type}, rgb={color.rgb}, theme={color.theme}, indexed={color.indexed}")
                else:
                    print(f"Cell {cell.coordinate}: val={cell.value}, no color info")
except Exception as e:
    print(f"Error: {e}")
