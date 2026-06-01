import pandas as pd
import sys

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx'
}

try:
    xls = pd.ExcelFile(FILES['META'])
    print(f"Sheets: {xls.sheet_names}")
    for sh in xls.sheet_names:
        if sh.startswith('METAS') and 'Backup' not in sh:
            print(f"\n--- Checking sheet: {sh} ---")
            df = pd.read_excel(xls, sheet_name=sh, header=3)
            print(f"Columns: {[repr(c) for c in df.columns]}")
            
            # Search for 'COMISSÃO' with case-insensitive and space-ignoring
            target = None
            for c in df.columns:
                if 'COM' in str(c).upper() and 'MISS' in str(c).upper():
                    target = c
                    break
            
            if target:
                print(f"Found column: {repr(target)}")
                # Show first 20 rows of this column where it's not NaN
                not_null = df[df[target].notnull()]
                if not not_null.empty:
                    print("First 10 non-null values:")
                    print(not_null[['Agente', target]].head(10))
                else:
                    print("All values in this column are NULL for this sheet (in the first rows or everywhere)")
                    print("Showing first 10 rows of the sheet for context:")
                    print(df[['Agente', target]].head(10))
            else:
                print("COMMISSION column NOT FOUND")
except Exception as e:
    print(f"Error: {e}")
