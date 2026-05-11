// ═══════════════════════════════════════════════════════════
//  CONSTANTES
// ═══════════════════════════════════════════════════════════
const ADMIN_SENHA       = '1926';
const DATA_CORTE        = new Date(2026, 2, 16);

// Mapeamento dinâmico será construído na inicialização
let MES_MAP = {};

let lastUpdatedAt = null;
let pollInterval  = null;

// ═══════════════════════════════════════════════════════════
//  ESTADO GLOBAL
// ═══════════════════════════════════════════════════════════
let G = {
    isAdmin:         false,
    currentMatricula: null,   // null = admin, string = operador
    mesSelecionado:  'METAS MAIO2026',
    mesStr:          '2026-05',
    filtroOperacao:  '',
    filtroNome:      '',
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
//  AGENDAMENTO DIÁRIO E INICIAR APP
// ─────────────────────────────────────────────────────────
function agendarAtualizacaoDiaria() {
    const agora = new Date();
    // Agendado para as 07:55:00
    let proxAtualizacao = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate(), 7, 55, 0);
    if (agora >= proxAtualizacao) {
        proxAtualizacao.setDate(proxAtualizacao.getDate() + 1);
    }
    const msAteAtualizar = proxAtualizacao - agora;
    
    setTimeout(() => {
        if (!G.isAdmin) renderOperadores();
        agendarAtualizacaoDiaria();
    }, msAteAtualizar);
}

function iniciarApp(isAdmin, matricula) {
    G.isAdmin          = isAdmin;
    G.currentMatricula = matricula;



    document.getElementById('login-screen').style.display   = 'none';
    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('app-wrapper').style.display    = 'flex';

    // Info do usuário na sidebar
    atualizarInfoUsuario();

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
    buildMesMap();
    buildSelectores();
    registrarEventosFiltros();

    buildOperadores();
    renderTudo();
    
    agendarAtualizacaoDiaria();
    iniciarAutoUpdate();
}

// ─────────────────────────────────────────────────────────
//  AUTO UPDATE (POLLING)
// ─────────────────────────────────────────────────────────
function iniciarAutoUpdate() {
    if (pollInterval) clearInterval(pollInterval);
    lastUpdatedAt = EMBEDDED_DATA.updated_at;
    
    // Verifica a cada 10 segundos
    pollInterval = setInterval(verificarNovosDados, 10000);
}

function verificarNovosDados() {
    const script = document.createElement('script');
    // Adiciona timestamp para evitar cache do navegador
    script.src = 'data_embedded.js?t=' + Date.now();
    script.onload = () => {
        if (lastUpdatedAt && EMBEDDED_DATA.updated_at !== lastUpdatedAt) {
            console.log('🔄 Dados atualizados detectados em: ' + EMBEDDED_DATA.updated_at);
            lastUpdatedAt = EMBEDDED_DATA.updated_at;
            
            // Re-processa e re-renderiza tudo
            buildOperadores();
            renderTudo();
            
            // Atualiza o texto de "Última atualização" na sidebar
            atualizarInfoUsuario();
            
            // Feedback visual rápido no botão de atualizar
            const btn = document.getElementById('btn-atualizar');
            if (btn) {
                btn.style.transform = 'rotate(360deg)';
                btn.style.transition = 'transform 0.5s ease';
                setTimeout(() => { btn.style.transform = 'none'; }, 500);
            }
        }
        script.remove();
    };
    script.onerror = () => script.remove();
    document.head.appendChild(script);
}

function atualizarInfoUsuario() {
    const dt = new Date(EMBEDDED_DATA.updated_at);
    const lastUpd = dt.toLocaleDateString('pt-BR') + ' ' + dt.toLocaleTimeString('pt-BR');

    if (G.isAdmin) {
        document.getElementById('user-info').textContent = '👤 Admin | Atualizado: ' + lastUpd;
    } else {
        const op = (EMBEDDED_DATA.adm || []).find(o => o.matricula === G.currentMatricula);
        document.getElementById('user-info').textContent = (op ? op.nome : 'Operador ' + G.currentMatricula) + ' | ' + lastUpd;
    }
}

