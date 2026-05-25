import codecs
import re

def rebuild_css():
    with codecs.open('style.css', 'r', 'utf-8') as f:
        painel_css = f.read()

    idx = painel_css.find('/* ================= QUARTIL STYLES ================= */')
    if idx != -1:
        painel_css = painel_css[:idx].strip()

    with codecs.open(r'..\QUARTIL\static\styles.css', 'r', 'utf-8') as f:
        quartil_css = f.read()

    # Extract :root
    root_match = re.search(r':root\s*\{([^}]+)\}', quartil_css)
    root_vars = root_match.group(1) if root_match else ""

    # Strip out root, body, html, *, sidebar, main, topbar, nav-item
    quartil_css = re.sub(r':root\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'body\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\*,\s*\*\:\:before,\s*\*\:\:after\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'#sidebar\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\.sidebar-logo[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'#sidebar nav[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\.nav-item[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\.sidebar-footer[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'#topbar[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'#main\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'#content\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\.section\s*\{[^}]+\}', '', quartil_css)
    quartil_css = re.sub(r'\.section\.active\s*\{[^}]+\}', '', quartil_css)

    # Now we need to prefix selectors with #view-quartil, #view-q4alerts
    # Regex to capture css blocks: selector { rules }
    # This is simplified and assumes no nested @media blocks. Let's see if Quartil has @media
    media_blocks = []
    
    # Simple CSS parser
    out_lines = []
    out_lines.append("/* ================= QUARTIL STYLES ================= */")
    
    # Inject scoped variables and base styles
    out_lines.append("#view-quartil, #view-q4alerts {")
    out_lines.append(root_vars)
    out_lines.append("  background-color: var(--bg);")
    out_lines.append("  color: var(--text);")
    out_lines.append("  padding: 20px;")
    out_lines.append("  border-radius: var(--card-radius);") # Match Painel slightly
    out_lines.append("}\n")

    # To scope all rules, it's easier to just do simple replacements since Quartil CSS classes are known
    # Let's find all selectors:
    
    def replacer(match):
        selector_part = match.group(1).strip()
        rules_part = match.group(2)
        
        if selector_part.startswith('@media'):
            # It's a media query. We will just return it as is, but we'd need to scope its internals.
            # To avoid writing a full parser, let's just do a hacky replace.
            return match.group(0)
            
        # Split multiple selectors
        selectors = [s.strip() for s in selector_part.split(',')]
        new_selectors = []
        for s in selectors:
            if not s: continue
            if s.startswith('@'):
                new_selectors.append(s)
            else:
                new_selectors.append(f"#view-quartil {s}, #view-q4alerts {s}")
        
        return ",\n".join(new_selectors) + " {" + rules_part + "}"

    # We can match `selector { rules }`
    # Be careful with @media { ... { ... } }
    
    # Instead of regex for scoping, let's just use postcss via npx! Wait, we don't have postcss guaranteed.
    # An alternative is to just find specific classes and rename them, or just prefix them.
    # Actually, we can use standard re:
    
    # Let's remove comments
    clean_css = re.sub(r'/\*.*?\*/', '', quartil_css, flags=re.DOTALL)
    
    blocks = []
    buffer = ""
    brace_level = 0
    
    for char in clean_css:
        buffer += char
        if char == '{':
            brace_level += 1
        elif char == '}':
            brace_level -= 1
            if brace_level == 0:
                blocks.append(buffer)
                buffer = ""
                
    scoped_blocks = []
    for block in blocks:
        block = block.strip()
        if not block: continue
        
        if block.startswith('@media'):
            # Extract the media rule and the inner content
            media_match = re.match(r'(@media[^{]+)\{(.*)\}', block, re.DOTALL)
            if media_match:
                media_query = media_match.group(1).strip()
                inner_css = media_match.group(2)
                
                # Scope inner css
                inner_blocks = []
                inner_buffer = ""
                inner_level = 0
                for c in inner_css:
                    inner_buffer += c
                    if c == '{': inner_level += 1
                    elif c == '}':
                        inner_level -= 1
                        if inner_level == 0:
                            inner_blocks.append(inner_buffer)
                            inner_buffer = ""
                            
                scoped_inner = []
                for ib in inner_blocks:
                    ib = ib.strip()
                    if not ib: continue
                    sel, rules = ib.split('{', 1)
                    sel = sel.strip()
                    rules = rules[:-1] # remove trailing }
                    sels = [s.strip() for s in sel.split(',')]
                    new_sels = [f"#view-quartil {s}, #view-q4alerts {s}" for s in sels if s]
                    scoped_inner.append(",\n".join(new_sels) + " {" + rules + "}")
                
                scoped_blocks.append(media_query + " {\n" + "\n".join(scoped_inner) + "\n}")
            else:
                scoped_blocks.append(block)
        else:
            sel, rules = block.split('{', 1)
            sel = sel.strip()
            rules = rules[:-1] # remove trailing }
            sels = [s.strip() for s in sel.split(',')]
            new_sels = [f"#view-quartil {s}, #view-q4alerts {s}" for s in sels if s]
            scoped_blocks.append(",\n".join(new_sels) + " {" + rules + "}")

    out_lines.append("\n".join(scoped_blocks))
    
    final_css = painel_css + "\n\n" + "\n".join(out_lines)
    with codecs.open('style.css', 'w', 'utf-8') as f:
        f.write(final_css)
    print("CSS rebuilt with scoping!")

if __name__ == "__main__":
    rebuild_css()
