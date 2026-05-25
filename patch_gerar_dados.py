import json
import codecs

def patch():
    with codecs.open('gerar_dados.py', 'r', 'utf-8') as f:
        content = f.read()
    
    if "def calcular_quartis(" in content:
        print("Already patched.")
        return

    insert_logic = """
    # ── 6. CÁLCULO DINÂMICO DE QUARTIS E DISPERSÃO ────────────────────
    def calcular_quartis(meta_data, adm_list):
        import numpy as np
        
        # Mapear operações
        op_map = {a['nome_norm']: a['operacao'] for a in adm_list if a.get('operacao')}
        
        quartil_result = {}
        
        for mes_key, mes_info in meta_data.items():
            rows = mes_info.get('rows', [])
            
            # Separar por operação
            ops = {}
            for r in rows:
                if not r.get('nome_norm'): continue
                op = op_map.get(r['nome_norm'], 'Desconhecida')
                if op not in ops:
                    ops[op] = []
                ops[op].append(r)
                
            resultados_mes = []
            carteiras_list = []
            
            # Para médias gerais
            all_valid_ho = []
            all_valid_prom = []
            
            for op_name, op_rows in ops.items():
                # Validos = ho > 0
                validos = [r for r in op_rows if r.get('ho', 0) > 0]
                
                ho_n = len(validos)
                if ho_n == 0: continue
                
                # ho dispersão/quartil
                validos.sort(key=lambda x: x.get('ho', 0), reverse=True)
                ho_max = max(x.get('ho', 0) for x in validos)
                
                for rank, r in enumerate(validos):
                    pct = rank / max(1, ho_n - 1)
                    if ho_n <= 1: q = 1
                    elif pct <= 0.25: q = 1
                    elif pct <= 0.50: q = 2
                    elif pct <= 0.75: q = 3
                    else: q = 4
                    
                    r['_q_ho'] = f"{q}º Quartil"
                    r['_disp_ho'] = round((r.get('ho', 0) / ho_max * 100), 1) if ho_max > 0 else 0
                    all_valid_ho.append(r.get('ho', 0))
                    
                # promessas dispersão/quartil
                validos_prom = [r for r in validos if r.get('promessas') is not None]
                prom_n = len(validos_prom)
                validos_prom.sort(key=lambda x: x.get('promessas', 0), reverse=True)
                prom_max = max((x.get('promessas', 0) for x in validos_prom), default=0)
                
                for rank, r in enumerate(validos_prom):
                    pct = rank / max(1, prom_n - 1)
                    if prom_n <= 1: q = 1
                    elif pct <= 0.25: q = 1
                    elif pct <= 0.50: q = 2
                    elif pct <= 0.75: q = 3
                    else: q = 4
                    
                    r['_q_prom'] = f"{q}º Quartil"
                    r['_disp_prom'] = round((r.get('promessas', 0) / prom_max * 100), 1) if prom_max > 0 else 0
                    all_valid_prom.append(r.get('promessas', 0))
                
                # Resumo da carteira (Operação)
                def media(lst): return round(float(np.mean(lst)), 2) if lst else 0.0
                
                def get_vals(q_val, key, disp=True):
                    if disp: return [x.get(f'_disp_{key}') for x in validos if x.get(f'_q_{key}') == q_val and f'_disp_{key}' in x]
                    else: return [x.get(key) for x in validos if x.get(f'_q_{key}') == q_val and key in x]
                
                ho_disp = {f"{q}º Quartil": media(get_vals(f"{q}º Quartil", "ho", True)) for q in range(1,5)}
                ho_prod = {f"{q}º Quartil": media(get_vals(f"{q}º Quartil", "ho", False)) for q in range(1,5)}
                
                prom_disp = {f"{q}º Quartil": media(get_vals(f"{q}º Quartil", "prom", True)) for q in range(1,5)}
                prom_prod = {f"{q}º Quartil": media(get_vals(f"{q}º Quartil", "prom", False)) for q in range(1,5)}

                carteira_stats = {
                    "operacao": op_name,
                    "media_ho": media([x.get('ho') for x in validos]),
                    "media_dispersao_ho": media([x.get('_disp_ho') for x in validos if '_disp_ho' in x]),
                    "ho_quartil_disp": ho_disp,
                    "ho_quartil_prod": ho_prod,
                    "media_promessas": media([x.get('promessas') for x in validos_prom]),
                    "media_dispersao_promessas": media([x.get('_disp_prom') for x in validos_prom if '_disp_prom' in x]),
                    "prom_quartil_disp": prom_disp,
                    "prom_quartil_prod": prom_prod,
                    "qtd_agentes": ho_n
                }
                carteiras_list.append(carteira_stats)
                
                for r in validos:
                    # Injetar os valores direto em r
                    r['quartil_ho'] = r.get('_q_ho')
                    r['dispersao_ho'] = r.get('_disp_ho')
                    r['quartil_promessas'] = r.get('_q_prom')
                    r['dispersao_promessas'] = r.get('_disp_prom')
                    
                    # E também na lista legada
                    resultados_mes.append({
                        "Matricula": r.get('matricula', '—'),
                        "Agente": r.get('nome', '—'),
                        "Operacao": op_name,
                        "HO": r.get('ho'),
                        "Quartil_HO": r.get('_q_ho', '—'),
                        "Dispersao_HO": r.get('_disp_ho'),
                        "Promessas": r.get('promessas'),
                        "Quartil_Promessas": r.get('_q_prom', '—'),
                        "Dispersao_Promessas": r.get('_disp_prom')
                    })
                    
            stats_geral = {
                "total_agentes": len(all_valid_ho),
                "media_ho": media(all_valid_ho),
                "media_promessas": media(all_valid_prom),
                "operacoes": sorted(list(ops.keys())),
                "carteiras": carteiras_list
            }
            
            quartil_result[mes_key] = {
                "data": resultados_mes,
                "stats": stats_geral
            }
            
        return quartil_result

    quartil_data = calcular_quartis(meta_data, adm_list)
"""

    parts = content.split("output = {")
    new_content = parts[0] + insert_logic + "\n    output = {" + parts[1]
    
    # Inject quartil_data into output
    parts2 = new_content.split("'operacoes':  sorted(operacoes_set),")
    new_content2 = parts2[0] + "'operacoes':  sorted(operacoes_set),\n        'quartil_data': quartil_data," + parts2[1]

    with codecs.open('gerar_dados.py', 'w', 'utf-8') as f:
        f.write(new_content2)
    print("Patched successfully.")

if __name__ == "__main__":
    patch()
