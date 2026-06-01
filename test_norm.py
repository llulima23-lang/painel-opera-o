import sys
sys.stdout.reconfigure(encoding='utf-8')
import unicodedata

def normalize(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', str(s).upper().strip()) if unicodedata.category(c) != 'Mn')
    s = s.replace('CC', 'C')
    return s

# Test the CC replace issue
tests = [
    'Celiane Lourenço de Sousa',
    'Celiane Lourençço',
    'Izali Dutra da Cunha Magalhães',
    'IZALI DUTRA DA CUNHA',
    'Maria Natalia Farias',
    'MARIA NATALIA FARIAS SILVA',
]
for t in tests:
    print(f"  '{t}' -> '{normalize(t)}'")

# The CC -> C replacement is WRONG! It strips valid CC from names
# like "LOURENÇÇO" -> "LOURENCO" (good) but also "RACCOON" -> "RAOON" (bad)
# More importantly, "Celiane Lourenço de Sousa" -> after NFD stripping becomes
# "CELIANE LOURENCO DE SOUSA" and then CC->C makes it "CELIANE LOURENCO DE SOUSA" (no change since single C)
# But "Celiane Lourençço" (DATA COMPENSA) -> after NFD: "CELIANE LOURENCCO" -> CC->C -> "CELIANE LOURENCO"
# So they should match... let me check

print("\nDirect test:")
print(f"  BASE:     '{normalize('Celiane Lourenço de Sousa')}'")
print(f"  COMPENSA: '{normalize('Celiane Lourençço')}'")
print(f"  Match: {normalize('Celiane Lourenço de Sousa') == normalize('Celiane Lourençço')}")

# Problem: "Celiane Lourenço de Sousa" vs "Celiane Lourençço" 
# The BASE name has full name with "de Sousa" but COMPENSA just has short name
