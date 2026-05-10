import unicodedata
import sys
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    if not s: return ''
    return ''.join(c for c in unicodedata.normalize('NFD', str(s).upper().strip()) if unicodedata.category(c) != 'Mn')

print(f"[{normalize('Celiane Lourenço')}]")
print(f"[{normalize('Celiane Lourençço')}]")
