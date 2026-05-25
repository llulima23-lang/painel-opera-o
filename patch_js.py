import codecs
import re

def create_app_quartil():
    with codecs.open(r'..\QUARTIL\static\app.js', 'r', 'utf-8') as f:
        js = f.read()

    # Wrap in function
    js = js.replace("document.addEventListener('DOMContentLoaded', () => {", "window.initQuartil = function() {")
    js = js.replace("renderDashboard()", "renderQuartilDashboard()")
    js = js.replace("function renderQuartilDashboard()", "window.renderQuartilDashboard = function()")

    # Replace loadData
    load_data_replacement = """
    window.loadDataQuartil = function() {
        if (typeof EMBEDDED_DATA === 'undefined' || !EMBEDDED_DATA.quartil_data) return;
        
        const mesAtual = (typeof G !== 'undefined' && G.mesSelecionado) ? G.mesSelecionado : 'METAS MAIO2026';
        const dataInfo = EMBEDDED_DATA.quartil_data[mesAtual] || { data: [], stats: {} };
        
        allAgents = dataInfo.data || [];
        originalStats = dataInfo.stats || {};
        
        if (isFirstLoad) {
            populateOperationsDropdown(originalStats.operacoes || []);
            if(loadingState) loadingState.classList.add('hidden');
            if(dashboardData) dashboardData.classList.remove('hidden');
            isFirstLoad = false;
        }
        
        if (window.renderQuartilDashboard) window.renderQuartilDashboard();
    }
    """
    
    js = re.sub(r'function loadData\(\)\s*\{.*?\}\s*// Initial load', load_data_replacement + '\n    // Initial load', js, flags=re.DOTALL)
    js = js.replace('loadData();', 'window.loadDataQuartil();')
    js = re.sub(r'setInterval\(loadData, 30000\);', '', js)
    
    with codecs.open('app_quartil.js', 'w', 'utf-8') as f:
        f.write(js)

def patch_app():
    with codecs.open('app.js', 'r', 'utf-8') as f:
        app_js = f.read()
        
    if "window.initQuartil" in app_js:
        print("app.js already patched")
        return
        
    # Hook into renderTudo
    app_js = app_js.replace("if (G.isAdmin) renderDashboard();", "if (G.isAdmin) renderDashboard();\n    if (typeof window.initQuartil === 'function' && !window.quartilInitialized) { window.initQuartil(); window.quartilInitialized = true; }\n    if (window.loadDataQuartil) window.loadDataQuartil();")
    
    with codecs.open('app.js', 'w', 'utf-8') as f:
        f.write(app_js)

def patch_index():
    with codecs.open('index.html', 'r', 'utf-8') as f:
        html = f.read()
        
    if "app_quartil.js" not in html:
        html = html.replace('<script src="app.js?v=2"></script>', '<script src="app_quartil.js?v=1"></script>\n    <script src="app.js?v=2"></script>')
        with codecs.open('index.html', 'w', 'utf-8') as f:
            f.write(html)

if __name__ == "__main__":
    create_app_quartil()
    patch_app()
    patch_index()
    print("JS patched successfully")
