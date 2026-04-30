import os
import sys
import json
import openpyxl
import pandas as pd
import datetime
import unicodedata
import traceback

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

FILES = {
    'META': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\META GERAL 2026.xlsx',
    'TEMPOS': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\TEMPOS 2026.xlsx',
    'ADM': r'C:\Users\sup.luciana\Meu Drive\MF\MF\Indicadores de Cobrança\ADM EQUIPES.xlsx'
}
JS_OUTPUT = r'C:\Users\sup.luciana\Desktop\AntiGravity\PAINEL OPERAÇÃO\data_embedded.js'

CORTE_BH = datetime.date(2026, 3, 16)
META_PADRAO_SEC = 7 * 3600 + 12 * 60  # 07:12:00

# Lista de feriados 2026 para o JS exibir como checkboxes
FERIADOS_2026 = [
    {"data": "2026-03-19", "nome": "São José (CE)",           "debito_sec": 4320},
    {"data": "2026-03-25", "nome": "Data Magna do Ceará",     "debito_sec": 4320},
    {"data": "2026-04-03", "nome": "Paixão de Cristo",        "debito_sec": 4320},
    {"data": "2026-04-21", "nome": "Tiradentes",              "debito_sec": 4320},
    {"data": "2026-05-01", "nome": "Dia do Trabalho",         "debito_sec": 4320},
    {"data": "2026-06-04", "nome": "Corpus Christi",          "debito_sec": 4320},
    {"data": "2026-08-15", "nome": "N. Sra. Assunção",        "debito_sec": 4320},
    {"data": "2026-09-07", "nome": "Independência",           "debito_sec": 4320},
    {"data": "2026-10-12", "nome": "N. Sra. Aparecida",       "debito_sec": 4320},
    {"data": "2026-11-02", "nome": "Finados",                 "debito_sec": 4320},
    {"data": "2026-11-15", "nome": "Proclamação da República","debito_sec": 4320},
    {"data": "2026-12-25", "nome": "Natal",                   "debito_sec": 4320},
]

def normalize(s):
    if not s: return ''
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(s).upper().strip())
        if unicodedata.category(c) != 'Mn'
    )