// ─────────────────────────────────────────────────────────
//  MAPEAMENTO DE MESES
// ─────────────────────────────────────────────────────────
function buildMesMap() {
    const metaKeys = Object.keys(EMBEDDED_DATA.meta || {});
    metaKeys.forEach(k => {
        // Tenta extrair o mês do nome da aba (ex: METAS ABRIL2026)
        const match = k.match(/METAS\s+(JANEIRO|FEVEREIRO|MARCO|MARÇO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)(\d{4})?/i);
        if (match) {
            const mesNome = match[1].toUpperCase();
            const ano = match[2] || '2026';
            const meses = {
                'JANEIRO': '01', 'FEVEREIRO': '02', 'MARCO': '03', 'MARÇO': '03',
                'ABRIL': '04', 'MAIO': '05', 'JUNHO': '06', 'JULHO': '07',
                'AGOSTO': '08', 'SETEMBRO': '09', 'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12'
            };
            MES_MAP[k] = `${ano}-${meses[mesNome]}`;
        }
    });
    
    // Atualiza o seletor de meses no HTML se necessário
    const selMes = document.getElementById('mes-filter');
    if (selMes) {
        selMes.innerHTML = '';
        Object.keys(MES_MAP).sort((a,b) => MES_MAP[b].localeCompare(MES_MAP[a])).forEach(k => {
            const opt = document.createElement('option');
            opt.value = k;
            opt.textContent = k.replace('METAS ', '');
            if (k === G.mesSelecionado) opt.selected = true;
            selMes.appendChild(opt);
        });
    }
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

}

// ─────────────────────────────────────────────────────────
//  MONTA OPERADORES
// ─────────────────────────────────────────────────────────
const COMPENSACAO_FERIADO = 26400; // 07:20:00 em segundos

