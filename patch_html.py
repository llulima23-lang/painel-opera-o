import codecs
import re

def patch():
    # Ler index.html do QUARTIL
    with codecs.open(r'..\QUARTIL\static\index.html', 'r', 'utf-8') as f:
        quartil_html = f.read()

    # Extrair sec-dashboard
    dashboard_match = re.search(r'(<div id="sec-dashboard" class="section active">.*?)<!-- SECTION 4º QUARTIL FOCUS -->', quartil_html, re.DOTALL)
    sec_dashboard = dashboard_match.group(1).replace('class="section active"', 'class="view-section" id="view-quartil" style="display:none;"')

    # Extrair sec-q4-alerts
    q4_match = re.search(r'(<div id="sec-q4-alerts" class="section">.*?)</div><!-- /content -->', quartil_html, re.DOTALL)
    sec_q4_alerts = q4_match.group(1).replace('class="section"', 'class="view-section" id="view-q4alerts" style="display:none;"')

    # Ler index.html do PAINEL OPERAÇÃO
    with codecs.open('index.html', 'r', 'utf-8') as f:
        painel_html = f.read()

    if 'id="view-quartil"' in painel_html:
        print("HTML Already patched")
        return

    # Patch Nav
    nav_links_target = """<li data-view="operadores">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                    <span>Operadores</span>
                </li>"""
    
    new_nav = nav_links_target + """
                <li class="admin-only" data-view="quartil">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    <span>Dashboard Quartil</span>
                </li>
                <li class="admin-only" data-view="q4alerts">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    <span>Foco 4º Quartil</span>
                </li>"""

    painel_html = painel_html.replace(nav_links_target, new_nav)

    # Patch Views
    views_target = """                <!-- VIEW: Operadores -->
                <div id="view-operadores" class="view-section" style="display:none;">
                    <div id="motivational-panel" style="display:none; margin-bottom: 20px;"></div>
                    <div class="cards-grid" id="operadores-grid"></div>
                </div>"""

    new_views = views_target + "\n\n                <!-- VIEW: Quartil -->\n" + sec_dashboard + "\n                <!-- VIEW: Q4 Alerts -->\n" + sec_q4_alerts

    painel_html = painel_html.replace(views_target, new_views)

    with codecs.open('index.html', 'w', 'utf-8') as f:
        f.write(painel_html)

    print("HTML patched successfully")

if __name__ == "__main__":
    patch()
