// ═══════════════════════════════════════════════════════════
//  CONSTANTES
// ═══════════════════════════════════════════════════════════
const ADMIN_SENHA       = '1926';
const DEBITO_FERIADO_SEC = 4320;  // 01:12:00
const DATA_CORTE        = new Date(2026, 2, 16);

const MES_MAP = {
    'METAS JANEIRO2026':   '2026-01',
    'METAS FEVEREIRO2026': '2026-02',
    'METAS MARÇO2026':     '2026-03',
    'METAS ABRIL2026':     '2026-04',
};

// ═══════════════════════════════════════════════════════════
//  ESTADO GLOBAL
// ═══════════════════════════════════════════════════════════
let G = {
    isAdmin:         false,
    currentMatricula: null,   // null = admin, string = operador
    mesSelecionado:  'METAS ABRIL2026',
    mesStr:          '2026-04',
    filtroOperacao:  '',
    filtroNome:      '',
    feriadosSel:     new Set(),
    operadores:      [],
};

// ═══════════════════════════════════════════════════════════
//  UTILITÁRIOS
// ═══════════════════════════════════════════════════════════
const secToStr = sec => {
    const neg = sec < 0;
    sec = Math.abs(Math.round(sec));
    const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    const p = v => String(v).padStart(2, '0');
    return (neg ? '-' : '') + `${p(h)}:${p(m)}:${p(s)}`;
};

const cor = (val, meta, maior = true) =>
    maior ? (val >= meta ? '#10b981' : '#ef4444') : (val <= meta ? '#10b981' : '#ef4444');

const norm = s => !s ? '' :
    String(s).toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();

const setKpi = (id, txt, clr) => {
    const el = document.getElementById(id);
    if (el) { el.textContent = txt; if (clr) el.style.color = clr; }
};

// ═══════════════════════════════════════════════════════════
//  INICIALIZAÇÃO
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    if (typeof EMBEDDED_DATA === 'undefined') {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('loading-screen').style.display = 'flex';
        document.getElementById('loading-text').textContent =
            'Erro: data_embedded.js não encontrado. Execute o gerar_dados.py.';
        document.getElementById('loading-text').style.color = '#ef4444';
        return;
    }

    // ── Login ───────────────────────────────────────────────
    const loginInput = document.getElementById('login-input');
    loginInput.addEventListener('keydown', e => { if (e.key === 'Enter') tentarLogin(); });
    document.getElementById('btn-login').addEventListener('click', tentarLogin);

    // ── Logout ──────────────────────────────────────────────
    document.getElementById('btn-logout').addEventListener('click', () => {
        sessionStorage.removeItem('po_sessao');
        location.reload();
    });

    // ── Restaura sessão ─────────────────────────────────────
    const sessao = sessionStorage.getItem('po_sessao');
    if (sessao) {
        const s = JSON.parse(sessao);
        iniciarApp(s.isAdmin, s.matricula);
    }
});

// ─────────────────────────────────────────────────────────
//  LOGIN
// ─────────────────────────────────────────────────────────
function tentarLogin() {
    const val = document.getElementById('login-input').value.trim();
    if (!val) return;

    if (val === ADMIN_SENHA) {
        sessionStorage.setItem('po_sessao', JSON.stringify({ isAdmin: true, matricula: null }));
        iniciarApp(true, null);
        return;
    }

    // Verifica se é matrícula válida
    const op = (EMBEDDED_DATA.adm || []).find(o => o.matricula === val);
    if (op) {
        sessionStorage.setItem('po_sessao', JSON.stringify({ isAdmin: false, matricula: val }));
        iniciarApp(false, val);
        return;
    }

    const errEl = document.getElementById('login-error');
    errEl.style.display = 'block';
    setTimeout(() => { errEl.style.display = 'none'; }, 3000);
}