def val_to_sec(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return 0
    if isinstance(v, datetime.timedelta): return int(v.total_seconds())
    if isinstance(v, datetime.time):      return v.hour*3600 + v.minute*60 + v.second
    if isinstance(v, datetime.datetime):  return v.hour*3600 + v.minute*60 + v.second
    if isinstance(v, float):              return int(round(v * 86400))
    if isinstance(v, str):
        parts = v.strip().split(':')
        if len(parts) >= 2:
            try: return int(parts[0])*3600 + int(parts[1])*60 + (int(parts[2]) if len(parts)>2 else 0)
            except: pass
    return 0

def safe_pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    f = float(v)
    return round(f*100, 2) if 0 < abs(f) <= 1.0 else round(f, 2)

def is_red_font(cell):
    try:
        if cell.font and cell.font.color and cell.font.color.type == 'rgb':
            rgb = cell.font.color.rgb
            r, g, b = int(rgb[2:4],16), int(rgb[4:6],16), int(rgb[6:8],16)
            return r > 150 and g < 100 and b < 100
    except: pass
    return False

def process_excel():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Processando planilhas...")

    # ── 1. ADM EQUIPES (cores de fonte para detectar desligados) ──────
    wb_adm  = openpyxl.load_workbook(FILES['ADM'])
    ws_esp  = wb_adm['ESPELHO']
    header_map = {str(c.value).strip(): c.column-1 for c in ws_esp[1] if c.value}

    col_nome = header_map.get('Agente',              0)
    col_adm  = header_map.get('Admissão',            3)
    col_mat  = header_map.get('Matricula',            5)
    col_op   = header_map.get('Operação que atua',   16)

    adm_list         = []   # operadores ativos
    desligados_norm  = set()
    operacoes_set    = set()

    for row in ws_esp.iter_rows(min_row=2, max_row=ws_esp.max_row):
        nome_cell = row[col_nome]
        nome = nome_cell.value
        if not nome: continue
        nome = str(nome).strip()

        if is_red_font(nome_cell):
            desligados_norm.add(normalize(nome))
            continue

        adm_val = row[col_adm].value if col_adm < len(row) else None
        mat_val = row[col_mat].value if col_mat < len(row) else None
        op_val  = row[col_op].value  if col_op  < len(row) else None

        adm_str = (adm_val.strftime('%Y-%m-%d') if isinstance(adm_val, (datetime.datetime, datetime.date))
                   else str(adm_val) if adm_val else None)
        mat_str = None
        if mat_val is not None:
            try:   mat_str = str(int(float(mat_val)))
            except: mat_str = str(mat_val)

        op_str = str(op_val).strip() if op_val else None
        if op_str: operacoes_set.add(op_str)

        adm_list.append({
            'nome':      nome,
            'nome_norm': normalize(nome),
            'admissao':  adm_str,
            'matricula': mat_str,
            'operacao':  op_str
        })

    print(f"  ADM: {len(adm_list)} ativos | {len(desligados_norm)} desligados excluidos")
    print(f"  Operacoes: {sorted(operacoes_set)}")

    # ── 2. TEMPOS BASE agrupado por operador × mes ────────────────────
    df_base = pd.read_excel(FILES['TEMPOS'], sheet_name='BASE', header=0)
    df_base['DATA'] = pd.to_datetime(df_base['DATA'], errors='coerce')
    df_base = df_base[df_base['DATA'] >= pd.Timestamp(CORTE_BH)].copy()
    df_base['_NORM'] = df_base['AGENTE'].apply(lambda x: normalize(str(x)))
    df_base = df_base[~df_base['_NORM'].isin(desligados_norm)]
    df_base['_MES'] = df_base['DATA'].dt.strftime('%Y-%m')
    print(f"  TEMPOS: {len(df_base)} registros a partir de {CORTE_BH}")

    # agrupamento (nome_norm, mes) → stats
    monthly_map = {}
    for _, row in df_base.iterrows():
        nome     = str(row['AGENTE']).strip()
        nome_norm= normalize(nome)
        mes      = row['_MES']
        key      = (nome_norm, mes)

        tempo_log = val_to_sec(row.get('TEMPO LOGADO', 0))
        meta_sec  = val_to_sec(row.get('META', None)) or META_PADRAO_SEC

        # Recalcula crédito/déficit pela meta real
        credito_sec = max(0, tempo_log - meta_sec)
        deficit_sec = max(0, meta_sec  - tempo_log)

        pausa_pct = row.get('Pausa', None)

        if key not in monthly_map:
            monthly_map[key] = {
                'nome': nome, 'nome_norm': nome_norm, 'mes': mes,
                'credito': 0, 'deficit': 0, 'dias': 0,
                'total_tempo': 0, 'total_meta': 0,
                'total_pausa_pct': 0.0, 'pausa_dias': 0
            }
        d = monthly_map[key]
        d['credito']    += credito_sec
        d['deficit']    += deficit_sec
        d['dias']       += 1
        d['total_tempo']+= tempo_log
        d['total_meta'] += meta_sec

        if pausa_pct is not None and not (isinstance(pausa_pct, float) and pd.isna(pausa_pct)):
            p = float(pausa_pct)
            if 0 < abs(p) <= 1.0: p *= 100
            d['total_pausa_pct'] += p
            d['pausa_dias']      += 1

    # Converte para lista com médias calculadas
    tempos_list = []
    for (nome_norm, mes), v in monthly_map.items():
        dias = v['dias'] or 1
        media_tempo = int(v['total_tempo'] / dias)
        media_meta  = int(v['total_meta']  / dias)
        media_pausa = round(v['total_pausa_pct'] / v['pausa_dias'], 2) if v['pausa_dias'] > 0 else 0
        tempos_list.append({
            'nome':            v['nome'],
            'nome_norm':       nome_norm,
            'mes':             mes,                     # "2026-03"
            'credito_sec':     v['credito'],
            'deficit_sec':     v['deficit'],
            'dias_trabalhados':v['dias'],
            'media_tempo_sec': media_tempo,
            'meta_diaria_sec': media_meta,
            'media_pausa_pct': media_pausa,
        })

    print(f"  TEMPOS: {len(tempos_list)} registros mes/operador")

    # ── 3. META GERAL ─────────────────────────────────────────────────
    meta_sheets = ['METAS JANEIRO2026','METAS FEVEREIRO2026','METAS MARÇO2026','METAS ABRIL2026']
    meta_data   = {}
    xls_meta    = pd.ExcelFile(FILES['META'])

    for sh in meta_sheets:
        if sh not in xls_meta.sheet_names: continue
        df_raw = pd.read_excel(xls_meta, sheet_name=sh, header=None, nrows=4)
        du_val = None
        for r in range(df_raw.shape[0]):
            for c in range(df_raw.shape[1]-1):
                if str(df_raw.iloc[r,c]).strip() == 'D.U':
                    try: du_val = int(df_raw.iloc[r,c+1])
                    except: pass
        df = pd.read_excel(xls_meta, sheet_name=sh, header=3)
        rows = []
        for _, row in df.iterrows():
            nome = row.get('Agente', None)
            if not nome or str(nome).strip() in ('','nan','None'): continue
            nome_str  = str(nome).strip()
            nome_norm = normalize(nome_str)
            if nome_norm in desligados_norm: continue

            promessas = row.get('PROMESSAS', None)
            meta_prom = row.get('META PROM', None)
            qualidade = safe_pct(row.get('QUALIDADE', None))
            abs_col   = next((c for c in df.columns if str(c).upper().startswith('ABS')), None)
            abs_dias  = float(row[abs_col]) if abs_col and not pd.isna(row.get(abs_col)) else 0
            mat_val   = row.get('Matricula', None)
            mat_str   = None
            if mat_val is not None and not (isinstance(mat_val, float) and pd.isna(mat_val)):
                try:   mat_str = str(int(float(mat_val)))
                except: mat_str = str(mat_val)

            rows.append({
                'nome':      nome_str,
                'nome_norm': nome_norm,
                'matricula': mat_str,
                'promessas': float(promessas) if promessas is not None and not (isinstance(promessas,float) and pd.isna(promessas)) else 0,
                'meta_prom': float(meta_prom)  if meta_prom  is not None and not (isinstance(meta_prom, float) and pd.isna(meta_prom))  else 0,
                'qualidade': qualidade,
                'abs_dias':  abs_dias,
            })
        meta_data[sh] = {'rows': rows, 'du': du_val}
        print(f"  META {sh}: {len(rows)} ativos, D.U={du_val}")

    # ── Salva ─────────────────────────────────────────────────────────
    output = {
        'meta':       meta_data,
        'tempos':     tempos_list,
        'adm':        adm_list,
        'feriados':   FERIADOS_2026,
        'operacoes':  sorted(operacoes_set),
        'updated_at': datetime.datetime.now().isoformat()
    }
    js_content = f"const EMBEDDED_DATA = {json.dumps(output, ensure_ascii=False, default=str)};\n"
    with open(JS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("  OK! data_embedded.js gerado com sucesso!")

if __name__ == "__main__":
    process_excel()
