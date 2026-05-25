import codecs

def patch_css():
    with codecs.open(r'..\QUARTIL\static\styles.css', 'r', 'utf-8') as f:
        quartil_css = f.read()

    # We will strip out body, *, :root, #sidebar, #topbar, #main
    import re
    
    # Remove all CSS blocks for *, body, #sidebar..., :root
    quartil_css = re.sub(r':root\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'\*,\s*\*\:\:before,\s*\*\:\:after\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'body\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    
    # Remove #sidebar and #main blocks
    quartil_css = re.sub(r'#sidebar\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'\.sidebar-logo.*?\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'#sidebar nav.*?\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'\.nav-item.*?\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'\.sidebar-footer.*?\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'#main\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'#topbar.*?\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'#content\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    
    # Rename .section to .view-section, or just remove .section styling if PAINEL already has it
    quartil_css = re.sub(r'\.section\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    quartil_css = re.sub(r'\.section\.active\s*\{.*?\}', '', quartil_css, flags=re.DOTALL)
    
    # Read existing PAINEL css
    with codecs.open('style.css', 'r', 'utf-8') as f:
        painel_css = f.read()
        
    if "/* ================= QUARTIL STYLES ================= */" in painel_css:
        print("CSS already patched")
        return

    # Add Quartil styles to PAINEL CSS
    new_css = painel_css + "\n\n/* ================= QUARTIL STYLES ================= */\n" + quartil_css
    
    with codecs.open('style.css', 'w', 'utf-8') as f:
        f.write(new_css)
        
    print("CSS patched successfully")

if __name__ == "__main__":
    patch_css()
