import os
import sys
import json
import openpyxl
import pandas as pd
import datetime
import unicodedata
import traceback
import time

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
COMPENSA_SEC    = 7 * 3600 + 12 * 60  # 07:12:00 por data compensada



def normalize(s):
    """Remove acentos e converte para maiúsculas para comparação."""
    if not s: return ''
    s = ''.join(
        c for c in unicodedata.normalize('NFD', str(s).upper().strip())
        if unicodedata.category(c) != 'Mn'
    )
    # Remove espaços duplos
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s

def fuzzy_match(name_a, name_b):
    """Verifica se dois nomes normalizados se referem à mesma pessoa.
    Usa lógica: um nome é prefixo do outro, ou compartilham primeiros 2+ termos."""
    if name_a == name_b:
        return True
    if not name_a or not name_b:
        return False
    # Um começa com o outro
    if name_a.startswith(name_b) or name_b.startswith(name_a):
        return True
    # Compara primeiros 2 termos (primeiro nome + sobrenome)
    parts_a = name_a.split()
    parts_b = name_b.split()
    if len(parts_a) >= 2 and len(parts_b) >= 2:
        # Pelo menos primeiro nome + segundo nome iguais e terceiro (se existir)
        if parts_a[0] == parts_b[0] and parts_a[1] == parts_b[1]:
            # Se tem 3+ termos, verificar o terceiro também para evitar falsos positivos
            if len(parts_a) >= 3 and len(parts_b) >= 3:
                return parts_a[2] == parts_b[2]
            return True
    return False

def find_best_match(target_norm, name_set):
    """Encontra o melhor match para um nome normalizado em um set de nomes."""
    if target_norm in name_set:
        return target_norm
    for candidate in name_set:
        if fuzzy_match(target_norm, candidate):
            return candidate
    return None

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
        color = cell.font.color
        if not color: return False
        # Vermelho padrão Excel (RGB: FFFF0000 ou Indexed: 2)
        if color.type == 'rgb' and str(color.rgb).upper() in ('FFFF0000', 'FF0000'):
            return True
        if color.type == 'indexed' and color.indexed == 2:
            return True
        # Tenta extrair RGB se for outro formato
        if color.type == 'rgb' and color.rgb:
            rgb = str(color.rgb).upper()
            if len(rgb) == 8:
                r = int(rgb[2:4], 16)
                g = int(rgb[4:6], 16)
                b = int(rgb[6:8], 16)
                return r > 150 and g < 100 and b < 100
    except: pass
    return False

