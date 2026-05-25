import codecs
import re

def generate():
    with codecs.open(r'..\QUARTIL\static\styles.css', 'r', 'utf-8') as f:
        quartil_css = f.read()
        
    # We want QUARTIL's root, body, sidebar, and generic classes as base.
    # PAINEL OPERAÇÃO's specific layout classes will be added and adapted.
    
    painel_specific_css = """
/* ═══════════════════════════════════════════════════════════
   PAINEL OPERAÇÕES — ADAPTADO PARA QUARTIL THEME
   ═══════════════════════════════════════════════════════════ */

/* ── LOGIN SCREEN ── */
#login-screen {
    position:fixed; inset:0;
    background: var(--dark);
    display:flex; align-items:center; justify-content:center; z-index:2000;
}
.login-card {
    background: var(--card);
    padding:44px 40px; border-radius:16px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 30px rgba(0,0,0,.15);
    max-width:420px; width:100%;
    animation:fadeUp .5s ease;
}
.login-logo-icon {
    width:72px; height:72px;
    background: var(--green);
    border-radius:16px; font-size:24px; font-weight:800; color:#fff;
    display:flex; align-items:center; justify-content:center; margin:0 auto;
    letter-spacing:2px;
}
.login-logo-icon span { color:var(--lime); }
.form-group { display:flex; flex-direction:column; gap:6px; margin-bottom: 12px; }
.form-group label { font-size:12px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:1px; }
.form-group input {
    padding:14px 18px; border:1px solid var(--border); border-radius:8px;
    background:#fff; color:var(--text);
    font-size:16px; outline:none; letter-spacing:3px; transition:all .3s;
}
.form-group input:focus { border-color:var(--green); box-shadow: 0 0 10px var(--accent-glow); }
#btn-login { width: 100%; padding: 14px; background: var(--green); color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
#btn-login:hover { background: var(--navy-mid); }
#login-error { color: var(--q4); }

/* ── LAYOUT ── */
#app-wrapper { display:flex; height:100vh; overflow:hidden; }
.content-area { flex:1; display:flex; flex-direction:column; overflow:hidden; background: var(--bg); }
.main-content { flex:1; overflow-y:auto; padding-bottom: 40px; }

/* ── SIDEBAR ADAPTATIONS (Mapping painel classes to Quartil styles) ── */
.sidebar {
    width: var(--sidebar-w); min-width: var(--sidebar-w);
    background: var(--dark);
    display:flex; flex-direction:column;
    z-index: 100;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
}
.logo-sidebar {
    padding: 30px 20px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    text-align:center;
}
.logo-sidebar h2 { font-size:24px; font-weight:800; letter-spacing:4px; color: #fff; }
.logo-sidebar span { color: var(--lime); }

.nav-links { list-style:none; padding:14px 0; flex:1; }
.nav-links li {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 24px; cursor: pointer;
    color: #7aad8a; font-size: 0.85rem; font-weight: 600;
    transition: all 0.2s; border-left: 4px solid transparent;
}
.nav-links li:hover { color: #fff; background: rgba(255, 255, 255, 0.04); }
.nav-links li.active { color: #fff; background: rgba(141, 198, 66, 0.15); border-left-color: var(--lime); }

.sidebar-footer {
    padding: 16px 20px; border-top: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 0.7rem; color: #4a7a57; text-align: center; margin-top:auto;
}
.btn-logout {
    background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.1); color:#7aad8a;
    padding:10px 14px; border-radius:8px; font-size:12px; cursor:pointer; width:100%;
    transition:all .3s; font-weight: 600;
}
.btn-logout:hover { background:rgba(255,255,255,.1); color:#fff; }

/* ── TOPBAR ── */
.topbar {
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding:14px 24px; display:flex; align-items:center; gap:14px;
    flex-wrap:wrap; position:sticky; top:0; z-index:10;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.topbar-title h1 { font-size:18px; font-weight:700; color:var(--navy); }
.global-filters { display:flex; align-items:flex-end; gap:12px; flex-wrap:wrap; flex:1; justify-content:flex-end; }
.filter-item { display:flex; flex-direction:column; gap:4px; }
.filter-item label { font-size:10px; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.6px; }
.filter-item select, .filter-item input {
    padding:8px 12px; border:1px solid var(--border); border-radius:6px;
    background:#fff; color:var(--text); font-weight: 500;
    font-size:13px; outline:none; min-width:110px; transition:all .3s;
}
.filter-item select:focus, .filter-item input:focus { border-color:var(--green); box-shadow:0 0 0 3px var(--accent-glow); }
.filter-item select option { background:#fff; color:var(--text); }

/* ── COMMON ELEMENTS ── */
.view-section { padding:24px 30px; animation:fadeUp .35s ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)} }

/* ── MOTIVATIONAL PANEL ── */
.motivational-container { display:flex; gap:16px; align-items:center; justify-content:center; margin-bottom:24px; }
.status-card {
    flex:none; width:100%; max-width:650px; display:flex; gap:18px; padding:20px 24px; align-items:center;
    border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,.05);
    background:var(--card); border:1px solid var(--border); border-left:6px solid var(--green);
}
.status-card.good { border-left-color:var(--green); }
.status-card.alert { border-left-color:#F79646; }
.status-card.bad { border-left-color:var(--q4); }
.status-img { width:80px; height:80px; border-radius:10px; object-fit:cover; background:#f1f3f5; }
.status-content { flex:1; display:flex; flex-direction:column; justify-content:center; }
.status-title { font-size:18px; font-weight:800; margin-bottom:6px; color:var(--navy); }
.status-details { font-size:13px; color:var(--muted); display:flex; flex-direction:column; gap:4px; }
.status-good-text { color:var(--green); font-weight: 700; }
.status-bad-text { color:var(--q4); font-weight: 700; }

/* ── KPI GRID (Dashboard Main) ── */
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; margin-bottom:24px; }
/* Reusing Quartil .kpi-card structure for main dashboard */
.kpi-card {
  background: var(--card);
  border-radius: 12px;
  padding: 20px 22px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 10px rgba(27, 94, 56, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex; align-items: center; gap: 16px;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(27, 94, 56, 0.08); }
.kpi-icon { width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; background: var(--green-light); color: var(--navy); }
.kpi-info { display: flex; flex-direction: column; }
.kpi-info h3 { font-size:11px; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }
.kpi-info .value { font-size:24px; font-weight:800; color:var(--navy); }
.kpi-info .target { font-size:12px; color:var(--muted); margin-top:2px; font-weight: 500; }

.section-title { font-size:16px; font-weight:800; color:var(--navy); margin-bottom:16px; display:flex; align-items:center; gap:8px; }

/* BH Grid */
.bh-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:4px; }
.bh-item { background:var(--bg); border-radius:8px; padding:12px; border: 1px solid var(--border); }
.bh-item.bh-cred { border-left:4px solid var(--green); }
.bh-item.bh-def  { border-left:4px solid var(--q4); }
.bh-item.bh-fer  { border-left:4px solid #F79646; }
.bh-item.bh-saldo{ grid-column:1/-1; background:var(--green-light); border-left:4px solid var(--navy); }
.bh-label { font-size:10px; color:var(--muted); font-weight:700; margin-bottom:4px; text-transform:uppercase; }
.bh-val   { font-size:16px; font-weight:800; color: var(--text); }

.charts-container { background:var(--card); padding:24px; border-radius:12px; border:1px solid var(--border); box-shadow:0 2px 10px rgba(0,0,0,.03); }
.charts-container h3 { font-size:15px; font-weight:800; margin-bottom:16px; color:var(--navy); }
.stat-row { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid var(--bg); }
.stat-row:last-child { border-bottom:none; }
.stat-row span { color:var(--muted); font-size:13px; font-weight: 500; }
.stat-row strong { font-size:15px; font-weight:800; color: var(--text); }

.abs-operacao-container { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:12px; margin-bottom:24px; }
.abs-op-item {
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:16px; display:flex; justify-content:space-between; align-items:center;
    box-shadow:0 2px 8px rgba(0,0,0,.02); transition: transform 0.2s;
}
.abs-op-item:hover { transform: translateY(-2px); border-color: var(--navy-mid); }
.abs-op-name { font-size:13px; color:var(--muted); font-weight:700; }
.abs-op-val { font-size:18px; font-weight:800; color: var(--navy); }

/* ── OPERATOR CARDS (Replacing glassmorphism with Quartil flat style) ── */
.cards-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; }
.op-card {
    background: var(--card); border-radius:12px; padding:0;
    border:1px solid var(--border); position:relative; overflow:hidden;
    transition:transform .2s, box-shadow .2s;
    box-shadow: 0 2px 10px rgba(27, 94, 56, 0.04);
}
.op-card:hover { transform:translateY(-4px); box-shadow: 0 8px 20px rgba(27, 94, 56, 0.08); border-color: var(--green); }
.op-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:4px;
    background: var(--navy-mid);
}
.op-card.meta-batida::before { background: var(--green); }

.meta-badge {
    position:absolute; top:16px; right:16px;
    background: var(--green-light); color: var(--green);
    padding:4px 12px; border-radius:20px; font-size:11px; font-weight:800;
    border: 1px solid var(--green); text-transform: uppercase;
}

.op-header { display:flex; align-items:center; gap:16px; padding:20px 20px 0; margin-bottom:16px; }
.op-avatar { width:52px; height:52px; border-radius:50%; border:2px solid var(--border); object-fit:cover; }
.op-avatar-initials {
    width:52px; height:52px; border-radius:50%; border:2px solid var(--green-light);
    display:flex; align-items:center; justify-content:center;
    background:var(--bg); color:var(--navy); font-size:18px; font-weight:800;
}
.op-header-info { flex:1; min-width:0; }
.op-header-info h3 { font-size:15px; font-weight:800; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.op-header-info p { font-size:11px; color:var(--muted); margin-top:4px; display:flex; flex-wrap:wrap; align-items:center; gap:6px; font-weight: 500; }
.tag-mat { background:var(--bg); color:var(--muted); padding:3px 8px; border-radius:6px; border: 1px solid var(--border); }
.tag-op  { background:var(--green-light); color:var(--navy-mid); padding:3px 8px; border-radius:6px; }

.metrics-section { padding:0 20px 20px; }
.section-label { font-size:10px; font-weight:800; text-transform:uppercase; color:var(--muted); margin-bottom:12px; padding-top:12px; border-top:1px solid var(--bg); }

.op-metrics-grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; }
.metric-item {
    background:var(--bg); border:1px solid var(--border); border-radius:8px;
    padding:12px; transition:all .2s;
}
.metric-item:hover { background: #fff; border-color: var(--green); }
.metric-item.full-width { grid-column: 1 / -1; }
.metric-label { font-size:10px; font-weight:700; text-transform:uppercase; color:var(--muted); margin-bottom:6px; }
.metric-val { font-size:16px; font-weight:800; color:var(--navy); }
.metric-sub { font-size:11px; color:var(--muted); margin-top:4px; font-weight: 500; }

.progress-bar-wrap { width:100%; height:6px; background:#e2e8f0; border-radius:3px; margin:8px 0 4px; overflow:hidden; }
.progress-bar { height:100%; border-radius:3px; transition:width .8s ease; background: var(--navy-mid); }

.text-success { color:var(--green)!important; }
.text-danger  { color:var(--q4)!important; }
.text-warning { color:#F79646!important; }

/* Utilities */
.hidden { display: none !important; }

/* RESPONSIVE */
@media (max-width:768px) {
    .sidebar { width:60px; min-width:60px; }
    .sidebar span { display:none; }
    .logo-sidebar h2 { font-size:18px; }
    .cards-grid { grid-template-columns:1fr; }
    .kpi-grid { grid-template-columns:1fr 1fr; }
    .op-metrics-grid { grid-template-columns:1fr; }
}
"""

    # We concatenate QUARTIL global styles + Painel Specific Adapations
    
    # Strip some things from QUARTIL CSS that clash
    quartil_css_clean = quartil_css
    
    final_css = quartil_css_clean + "\n" + painel_specific_css
    
    with codecs.open('style.css', 'w', 'utf-8') as f:
        f.write(final_css)
        
    print("Unified style.css generated successfully!")

if __name__ == "__main__":
    generate()
