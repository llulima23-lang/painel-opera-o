import sys, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
ADM = r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\ADM EQUIPES.xlsx'
df = pd.read_excel(ADM, sheet_name='ESPELHO')
print("Colunas:", df.columns.tolist())
print("\nOperacoes unicas:")
print(df['Operação que atua'].dropna().unique())
print("\nPrimeiras 5 linhas:")
print(df[['Agente','Admissão','Matricula','Operação que atua']].head(5).to_string())