function buildOperadores() {
    const adm    = EMBEDDED_DATA.adm    || [];
    const tempos = EMBEDDED_DATA.tempos || [];
    
    // Build photo map
    const fotoMap = {};
    adm.forEach(a => { if (a.foto) fotoMap[a.nome_norm] = a.foto; });

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
        
        // Saldo do mês vs Saldo Acumulado
        const bh = G.mesSelecionado ? 
                   (tempoMes ? { credito: tempoMes.credito_sec, deficit: tempoMes.deficit_sec } : { credito: 0, deficit: 0 }) :
                   (bhTotal[nNorm] || { credito: 0, deficit: 0 });

        // Captura o Saldo Inicial do RESUMO (que é um débito histórico)
        const bhResumo = EMBEDDED_DATA.resumo ? (EMBEDDED_DATA.resumo[nNorm] || 0) : 0;

        const metasMap = {};
        Object.entries(EMBEDDED_DATA.meta || {}).forEach(([sh, shData]) => {
            metasMap[sh] = (shData.rows || []).find(r => r.nome_norm === nNorm) || null;
        });

        return { 
            ...op,
            nome: op.nome, nomeNorm: nNorm, admissao: op.admissao,
            matricula: op.matricula, operacao: op.operacao,
            foto: fotoMap[nNorm] || null,
            tempoMes, bhCredito: bh.credito, 
            bhDeficit: bh.deficit,
            bhResumo,
            metasMap 
        };
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

function calcDebitosExtras(op) {
    const admDate = op.admissao ? new Date(op.admissao + 'T12:00:00') : null;
    let compensaSec = 0;

    // Datas de Compensa (DÉBITO de 07:12:00 cada - Faltas a compensar)
    const datasCompensa = (EMBEDDED_DATA.compensa || {})[op.nomeNorm] || [];
    datasCompensa.forEach(dataISO => {
        const d = new Date(dataISO + 'T12:00:00');
        if (d >= DATA_CORTE && (!admDate || d >= admDate)) {
            compensaSec += (7 * 3600 + 12 * 60); // 07:12:00 = 25920s
        }
    });

    // Retorna como penalidades (valores que serão subtraídos do saldo)
    return { 
        total: compensaSec,
        compensaSec, 
        numComp: datasCompensa.length 
    };
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

    // Absenteísmo: usa dados da planilha TRATADO-ABS
    const absData = EMBEDDED_DATA.abs_data || {};
    const absGeralUlt3 = absData.geral_ultimos_3 || 0;
    const absGeralMes = (absData.geral_por_mes || {})[G.mesStr] || null;

    const comTempo   = lista.filter(o => o.tempoMes);
    // Cálculo ponderado de pausas do time (Total Pausas / Total Tempo Logado)
    const totalPausasSec = comTempo.reduce((a,o) => a + ((o.tempoMes.media_pausas_total_sec || 0) * o.tempoMes.dias_trabalhados), 0);
    const totalTempoSec  = comTempo.reduce((a,o) => a + ((o.tempoMes.media_tempo_sec || 0) * o.tempoMes.dias_trabalhados), 0);
    const pausaMedia     = totalTempoSec > 0 ? (totalPausasSec / totalTempoSec * 100) : 0;
    
    // Média Tempo Logado: usa dados globais mensais da planilha
    const tempoMediaGlobal = (EMBEDDED_DATA.tempo_logado_media_mensal || {})[G.mesStr] || 0;

    setKpi('kpi-atingimento', atingPct.toFixed(1)+'%',
        atingPct >= 100 ? '#10b981' : atingPct >= 80 ? '#f59e0b' : '#ef4444');
    setKpi('kpi-promessas-det', `${totalProm.toLocaleString('pt-BR')} / ${totalMeta.toLocaleString('pt-BR')} promessas`);
    setKpi('kpi-qualidade',    qualMedia.toFixed(1)+'%',  cor(qualMedia,  95));
    
    // ABS: mostra o mês selecionado como valor principal
    const absDisplay = absGeralMes !== null ? absGeralMes : 0;
    setKpi('kpi-abs', absDisplay.toFixed(2)+'%', cor(absDisplay, 2, false));
    // Subtexto: Volta a ser a meta
    const absSubEl = document.getElementById('kpi-abs-sub');
    if (absSubEl) {
        absSubEl.textContent = 'Meta: < 2%';
    }
    
    setKpi('kpi-pausas',       pausaMedia.toFixed(2)+'%', cor(pausaMedia, 15.5, false));
    setKpi('kpi-tempo-medio',  secToStr(Math.round(tempoMediaGlobal)), cor(tempoMediaGlobal, 7*3600+12*60));

    // BH - usa totais diretos da planilha RESUMO
    const resumoTotals = EMBEDDED_DATA.resumo_totals || {};
    const posTotal = resumoTotals.credito_total_sec || 0;
    const negTotal = resumoTotals.debito_total_sec || 0;
    const saldo = posTotal - negTotal;
    setKpi('bh-positivo', secToStr(posTotal), '#10b981');
    setKpi('bh-negativo', secToStr(negTotal), '#ef4444');
    setKpi('bh-saldo',    secToStr(saldo),    saldo >= 0 ? '#10b981' : '#ef4444');
    document.getElementById('dash-info').textContent =
        `| ${du} D.U | ${lista.length} operadores`;

    // ABS por operação
    renderAbsPorOperacao();
}

// ─────────────────────────────────────────────────────────
//  ABS POR OPERAÇÃO (Dashboard)
// ─────────────────────────────────────────────────────────
function renderAbsPorOperacao() {
    const container = document.getElementById('abs-operacao-grid');
    if (!container) return;
    
    const absData = EMBEDDED_DATA.abs_data || {};
    const opsAbs = (absData.por_operacao_mes || {})[G.mesStr] || [];
    
    if (!opsAbs.length) {
        container.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:8px;">Sem dados de ABS por operação neste mês.</p>';
        return;
    }
    
    container.innerHTML = opsAbs.map(op => {
        const clr = op.abs_pct <= 2 ? '#10b981' : op.abs_pct <= 5 ? '#f59e0b' : '#ef4444';
        return `<div class="abs-op-item">
            <span class="abs-op-name">${op.operacao}</span>
            <span class="abs-op-val" style="color:${clr}">${op.abs_pct.toFixed(2)}%</span>
        </div>`;
    }).join('');
}

// Helper: retorna ABS individual de um operador no mês selecionado
function getIndividualAbs(nomeNorm) {
    const absData = EMBEDDED_DATA.abs_data || {};
    const indMes = absData.individual_mes || {};
    // Usa estritamente o mês selecionado no filtro
    const lista = indMes[G.mesStr] || [];
    const found = lista.find(i => i.nome_norm === nomeNorm);
    if (found) return { ...found, mes: G.mesStr };
    return null;
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
        const pnl = document.getElementById('motivational-panel');
        if (pnl) pnl.style.display = 'none';
        return;
    }
    
    if (!G.isAdmin && G.currentMatricula && lista.length > 0) {
        const result = getOperatorStatusAndDetails(lista[0]);
        renderMotivational(result.status, result.details);
    } else {
        const pnl = document.getElementById('motivational-panel');
        if (pnl) pnl.style.display = 'none';
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
        const ho        = metaRow ? (metaRow.ho || 0) : 0;
        const comissao  = metaRow ? (metaRow.comissao || 0) : 0;
        const metaPausas= metaRow ? (metaRow.pausas || 0) : 0;
        const metaBh    = metaRow ? (metaRow.banco_horas || 0) : 0;
        const matricula = op.matricula || (metaRow && metaRow.matricula) || null;

        const bateouMeta = metaProm > 0 && promessas >= metaProm;
        const pctProm    = metaProm > 0 ? (promessas / metaProm * 100) : 0;
        const faltaMeta  = Math.max(0, metaProm - promessas);
        const absPct     = du > 0 ? (absDias / du * 100) : 0;

        const tm            = op.tempoMes;
        const mediaTempoSec = tm ? tm.media_tempo_sec : 0;

        const resumoSaldo = EMBEDDED_DATA.resumo_saldo_final ? (EMBEDDED_DATA.resumo_saldo_final[op.nomeNorm] || null) : null;

        const initials = op.nome.split(' ').filter(w => w.length > 1).slice(0,2).map(w => w[0]).join('');
        const avatarHtml = op.foto
            ? `<img src="${op.foto}" class="op-avatar" alt="${op.nome}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="op-avatar-initials" style="display:none">${initials}</div>`
            : `<div class="op-avatar-initials">${initials}</div>`;

        const card = document.createElement('div');
        card.className = 'op-card' + (bateouMeta ? ' meta-batida' : '');
        card.innerHTML = `
            ${bateouMeta ? '<div class="meta-badge">\u{1F3C6} Meta Batida!</div>' : ''}
            <div class="op-header">
                ${avatarHtml}
                <div class="op-header-info">
                    <h3>${op.nome}</h3>
                    <p>
                        ${matricula ? `<span class="tag-mat">Mat. ${matricula}</span>` : ''}
                        ${op.operacao ? `<span class="tag-op">${op.operacao}</span>` : ''}
                    </p>
                </div>
            </div>
            <div class="metrics-section">
                <div class="section-label">\u{1F4CA} Indicadores \u2014 ${G.mesSelecionado.replace('METAS ','')}</div>
                ${metaRow ? `
                <div class="op-metrics-grid">
                    <div class="metric-item full-width">
                        <div class="metric-label">Promessas</div>
                        <div class="metric-val" style="color:${cor(pctProm,100)}">${promessas.toLocaleString('pt-BR')} / ${metaProm.toLocaleString('pt-BR')}</div>
                        <div class="progress-bar-wrap"><div class="progress-bar" style="width:${Math.min(pctProm,100).toFixed(1)}%;background:${cor(pctProm,100)};"></div></div>
                        <div class="metric-sub" style="color:${cor(pctProm,100)}">${bateouMeta ? '\u2705 Meta atingida!' : `Falta: ${faltaMeta.toLocaleString('pt-BR')}`} \u2014 ${pctProm.toFixed(1)}%</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Qualidade</div>
                        <div class="metric-val" style="color:${qualidade!=null?cor(qualidade,95):'var(--text-muted)'}">${qualidade!=null?qualidade.toFixed(1)+'%':'N/D'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">ABS (Planilha)</div>
                        ${(() => {
                            const indAbs = getIndividualAbs(op.nomeNorm);
                            const totalDias = indAbs ? indAbs.total_dias : 0;
                            const absIndPct = du > 0 ? (totalDias / du * 100) : 0;
                            const clr = totalDias === 0 ? '#10b981' : absIndPct > 5 ? '#ef4444' : absIndPct > 2 ? '#f59e0b' : '#10b981';
                            return `<div class="metric-val" style="color:${clr}">${totalDias} dia(s)</div>
                                    <div class="metric-sub">${absIndPct.toFixed(2)}%</div>`;
                        })()}
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">H.O</div>
                        <div class="metric-val">R$ ${(ho || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Comiss\u00e3o</div>
                        <div class="metric-val" style="color:var(--success)">R$ ${comissao.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Pausas</div>
                        <div class="metric-val">${(metaPausas || 0).toFixed(2)}%</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Tempo Logado</div>
                        <div class="metric-val">${tm ? secToStr(mediaTempoSec) : 'N/D'}</div>
                        <div class="metric-sub">${tm ? tm.dias_trabalhados + ' dias' : ''}</div>
                    </div>
                    ${(() => {
                        const val = resumoSaldo !== null ? resumoSaldo : (metaBh !== null ? metaBh : null);
                        const corVal = val === null ? 'var(--text-muted)' : (val >= 0 ? 'var(--success)' : 'var(--danger)');
                        const bgVal = val === null ? 'rgba(124,58,237,.06)' : (val >= 0 ? 'rgba(52,211,153,.08)' : 'rgba(248,113,113,.08)');
                        const borderVal = val === null ? 'rgba(124,58,237,.15)' : (val >= 0 ? 'rgba(52,211,153,.2)' : 'rgba(248,113,113,.2)');
                        const txt = val !== null ? secToStr(val) : 'N/D';
                        return `
                        <div class="metric-item full-width" style="background:${bgVal}; border-color:${borderVal}">
                            <div class="metric-label">\u{1F3E6} Banco de Horas (Saldo Final)</div>
                            <div class="metric-val" style="font-size:20px; color:${corVal}">${txt}</div>
                        </div>`;
                    })()}
                </div>
                ` : '<p style="color:var(--text-muted);font-size:12px;padding:8px 0;">Sem dados neste m\u00eas.</p>'}
            </div>
        `;
        grid.appendChild(card);
    });




    if (!G.isAdmin && G.currentMatricula && lista.length === 1) {
        const hoje = new Date();
        const seed = hoje.getFullYear() * 366 + hoje.getMonth() * 32 + hoje.getDate();
        
        const quote = MOTIVATIONAL_QUOTES[seed % MOTIVATIONAL_QUOTES.length];
        const imgs = ['motivation_art_new_month.png', 'motivation_art_callcenter.png', 'motivation_art.png', 'motivation_art_funny.png'];
        const img = imgs[seed % imgs.length];
        
        const quoteCard = document.createElement('div');
        quoteCard.className = 'quote-card';
        quoteCard.innerHTML = `
            <img src="${img}" class="quote-img" alt="Motivação">
            <div class="quote-text">"${quote}"</div>
        `;
        grid.appendChild(quoteCard);
    }
}

// ─────────────────────────────────────────────────────────
//  MOTIVACIONAL E STATUS DO OPERADOR
// ─────────────────────────────────────────────────────────
const MOTIVATIONAL_QUOTES = [
    "O sucesso é a soma de pequenos esforços repetidos dia após dia.",
    "Acredite que você pode, assim você já está no meio do caminho.",
    "Não espere por oportunidades, crie-as.",
    "A persistência é o caminho do êxito.",
    "Mês novo, foco renovado! 🚀 Que a força do café (e a vontade de bater meta) estejam com você!",
    "Grandes conquistas exigem grandes dedicações.",
    "O segredo do sucesso é a constância do propósito.",
    "O único lugar onde o sucesso vem antes do trabalho é no dicionário.",
    "Cada novo dia é uma nova chance de fazer melhor.",
    "Seu futuro é criado pelo que você faz hoje.",
    "A motivação te faz começar, o hábito te faz continuar.",
    "Foque no seu objetivo e não nas dificuldades.",
    "Desafios são oportunidades disfarçadas.",
    "O sucesso não é um acidente, é trabalho duro e aprendizado.",
    "Pequenos progressos diários levam a grandes resultados.",
    "Não importa o quão devagar você vá, desde que você não pare.",
    "O impossível é apenas uma palavra até que alguém o faça.",
    "Acredite no seu potencial e supere seus limites.",
    "A energia que você coloca no universo é a mesma que retorna para você.",
    "Cada passo à frente, por menor que seja, é um avanço.",
    "A disciplina é a ponte entre metas e realizações.",
    "Celebre as pequenas vitórias; elas te levarão ao grande sucesso.",
    "O otimismo é a fé em ação.",
    "Sucesso é ir de fracasso em fracasso sem perder o entusiasmo.",
    "A excelência não é um ato, mas um hábito.",
    "Mantenha o foco, a força e a fé em si mesmo.",
    "Não limite seus desafios, desafie seus limites.",
    "Sua atitude determina sua altitude.",
    "Acredite no processo e continue avançando.",
    "O amanhã começa com as escolhas de hoje.",
    "Você é mais forte e capaz do que imagina."
];

function getOperatorStatusAndDetails(op) {
    const metaRow = op.metasMap[G.mesSelecionado];
    const tm = op.tempoMes;
    
    let isBad = false, isAlert = false;
    let goodList = [];
    let badList = [];
    
    if (metaRow && metaRow.meta_prom > 0) {
        const pct = metaRow.promessas / metaRow.meta_prom * 100;
        if (pct < 80) { isBad = true; badList.push('Promessas'); }
        else if (pct < 100) { isAlert = true; badList.push('Promessas'); }
        else { goodList.push('Promessas'); }
    }
    if (metaRow && metaRow.qualidade !== null) {
        if (metaRow.qualidade < 90) { isBad = true; badList.push('Qualidade'); }
        else if (metaRow.qualidade < 95) { isAlert = true; badList.push('Qualidade'); }
        else { goodList.push('Qualidade'); }
    }
    if (metaRow && metaRow.abs_dias > 0) {
        const du = ((EMBEDDED_DATA.meta || {})[G.mesSelecionado] || {}).du || 22;
        const absPct = metaRow.abs_dias / du * 100;
        if (absPct > 5) { isBad = true; badList.push('Faltas'); }
        else if (absPct > 2) { isAlert = true; badList.push('Faltas'); }
        else { goodList.push('Faltas'); }
    } else if (metaRow && metaRow.abs_dias === 0) {
        goodList.push('Faltas');
    }
    
    if (tm && tm.media_pausa_pct !== null) {
        // Unificado para 15.5% como no BANCO DE HORAS
        if (tm.media_pausa_pct > 15.5) { isBad = true; badList.push('Pausas'); }
        else { goodList.push('Pausas'); }
    }
    
    let status = 'good';
    if (isBad) status = 'bad';
    else if (isAlert) status = 'alert';
    
    return { status, details: { good: goodList, bad: badList } };
}

function renderMotivational(status, details) {
    const pnl = document.getElementById('motivational-panel');
    if (!pnl) return;
    
    let title = "", imgSrc = "", cls = "";
    if (status === 'good') {
        title = "Excelente Trabalho! 🏆";
        imgSrc = "status_good.png";
        cls = "good";
    } else if (status === 'alert') {
        title = "Atenção: Foco nos indicadores! 🧭";
        imgSrc = "status_alert.png";
        cls = "alert";
    } else {
        title = "Aviso: Precisamos melhorar! 📢";
        imgSrc = "status_bad.png";
        cls = "bad";
    }
    
    let detailsHtml = "";
    if (details.good.length > 0) {
        detailsHtml += `<span><strong class="status-good-text">✅ Excelente em:</strong> ${details.good.join(', ')}</span>`;
    }
    if (details.bad.length > 0) {
        detailsHtml += `<span><strong class="status-bad-text">⚠️ Precisamos melhorar:</strong> ${details.bad.join(', ')}</span>`;
    }
    if (detailsHtml === "") {
        detailsHtml = `<span>Ainda não há dados suficientes neste mês.</span>`;
    }
    
    pnl.className = 'motivational-container';
    pnl.innerHTML = `
        <div class="status-card ${cls}">
            <img src="${imgSrc}" class="status-img" alt="${status}">
            <div class="status-content">
                <div class="status-title">${title}</div>
                <div class="status-details">${detailsHtml}</div>
            </div>
        </div>
    `;
    pnl.style.display = 'flex';
}