// ─────────────────────────────────────────────────────────
//  INICIAR APP
// ─────────────────────────────────────────────────────────
function iniciarApp(isAdmin, matricula) {
    G.isAdmin          = isAdmin;
    G.currentMatricula = matricula;

    document.getElementById('login-screen').style.display   = 'none';
    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('app-wrapper').style.display    = 'flex';

    // Atualização
    const dt = new Date(EMBEDDED_DATA.updated_at);
    const lastUpd = dt.toLocaleDateString('pt-BR') + ' ' + dt.toLocaleTimeString('pt-BR');

    // Info do usuário na sidebar
    if (isAdmin) {
        document.getElementById('user-info').textContent = '👤 Admin | Atualizado: ' + lastUpd;
    } else {
        const op = (EMBEDDED_DATA.adm || []).find(o => o.matricula === matricula);
        document.getElementById('user-info').textContent = op ? op.nome : 'Operador ' + matricula;
    }

    // Oculta elementos admin-only se não for admin
    document.querySelectorAll('.admin-only').forEach(el => {
        el.style.display = isAdmin ? '' : 'none';
    });

    // Navegação (admin vê dashboard + operadores; operador só vê seu card)
    if (!isAdmin) {
        // Força view operadores e não exibe sidebar de dashboard
        document.getElementById('view-operadores').style.display = 'block';
        document.getElementById('view-dashboard').style.display  = 'none';
        document.getElementById('page-title').textContent = 'Meu Desempenho';
        // Marca nav operadores como ativo
        document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
        document.querySelector('[data-view="operadores"]').classList.add('active');
    }

    // Eventos de navegação
    document.querySelectorAll('.nav-links li').forEach(li => {
        li.addEventListener('click', () => {
            if (!isAdmin && li.classList.contains('admin-only')) return;
            document.querySelectorAll('.nav-links li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            const v = li.dataset.view;
            document.querySelectorAll('.view-section').forEach(s => s.style.display = 'none');
            document.getElementById('view-' + v).style.display = 'block';
            document.getElementById('page-title').textContent =
                v === 'dashboard' ? 'Dashboard Geral' : (isAdmin ? 'Operadores' : 'Meu Desempenho');
        });
    });

    // Filtros globais (Mês e Feriados disponíveis para operadores também)
    buildSelectores();
    buildFeriadosPanel();
    registrarEventosFiltros();

    buildOperadores();
    renderTudo();
}

// ─────────────────────────────────────────────────────────
//  SELECTORES
// ─────────────────────────────────────────────────────────
function buildSelectores() {
    const ops = EMBEDDED_DATA.operacoes || [];
    const selOp = document.getElementById('op-filter');
    ops.forEach(o => {
        const opt = document.createElement('option');
        opt.value = o; opt.textContent = o;
        selOp.appendChild(opt);
    });

    const selNome = document.getElementById('op-nome-filter');
    (EMBEDDED_DATA.adm || []).forEach(op => {
        const opt = document.createElement('option');
        opt.value = op.nome;
        opt.textContent = op.nome + (op.matricula ? ` (${op.matricula})` : '');
        selNome.appendChild(opt);
    });
}

// ─────────────────────────────────────────────────────────
//  FERIADOS
// ─────────────────────────────────────────────────────────
function buildFeriadosPanel() {
    const grid = document.getElementById('feriados-grid');
    (EMBEDDED_DATA.feriados || []).forEach(f => {
        const d = new Date(f.data + 'T12:00:00');
        const lbl = document.createElement('label');
        lbl.className = 'feriado-item';
        lbl.innerHTML = `
            <input type="checkbox" class="feriado-check" value="${f.data}">
            <span class="feriado-data">${d.toLocaleDateString('pt-BR')}</span>
            <span class="feriado-nome">${f.nome}</span>
            <span class="feriado-debito">−01:12</span>
        `;
        lbl.querySelector('input').addEventListener('change', e => {
            if (e.target.checked) G.feriadosSel.add(f.data);
            else G.feriadosSel.delete(f.data);
            atualizaBadge(); renderTudo();
        });
        grid.appendChild(lbl);
    });
}

function atualizaBadge() {
    document.getElementById('feriados-badge').textContent = G.feriadosSel.size;
}

// ─────────────────────────────────────────────────────────
//  EVENTOS FILTROS
// ─────────────────────────────────────────────────────────
function registrarEventosFiltros() {
    document.getElementById('mes-filter').addEventListener('change', e => {
        G.mesSelecionado = e.target.value;
        G.mesStr = MES_MAP[e.target.value] || '';
        renderTudo();
    });
    document.getElementById('op-filter').addEventListener('change', e => {
        G.filtroOperacao = e.target.value; renderTudo();
    });
    document.getElementById('op-nome-filter').addEventListener('change', e => {
        G.filtroNome = e.target.value;
        document.getElementById('search-op').value = e.target.value;
        renderTudo();
    });
    document.getElementById('search-op').addEventListener('input', e => {
        G.filtroNome = e.target.value;
        document.getElementById('op-nome-filter').value = '';
        renderTudo();
    });
    document.getElementById('btn-atualizar').addEventListener('click', () => location.reload());
    document.getElementById('btn-feriados').addEventListener('click', () => {
        const p = document.getElementById('feriados-panel');
        p.style.display = p.style.display === 'none' ? 'block' : 'none';
    });
    document.getElementById('btn-marcar-todos').addEventListener('click', () => {
        document.querySelectorAll('.feriado-check').forEach(cb => { cb.checked = true; G.feriadosSel.add(cb.value); });
        atualizaBadge(); renderTudo();
    });
    document.getElementById('btn-desmarcar-todos').addEventListener('click', () => {
        document.querySelectorAll('.feriado-check').forEach(cb => { cb.checked = false; });
        G.feriadosSel.clear(); atualizaBadge(); renderTudo();
    });
}

// ─────────────────────────────────────────────────────────
//  MONTA OPERADORES
// ─────────────────────────────────────────────────────────
function buildOperadores() {
    const adm    = EMBEDDED_DATA.adm    || [];
    const tempos = EMBEDDED_DATA.tempos || [];

    const temposIdx = {};
    tempos.forEach(t => { temposIdx[t.nome_norm + '|' + t.mes] = t; });

    const bhTotal = {};
    tempos.forEach(t => {
        if (!bhTotal[t.nome_norm]) bhTotal[t.nome_norm] = { credito: 0, deficit: 0 };
        bhTotal[t.nome_norm].credito += t.credito_sec;
        bhTotal[t.nome_norm].deficit += t.deficit_sec;
    });

    G.operadores = adm.map(op => {
        const nNorm = op.nome_norm;
        const tempoMes = temposIdx[nNorm + '|' + G.mesStr] || null;
        const bh = bhTotal[nNorm] || { credito: 0, deficit: 0 };

        const metasMap = {};
        Object.entries(EMBEDDED_DATA.meta || {}).forEach(([sh, shData]) => {
            metasMap[sh] = (shData.rows || []).find(r => r.nome_norm === nNorm) || null;
        });

        return { nome: op.nome, nomeNorm: nNorm, admissao: op.admissao,
                 matricula: op.matricula, operacao: op.operacao,
                 tempoMes, bhCredito: bh.credito, bhDeficit: bh.deficit, metasMap };
    });
}

function rebuildTempoMes() {
    const temposIdx = {};
    (EMBEDDED_DATA.tempos || []).forEach(t => { temposIdx[t.nome_norm + '|' + t.mes] = t; });
    G.operadores.forEach(op => { op.tempoMes = temposIdx[op.nomeNorm + '|' + G.mesStr] || null; });
}

// ─────────────────────────────────────────────────────────
//  FILTRO COMUM
// ─────────────────────────────────────────────────────────
function operadoresFiltrados() {
    // Se operador logado, mostra só o dele
    if (!G.isAdmin && G.currentMatricula) {
        return G.operadores.filter(o => o.matricula === G.currentMatricula);
    }
    const fNorm = norm(G.filtroNome);
    return G.operadores.filter(op => {
        if (G.filtroOperacao && op.operacao !== G.filtroOperacao) return false;
        if (fNorm) {
            const nomeOk = op.nomeNorm.includes(fNorm);
            const matOk  = op.matricula && op.matricula.includes(G.filtroNome.trim());
            if (!nomeOk && !matOk) return false;
        }
        return true;
    });
}

function calcDebitoFeriados(op) {
    const admDate = op.admissao ? new Date(op.admissao + 'T12:00:00') : null;
    let debito = 0;
    G.feriadosSel.forEach(dataISO => {
        const f = new Date(dataISO + 'T12:00:00');
        if (f >= DATA_CORTE && (!admDate || f >= admDate)) debito += DEBITO_FERIADO_SEC;
    });
    return debito;
}

// ─────────────────────────────────────────────────────────
//  RENDER TUDO
// ─────────────────────────────────────────────────────────
function renderTudo() {
    rebuildTempoMes();
    if (G.isAdmin) renderDashboard();
    renderOperadores();
}

// ─────────────────────────────────────────────────────────
//  DASHBOARD
// ─────────────────────────────────────────────────────────
function renderDashboard() {
    const sheet    = (EMBEDDED_DATA.meta || {})[G.mesSelecionado] || {};
    const du       = sheet.du || 22;
    const lista    = operadoresFiltrados();
    const metaRows = lista.map(op => op.metasMap[G.mesSelecionado]).filter(Boolean);

    let totalProm = 0, totalMeta = 0, qualSum = 0, qualCnt = 0, absSum = 0;
    metaRows.forEach(r => {
        totalProm += r.promessas || 0;
        totalMeta += r.meta_prom || 0;
        if (r.qualidade != null) { qualSum += r.qualidade; qualCnt++; }
        absSum += r.abs_dias || 0;
    });

    const atingPct  = totalMeta > 0 ? (totalProm / totalMeta * 100) : 0;
    const qualMedia = qualCnt   > 0 ? qualSum / qualCnt : 0;
    const absPct    = (absSum / ((lista.length || 1) * du)) * 100;

    const comTempo   = lista.filter(o => o.tempoMes);
    const pausaMedia = comTempo.length > 0 ? comTempo.reduce((a,o) => a+(o.tempoMes.media_pausa_pct||0),0)/comTempo.length : 0;
    const tempoMedia = comTempo.length > 0 ? comTempo.reduce((a,o) => a+(o.tempoMes.media_tempo_sec||0),0)/comTempo.length : 0;

    setKpi('kpi-atingimento', atingPct.toFixed(1)+'%',
        atingPct >= 100 ? '#10b981' : atingPct >= 80 ? '#f59e0b' : '#ef4444');
    setKpi('kpi-promessas-det', `${totalProm.toLocaleString('pt-BR')} / ${totalMeta.toLocaleString('pt-BR')} promessas`);
    setKpi('kpi-qualidade',    qualMedia.toFixed(1)+'%',  cor(qualMedia,  95));
    setKpi('kpi-abs',          absPct.toFixed(2)+'%',     cor(absPct,     2, false));
    setKpi('kpi-pausas',       pausaMedia.toFixed(2)+'%', cor(pausaMedia, 15.5, false));
    setKpi('kpi-tempo-medio',  secToStr(Math.round(tempoMedia)), cor(tempoMedia, 7*3600+12*60));

    // BH
    let posTotal = 0, negTotal = 0, ferTotal = 0;
    lista.forEach(op => {
        const d = calcDebitoFeriados(op);
        const s = op.bhCredito - op.bhDeficit - d;
        if (s >= 0) posTotal += s; else negTotal += Math.abs(s);
        ferTotal += d;
    });
    const saldo = posTotal - negTotal;
    setKpi('bh-positivo', secToStr(posTotal), '#10b981');
    setKpi('bh-negativo', secToStr(negTotal), '#ef4444');
    setKpi('bh-feriados', secToStr(ferTotal), '#f59e0b');
    setKpi('bh-saldo',    secToStr(saldo),    saldo >= 0 ? '#10b981' : '#ef4444');
    document.getElementById('feriados-qtd').textContent = G.feriadosSel.size + ' feriado(s) aplicado(s)';
    document.getElementById('dash-info').textContent =
        `| ${du} dias úteis | ${lista.length} operadores`;
}

// ─────────────────────────────────────────────────────────
//  CARDS DE OPERADORES
// ─────────────────────────────────────────────────────────
function renderOperadores() {
    const grid = document.getElementById('operadores-grid');
    grid.innerHTML = '';

    const sheet = (EMBEDDED_DATA.meta || {})[G.mesSelecionado] || {};
    const du    = sheet.du || 22;
    let lista   = operadoresFiltrados();

    if (!lista.length) {
        grid.innerHTML = '<p style="color:#64748b;padding:20px;">Nenhum operador encontrado.</p>';
        return;
    }

    // Ordena: meta batida primeiro (só admin vê todos)
    if (G.isAdmin) {
        lista = [...lista].sort((a, b) => {
            const rA = a.metasMap[G.mesSelecionado], rB = b.metasMap[G.mesSelecionado];
            const bA = rA && rA.meta_prom > 0 && rA.promessas >= rA.meta_prom;
            const bB = rB && rB.meta_prom > 0 && rB.promessas >= rB.meta_prom;
            if (bA && !bB) return -1; if (!bA && bB) return 1;
            return a.nome.localeCompare(b.nome, 'pt-BR');
        });
    }

    lista.forEach(op => {
        const metaRow   = op.metasMap[G.mesSelecionado];
        const promessas = metaRow ? (metaRow.promessas || 0) : 0;
        const metaProm  = metaRow ? (metaRow.meta_prom || 0) : 0;
        const qualidade = metaRow ? metaRow.qualidade : null;
        const absDias   = metaRow ? (metaRow.abs_dias || 0) : 0;
        const matricula = op.matricula || (metaRow && metaRow.matricula) || null;

        const bateouMeta = metaProm > 0 && promessas >= metaProm;
        const pctProm    = metaProm > 0 ? (promessas / metaProm * 100) : 0;
        const faltaMeta  = Math.max(0, metaProm - promessas);
        const absPct     = du > 0 ? (absDias / du * 100) : 0;

        const tm            = op.tempoMes;
        const mediaTempoSec = tm ? tm.media_tempo_sec : 0;
        const metaDiariaSec = tm ? tm.meta_diaria_sec : (7*3600+12*60);
        const diasTrab      = tm ? tm.dias_trabalhados : 0;
        const mediaPausa    = tm ? tm.media_pausa_pct  : null;
        const tempoVsMeta   = mediaTempoSec - metaDiariaSec;

        const debFer  = calcDebitoFeriados(op);
        const saldoBh = op.bhCredito - op.bhDeficit - debFer;

        const card = document.createElement('div');
        card.className = 'op-card' + (bateouMeta ? ' meta-batida' : '');
        card.innerHTML = `
            ${bateouMeta ? '<div class="meta-badge">🏆 Meta Batida!</div>' : ''}
            <div class="op-header">
                <h3>${op.nome}</h3>
                <p>
                    ${matricula ? `<span class="tag-mat">Mat. ${matricula}</span>` : ''}
                    ${op.operacao ? `<span class="tag-op">${op.operacao}</span>` : ''}
                    ${op.admissao ? ` Admissão: ${new Date(op.admissao+'T12:00:00').toLocaleDateString('pt-BR')}` : ''}
                </p>
            </div>

            <div class="metrics-section">
                <div class="section-label">📊 Metas — ${G.mesSelecionado.replace('METAS ','')}</div>
                ${metaRow ? `
                    <div class="op-metric">
                        <span class="label">Promessas</span>
                        <span class="val" style="color:${cor(pctProm,100)}">${promessas.toLocaleString('pt-BR')} / ${metaProm.toLocaleString('pt-BR')}</span>
                    </div>
                    <div class="progress-bar-wrap"><div class="progress-bar" style="width:${Math.min(pctProm,100).toFixed(1)}%;background:${cor(pctProm,100)};"></div></div>
                    <div class="op-metric" style="margin-top:-4px;">
                        <span class="label">${bateouMeta ? '✅ Meta atingida' : `Falta: ${faltaMeta.toLocaleString('pt-BR')}`}</span>
                        <span class="val" style="color:${cor(pctProm,100)}">${pctProm.toFixed(1)}%</span>
                    </div>
                    <div class="op-metric">
                        <span class="label">Qualidade</span>
                        <span class="val" style="color:${qualidade!=null?cor(qualidade,95):'#64748b'}">${qualidade!=null?qualidade.toFixed(1)+'%':'N/D'}</span>
                    </div>
                    <div class="op-metric">
                        <span class="label">ABS</span>
                        <span class="val" style="color:${cor(absPct,2,false)}">${absDias} dia(s) — ${absPct.toFixed(2)}%</span>
                    </div>
                ` : '<p style="color:#64748b;font-size:12px;">Sem dados de metas neste mês.</p>'}
            </div>

            <div class="metrics-section">
                <div class="section-label">⏱️ Tempos — Média ${G.mesStr}</div>
                ${tm ? `
                    <div class="op-metric">
                        <span class="label">Média logado/dia</span>
                        <span class="val" style="color:${tempoVsMeta>=0?'#10b981':'#ef4444'}">${secToStr(mediaTempoSec)}</span>
                    </div>
                    <div class="op-metric">
                        <span class="label">Meta diária</span>
                        <span class="val">${secToStr(metaDiariaSec)}</span>
                    </div>
                    <div class="op-metric">
                        <span class="label">Dias no mês</span>
                        <span class="val">${diasTrab}</span>
                    </div>
                    <div class="op-metric">
                        <span class="label">Média pausas</span>
                        <span class="val" style="color:${mediaPausa!=null?cor(mediaPausa,15.5,false):'#64748b'}">${mediaPausa!=null?mediaPausa.toFixed(2)+'%':'N/D'}</span>
                    </div>
                ` : `<p style="color:#64748b;font-size:12px;">Sem dados em ${G.mesStr}.</p>`}
            </div>

            <div class="metrics-section">
                <div class="section-label">🏦 Banco de Horas (desde 16/03/2026)</div>
                <div class="bh-grid">
                    <div class="bh-item bh-cred">
                        <div class="bh-label">Crédito</div>
                        <div class="bh-val">${secToStr(op.bhCredito)}</div>
                    </div>
                    <div class="bh-item bh-def">
                        <div class="bh-label">Déficit</div>
                        <div class="bh-val">${secToStr(op.bhDeficit)}</div>
                    </div>
                    <div class="bh-item bh-fer">
                        <div class="bh-label">Feriados (${G.feriadosSel.size})</div>
                        <div class="bh-val">${secToStr(debFer)}</div>
                    </div>
                    <div class="bh-item bh-saldo" style="border-top:1px dashed var(--border);padding-top:8px;margin-top:4px;">
                        <div class="bh-label"><strong>Saldo Final</strong></div>
                        <div class="bh-val" style="font-size:17px;font-weight:700;color:${saldoBh>=0?'#10b981':'#ef4444'}">${secToStr(saldoBh)}</div>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}
