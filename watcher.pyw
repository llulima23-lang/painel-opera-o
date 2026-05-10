import os
import sys
import time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Importa tudo do gerar_dados
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_dados
import datetime

FILES = gerar_dados.FILES

def watch_files():
    last_mtimes = {k: os.path.getmtime(v) if os.path.exists(v) else 0 for k, v in FILES.items()}
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Monitorando planilhas... (Ctrl+C para parar)")

    while True:
        try:
            time.sleep(5)
            changed = False
            for k, v in FILES.items():
                if os.path.exists(v):
                    mtime = os.path.getmtime(v)
                    if mtime != last_mtimes.get(k, 0):
                        last_mtimes[k] = mtime
                        changed = True
            if changed:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Alteracao detectada, atualizando...")
                time.sleep(1) # Pequena pausa para garantir que o Excel soltou o arquivo
                gerar_dados.process_excel()
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Erro no monitoramento: {e}")
            time.sleep(5)

if __name__ == "__main__":
    gerar_dados.process_excel()
    watch_files()