def process_excel():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Processando planilhas...")

    # ── 1. ADM EQUIPES (cores de fonte para detectar desligados) ──────
    for attempt in range(3):
        try:
            wb_adm  = openpyxl.load_workbook(FILES['ADM'], data_only=True)
            ws_esp  = wb_adm['ESPELHO']
            break
        except Exception as e:
            if attempt == 2: raise e
            print(f"  Aviso: Erro ao abrir ADM (tentativa {attempt+1}): {e}")
            time.sleep(2)
    
    header_map = {str(c.value).strip(): c.column-1 for c in ws_esp[1] if c.value}

    col_nome = header_map.get('Agente',              0)
    col_adm  = header_map.get('Admissão',            3)
    col_mat  = header_map.get('Matricula',            5)
    col_op   = header_map.get('Operação que atua',   16)

    adm_list         = []   # operadores ativos
    desligados_norm  = set()
    operacoes_set    = set()
    adm_norm_set     = set()  # Nomes normalizados dos operadores ativos

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

        nome_norm = normalize(nome)
        adm_norm_set.add(nome_norm)

        adm_list.append({
            'nome':      nome,
            'nome_norm': nome_norm,
            'admissao':  adm_str,
            'matricula': mat_str,
            'operacao':  op_str,
            'foto':      None
        })

    print(f"  ADM: {len(adm_list)} ativos | {len(desligados_norm)} desligados excluidos")
    print(f"  Operacoes: {sorted(operacoes_set)}")

    # ── 1.5 MAPEAMENTO DE FOTOS ──────────────────────────────────────
    import shutil, glob
    fotos_dir_src = r'C:\Users\sup.luciana\Meu Drive\FOTOS EQUIPES'
    fotos_dir_dst = os.path.join(os.path.dirname(__file__), 'fotos')
    os.makedirs(fotos_dir_dst, exist_ok=True)

    image_extensions = ('.jpg', '.jpeg', '.png')
    src_images = []
    for root, dirs, files in os.walk(fotos_dir_src):
        for file in files:
            if file.lower().endswith(image_extensions):
                src_images.append(os.path.join(root, file))

    fotos_found = 0
    for op in adm_list:
        n_norm = op['nome_norm']
        parts = n_norm.split()
        op_first = parts[0] if parts else ''
        best = None

        for img_path in src_images:
            base = normalize(os.path.splitext(os.path.basename(img_path))[0])
            if fuzzy_match(n_norm, base):
                best = img_path
                break
            if op_first and base.startswith(op_first + ' ') and len(parts) > 1 and parts[1] in base:
                best = img_path
                break

        if not best and op_first:
            for img_path in src_images:
                base = normalize(os.path.splitext(os.path.basename(img_path))[0])
                if base == op_first:
                    best = img_path
                    break

        if best:
            ext = os.path.splitext(best)[1].lower()
            safe = op['matricula'] if op['matricula'] else n_norm.replace(' ', '_')
            dst = os.path.join(fotos_dir_dst, f"{safe}{ext}")
            try:
                shutil.copy2(best, dst)
                op['foto'] = f"fotos/{safe}{ext}"
                fotos_found += 1
            except Exception as e:
                print(f"  Erro foto {best}: {e}")

    print(f"  FOTOS: {fotos_found}/{len(adm_list)} encontradas")

    # ── 2. TEMPOS BASE agrupado por operador × mes ────────────────────
    for attempt in range(3):
        try:
            df_base = pd.read_excel(FILES['TEMPOS'], sheet_name='BASE', header=0)
            break
        except Exception as e:
            if attempt == 2: raise e
            print(f"  Aviso: Erro ao abrir TEMPOS (tentativa {attempt+1}): {e}")
            time.sleep(2)
    df_base['DATA'] = pd.to_datetime(df_base['DATA'], errors='coerce')
    df_base = df_base[df_base['DATA'] >= pd.Timestamp(CORTE_BH)].copy()
    df_base['_NORM'] = df_base['AGENTE'].apply(lambda x: normalize(str(x)))

    # Criar mapa de resolução de nomes: TEMPOS -> ADM
    # Para cada nome único no TEMPOS, encontrar o equivalente no ADM
    tempo_names = set(df_base['_NORM'].unique())
    name_resolve = {}  # tempo_norm -> adm_norm
    unmatched_tempos = set()

    for tn in tempo_names:
        if tn in desligados_norm:
            name_resolve[tn] = None  # Desligado, ignorar
            continue
        # Verifica se esse nome de desligado faz match fuzzy
        is_desligado = False
        for dn in desligados_norm:
            if fuzzy_match(tn, dn):
                is_desligado = True
                break
        if is_desligado:
            name_resolve[tn] = None
            continue

        match = find_best_match(tn, adm_norm_set)
        if match:
            name_resolve[tn] = match
        else:
            unmatched_tempos.add(tn)
            name_resolve[tn] = tn  # Usa o próprio nome

    if unmatched_tempos:
        print(f"  ⚠️  Nomes TEMPOS sem match no ADM: {sorted(unmatched_tempos)}")

    # Filtra desligados
    df_base = df_base[df_base['_NORM'].apply(lambda x: name_resolve.get(x) is not None)]
    
    # Resolve nomes para o padrão ADM
    df_base['_NORM_RESOLVED'] = df_base['_NORM'].apply(lambda x: name_resolve.get(x, x))
    df_base['_MES'] = df_base['DATA'].dt.strftime('%Y-%m')
    print(f"  TEMPOS: {len(df_base)} registros a partir de {CORTE_BH}")

    # Detectar nomes de colunas (podem ter variações de acentuação)
    col_credito = None
    col_deficit = None
    col_pausa = None
    col_pausas_total = None
    col_tempo_logado = None
    col_meta = None

    for c in df_base.columns:
        cn = normalize(str(c))
        if cn == 'CREDITO': col_credito = c
        elif cn == 'DEFICT' or cn == 'DEFICIT': col_deficit = c
        elif cn == 'PAUSA' and 'TOTAL' not in cn and 'PAUSAS' not in cn: col_pausa = c
        elif 'PAUSAS TOTAL' in cn or cn == 'PAUSAS TOTAL': col_pausas_total = c
        elif cn == 'TEMPO LOGADO': col_tempo_logado = c
        elif cn == 'META': col_meta = c

    # Fallback names
    if not col_credito: col_credito = 'Crédito'
    if not col_deficit: col_deficit = 'DEFICT'
    if not col_pausa: col_pausa = 'Pausa'
    if not col_pausas_total: col_pausas_total = 'Pausas total'
    if not col_tempo_logado: col_tempo_logado = 'TEMPO LOGADO'
    if not col_meta: col_meta = 'META'

    print(f"  Colunas: credito='{col_credito}', deficit='{col_deficit}', pausa='{col_pausa}', pausas_total='{col_pausas_total}'")

    # agrupamento (nome_norm_resolved, mes) → stats
    monthly_map = {}
    for _, row in df_base.iterrows():
        nome_norm = row['_NORM_RESOLVED']
        mes       = row['_MES']
        key       = (nome_norm, mes)

        tempo_log = val_to_sec(row.get(col_tempo_logado, 0))
        meta_sec  = val_to_sec(row.get(col_meta, None)) or META_PADRAO_SEC

        # Cálculo manual conforme solicitado pela usuária:
        # A diferença entre Tempo Logado e Meta define o crédito ou débito do dia.
        diff = tempo_log - meta_sec
        if diff > 0:
            credito_sec = diff
            deficit_sec = 0
        else:
            credito_sec = 0
            deficit_sec = abs(diff)

        # Pausa % (coluna "Pausa" - é uma fração decimal como 0.123 = 12.3%)
        pausa_pct_val = row.get(col_pausa, None)

        # Pausas total (coluna "Pausas total" - é HH:MM:SS)
        pausas_total_val = row.get(col_pausas_total, None)

        if key not in monthly_map:
            monthly_map[key] = {
                'nome_norm': nome_norm, 'mes': mes,
                'credito': 0, 'deficit': 0, 'dias': 0,
                'total_tempo': 0, 'total_meta': 0,
                'pausa_pct_sum': 0.0, 'pausa_pct_dias': 0,
                'pausas_total_sec': 0, 'pausas_total_dias': 0
            }
        d = monthly_map[key]
        d['credito']    += credito_sec
        d['deficit']    += deficit_sec
        d['dias']       += 1
        d['total_tempo']+= tempo_log
        d['total_meta'] += meta_sec

        # Pausa % - lê e converte
        if pausa_pct_val is not None and not (isinstance(pausa_pct_val, float) and pd.isna(pausa_pct_val)):
            p = float(pausa_pct_val)
            if 0 < abs(p) <= 1.0: p *= 100
            d['pausa_pct_sum'] += p
            d['pausa_pct_dias'] += 1

        # Pausas total (absoluto em segundos)
        if pausas_total_val is not None and not (isinstance(pausas_total_val, float) and pd.isna(pausas_total_val)):
            pt = val_to_sec(pausas_total_val)
            d['pausas_total_sec'] += pt
            d['pausas_total_dias'] += 1

    # Converte para lista com médias calculadas
    tempos_list = []
    # Precisamos do nome "amigável" - pegar do ADM
    adm_name_map = {a['nome_norm']: a['nome'] for a in adm_list}

    for (nome_norm, mes), v in monthly_map.items():
        dias = v['dias'] or 1
        media_tempo = int(v['total_tempo'] / dias)
        media_meta  = int(v['total_meta']  / dias)
        media_pausa_pct = round((v['pausas_total_sec'] / v['total_tempo']) * 100, 2) if v['total_tempo'] > 0 else 0
        media_pausas_total_sec = int(v['pausas_total_sec'] / v['pausas_total_dias']) if v['pausas_total_dias'] > 0 else 0

        nome_display = adm_name_map.get(nome_norm, nome_norm)

        tempos_list.append({
            'nome':             nome_display,
            'nome_norm':        nome_norm,
            'mes':              mes,                     # "2026-03"
            'credito_sec':      v['credito'],
            'deficit_sec':      v['deficit'],
            'dias_trabalhados': v['dias'],
            'media_tempo_sec':  media_tempo,
            'meta_diaria_sec':  media_meta,
            'media_pausa_pct':  media_pausa_pct,
            'media_pausas_total_sec': media_pausas_total_sec,
        })

    print(f"  TEMPOS: {len(tempos_list)} registros mes/operador")

    # ── 2.5 DATA COMPENSA ─────────────────────────────────────────────
    compensa_map = {}  # adm_norm -> list of ISO dates
    try:
        df_comp = pd.read_excel(FILES['TEMPOS'], sheet_name='DATA COMPENSA', header=0)
        for _, row in df_comp.iterrows():
            nome_c = str(row.get('NOME', '')).strip()
            data_c = row.get('DATA', None)
            if not nome_c:
                continue

            n_norm_raw = normalize(nome_c)

            # Resolve para o nome ADM usando fuzzy match
            resolved = find_best_match(n_norm_raw, adm_norm_set)
            if not resolved:
                resolved = n_norm_raw
                print(f"  ⚠️  COMPENSA: '{nome_c}' (norm: {n_norm_raw}) sem match no ADM")

            if resolved not in compensa_map:
                compensa_map[resolved] = []

            # Só adiciona se tem data preenchida
            if pd.notna(data_c) and data_c is not None:
                if isinstance(data_c, (datetime.datetime, datetime.date)):
                    compensa_map[resolved].append(data_c.strftime('%Y-%m-%d'))
                elif isinstance(data_c, str) and data_c.strip():
                    compensa_map[resolved].append(data_c.strip())

        # Remove entradas sem datas
        compensa_map = {k: v for k, v in compensa_map.items() if v}
        print(f"  COMPENSA: {len(compensa_map)} operadores com datas de compensação")
        for k, v in compensa_map.items():
            print(f"    {k}: {v}")
    except Exception as e:
        print(f"  Erro ao ler DATA COMPENSA: {e}")

    # ── 2.7 RESUMO (Banco de Horas Inicial e Saldo Final com cor de fonte) ──
    resumo_map = {} # adm_norm -> bh_inicial_sec
    resumo_saldo_final = {} # adm_norm -> saldo final em sec (coluna F)
    try:
        # Usamos openpyxl para detectar a COR da fonte (vermelho = negativo)
        for attempt in range(3):
            try:
                wb_res = openpyxl.load_workbook(FILES['TEMPOS'], data_only=True)
                ws_res = wb_res['RESUMO']
                break
            except Exception as e:
                if attempt == 2: raise e
                time.sleep(2)

        # Detecta colunas
        header_res = [str(c.value).upper() if c.value else '' for c in ws_res[1]]
        idx_nome = header_res.index('NOME') if 'NOME' in header_res else 0
        
        # Procura coluna de Saldo Final (prioriza o nome exato SALDO FINAL)
        idx_saldo = -1
        # Primeiro tenta o exato
        for i, h in enumerate(header_res):
            if 'SALDO FINAL' == h:
                idx_saldo = i
                break
        # Se não achou, tenta o parcial, mas excluindo DÉBITO FINAL se possível
        if idx_saldo == -1:
            for i, h in enumerate(header_res):
                if 'SALDO FINAL' in h:
                    idx_saldo = i
                    break
        # Se ainda não achou, pega DÉBITO FINAL
        if idx_saldo == -1:
            for i, h in enumerate(header_res):
                if 'DEBITO FINAL' in h or 'DÉBITO FINAL' in h:
                    idx_saldo = i
                    break
        
        if idx_saldo == -1: idx_saldo = 5 # Fallback para coluna F (6ª coluna)

        idx_bh_ini = 3 # Coluna D (banco de horas)

        for row in ws_res.iter_rows(min_row=2, max_row=ws_res.max_row):
            nome_res = str(row[idx_nome].value).strip() if row[idx_nome].value else None
            if not nome_res: continue
            
            n_norm = normalize(nome_res)
            resolved = find_best_match(n_norm, adm_norm_set)
            if not resolved: resolved = n_norm
            
            # Banco de Horas Inicial (Coluna D)
            cell_bh = row[idx_bh_ini]
            val_bh = val_to_sec(cell_bh.value)
            if is_red_font(cell_bh): val_bh = -abs(val_bh)
            resumo_map[resolved] = val_bh
            
            # Saldo Final (Coluna F ou similar)
            cell_saldo = row[idx_saldo]
            val_saldo = val_to_sec(cell_saldo.value)
            if is_red_font(cell_saldo): 
                val_saldo = -abs(val_saldo)
                
            resumo_saldo_final[resolved] = val_saldo

        print(f"  RESUMO: {len(resumo_map)} saldos iniciais | {len(resumo_saldo_final)} saldos finais (com detecção de cor)")
    except Exception as e:
        print(f"  Erro ao ler RESUMO: {e}")
        traceback.print_exc()

    # ── 3. META GERAL (Busca dinâmica de abas) ────────────────────────
    for attempt in range(3):
        try:
            xls_meta = pd.ExcelFile(FILES['META'])
            break
        except Exception as e:
            if attempt == 2: raise e
            print(f"  Aviso: Erro ao abrir META (tentativa {attempt+1}): {e}")
            time.sleep(2)
    # Pega todas as abas que começam com METAS, exceto possíveis backups
    meta_sheets = [s for s in xls_meta.sheet_names if s.startswith('METAS') and 'Backup' not in s]
    meta_data   = {}

    for sh in meta_sheets:
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

            # Verifica desligados com fuzzy match
            is_desligado = False
            for dn in desligados_norm:
                if fuzzy_match(nome_norm, dn):
                    is_desligado = True
                    break
            if is_desligado:
                continue

            # Resolve nome para ADM
            resolved_norm = find_best_match(nome_norm, adm_norm_set)
            if resolved_norm:
                nome_norm = resolved_norm

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

            # Busca dinâmica de colunas para H.O e Comissão (robusto contra espaços/acentos)
            col_ho_name = next((c for c in df.columns if normalize(c) == 'HO'), 'H.O')
            col_com_name = next((c for c in df.columns if normalize(c) == 'COMISSAO'), 'COMISSÃO')
            
            val_ho   = float(row.get(col_ho_name, 0)) if not pd.isna(row.get(col_ho_name)) else 0
            val_com  = float(row.get(col_com_name, 0)) if not pd.isna(row.get(col_com_name)) else 0

            # Pausas (percentual) e Banco de Horas (tempo)
            col_pausa_name = next((c for c in df.columns if normalize(c) == 'PAUSAS' or normalize(c) == 'PAUSA'), 'Pausas')
            pausas_val = row.get(col_pausa_name, 0)
            pausas_pct = float(pausas_val) * 100 if not pd.isna(pausas_val) else 0

            rows.append({
                'nome':      nome_str,
                'nome_norm': nome_norm,
                'matricula': mat_str,
                'promessas': float(promessas) if promessas is not None and not (isinstance(promessas,float) and pd.isna(promessas)) else 0,
                'meta_prom': float(meta_prom)  if meta_prom  is not None and not (isinstance(meta_prom, float) and pd.isna(meta_prom))  else 0,
                'qualidade': qualidade,
                'abs_dias':  abs_dias,
                'ho': val_ho, 
                'comissao': val_com,
                'pausas': pausas_pct,
                'banco_horas': val_to_sec(row.get('Banco de horas', 0))
            })
        meta_data[sh] = {'rows': rows, 'du': du_val}
        print(f"  META {sh}: {len(rows)} ativos, D.U={du_val}")

    # ── Debug: mostra saldos finais ───────────────────────────────────
    print("\n  === SALDOS BANCO DE HORAS ===")
    bh_totals = {}
    for t in tempos_list:
        nn = t['nome_norm']
        if nn not in bh_totals:
            bh_totals[nn] = {'nome': t['nome'], 'credito': 0, 'deficit': 0}
        bh_totals[nn]['credito'] += t['credito_sec']
        bh_totals[nn]['deficit'] += t['deficit_sec']

    def sec_fmt(s):
        neg = s < 0
        s = abs(int(s))
        h = s // 3600; m = (s % 3600) // 60; ss = s % 60
        return ('-' if neg else '') + f'{h:02d}:{m:02d}:{ss:02d}'

    for nn in sorted(bh_totals.keys()):
        bh = bh_totals[nn]
        comp_dates = compensa_map.get(nn, [])
        comp_sec = len(comp_dates) * COMPENSA_SEC
        saldo = bh['credito'] - bh['deficit'] - comp_sec
        print(f"    {bh['nome'][:35]:35} C={sec_fmt(bh['credito']):>10} D={sec_fmt(bh['deficit']):>10} Comp={len(comp_dates)}x07:12={sec_fmt(comp_sec):>10} SALDO={sec_fmt(saldo):>10}")

    # ── Salva ─────────────────────────────────────────────────────────
    output = {
        'meta':       meta_data,
        'tempos':     tempos_list,
        'adm':        adm_list,
        'compensa':   compensa_map,
        'resumo':     resumo_map,
        'resumo_saldo_final': resumo_saldo_final,
        'operacoes':  sorted(operacoes_set),
        'updated_at': datetime.datetime.now().isoformat()
    }
    js_content = f"var EMBEDDED_DATA = {json.dumps(output, ensure_ascii=False, default=str, indent=4)};\n"
    with open(JS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"\n  OK! data_embedded.js gerado com sucesso! ({datetime.datetime.now().strftime('%H:%M:%S')})")

if __name__ == "__main__":
    process_excel()
