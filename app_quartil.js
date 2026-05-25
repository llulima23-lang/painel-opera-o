window.initQuartil = function() {
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const dashboardData = document.getElementById('dashboardData');
    
    // Filters
    const filterOp = document.getElementById('filterOp');
    const filterQuartilHO = document.getElementById('filterQuartilHO');
    const filterQuartilPromessa = document.getElementById('filterQuartilPromessa');
    const searchAgent = document.getElementById('searchAgent');
    
    // KPI elements
    const kpiTotalAgentes = document.getElementById('kpiTotalAgentes');
    const kpiMediaHO = document.getElementById('kpiMediaHO');
    const kpiMediaPromessas = document.getElementById('kpiMediaPromessas');
    const kpiTotalOperacoes = document.getElementById('kpiTotalOperacoes');
    
    // Distribution elements
    const q1Count = document.getElementById('q1Count');
    const q2Count = document.getElementById('q2Count');
    const q3Count = document.getElementById('q3Count');
    const q4Count = document.getElementById('q4Count');
    
    // Grid
    const agentsGrid = document.getElementById('agentsGrid');
    
    // Page navigation
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSec = item.getAttribute('data-sec');
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            sections.forEach(sec => {
                if (sec.id === `sec-${targetSec}`) {
                    sec.classList.add('active');
                } else {
                    sec.classList.remove('active');
                }
            });
        });
    });
    
    let allAgents = [];
    let originalStats = {};
    let isFirstLoad = true;

    
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
    
    // Initial load
    window.loadDataQuartil();

    // Auto-refresh every 30 seconds (30000 ms)
    

    function showError(message) {
        loadingState.classList.add('hidden');
        errorState.textContent = message;
        errorState.classList.remove('hidden');
    }

    function populateOperationsDropdown(ops) {
        ops.forEach(op => {
            const option = document.createElement('option');
            option.value = op;
            option.textContent = op;
            filterOp.appendChild(option);
        });

        // Set up change event listeners
        filterOp.addEventListener('change', window.renderQuartilDashboard);
        filterQuartilHO.addEventListener('change', window.renderQuartilDashboard);
        filterQuartilPromessa.addEventListener('change', window.renderQuartilDashboard);
        searchAgent.addEventListener('input', window.renderQuartilDashboard);
    }

    function getQuartileClass(quartil) {
        if (!quartil) return "q-empty";
        if (quartil.includes("1º")) return "q1";
        if (quartil.includes("2º")) return "q2";
        if (quartil.includes("3º")) return "q3";
        if (quartil.includes("4º")) return "q4";
        return "q-empty";
    }

    window.renderQuartilDashboard = function() {
        const opVal = filterOp.value;
        const qHOVal = filterQuartilHO.value;
        const qPromVal = filterQuartilPromessa.value;
        const searchVal = searchAgent.value.toLowerCase().trim();

        // 1. Filter the dataset
        const filtered = allAgents.filter(item => {
            const matchOp = opVal === 'all' || item.Operacao === opVal;
            const matchQHO = qHOVal === 'all' || item.Quartil_HO === qHOVal;
            const matchQProm = qPromVal === 'all' || item.Quartil_Promessas === qPromVal;
            const matchSearch = item.Agente.toLowerCase().includes(searchVal) || 
                                item.Matricula.toLowerCase().includes(searchVal);
            return matchOp && matchQHO && matchQProm && matchSearch;
        });

        // Sort by Quartil_HO first, then by Dispersao_HO descending within each quartile
        const getQuartileScore = (qStr) => {
            if (!qStr || qStr === '—') return 10;
            const match = qStr.match(/(\d+)º/);
            return match ? parseInt(match[1]) : 10;
        };

        filtered.sort((a, b) => {
            const qHOA = getQuartileScore(a.Quartil_HO);
            const qHOB = getQuartileScore(b.Quartil_HO);
            if (qHOA !== qHOB) {
                return qHOA - qHOB;
            }
            // Sort by Dispersao_HO descending (best dispersion to worst)
            const dispA = a.Dispersao_HO !== null ? a.Dispersao_HO : -1;
            const dispB = b.Dispersao_HO !== null ? b.Dispersao_HO : -1;
            if (dispA !== dispB) {
                return dispB - dispA;
            }
            // Finally alphabetically by name
            return a.Agente.localeCompare(b.Agente);
        });

        // === Q4 PAGE UPDATES ===
        const q4Agents = allAgents.filter(item => {
            const matchOp = opVal === 'all' || item.Operacao === opVal;
            const isQ4 = item.Quartil_HO === '4º Quartil';
            return matchOp && isQ4;
        });

        const q4TotalOperadores = document.getElementById('q4TotalOperadores');
        const q4MediaDispersao = document.getElementById('q4MediaDispersao');
        const q4StatusMeta = document.getElementById('q4StatusMeta');
        const q4StatusMetaSub = document.getElementById('q4StatusMetaSub');
        const q4ImpactoEstimado = document.getElementById('q4ImpactoEstimado');
        const q4OperatorsTableBody = document.getElementById('q4OperatorsTableBody');

        if (q4TotalOperadores) {
            q4TotalOperadores.textContent = q4Agents.length;
            const q4Dispersions = q4Agents.filter(item => item.Dispersao_HO !== null).map(item => item.Dispersao_HO);
            const avgQ4Disp = q4Dispersions.length > 0 ? (q4Dispersions.reduce((x, y) => x + y, 0) / q4Dispersions.length) : 0;
            q4MediaDispersao.textContent = q4Dispersions.length > 0 ? `${avgQ4Disp.toFixed(1)}%` : "—";

            if (q4Dispersions.length === 0) {
                q4StatusMeta.textContent = "—";
                q4StatusMeta.className = "kpi-value";
                q4StatusMetaSub.textContent = "Sem lançamentos";
            } else if (avgQ4Disp >= 50) {
                q4StatusMeta.textContent = "Atingida ✅";
                q4StatusMeta.className = "kpi-value text-success";
                q4StatusMetaSub.textContent = "Média de dispersão ≥ 50%";
            } else {
                q4StatusMeta.textContent = "Abaixo ❌";
                q4StatusMeta.className = "kpi-value text-danger";
                q4StatusMetaSub.textContent = `Falta ${(50 - avgQ4Disp).toFixed(1)}% para a meta`;
            }

            // Calculate estimated recovery impact
            const opMinMax = {};
            allAgents.forEach(itm => {
                if (itm.HO !== null) {
                    const op = itm.Operacao;
                    if (!opMinMax[op]) {
                        opMinMax[op] = { min: Infinity, max: -Infinity };
                    }
                    if (itm.HO < opMinMax[op].min) opMinMax[op].min = itm.HO;
                    if (itm.HO > opMinMax[op].max) opMinMax[op].max = itm.HO;
                }
            });

            let totalImpact = 0;
            q4Agents.forEach(itm => {
                const op = itm.Operacao;
                const minMax = opMinMax[op];
                if (minMax && minMax.max > minMax.min && itm.HO !== null) {
                    const targetHO = minMax.min + 0.5 * (minMax.max - minMax.min);
                    if (itm.HO < targetHO) {
                        totalImpact += (targetHO - itm.HO);
                    }
                }
            });
            q4ImpactoEstimado.textContent = totalImpact > 0 ? totalImpact.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "R$ 0,00";

            // Populate table
            const q4AgentsSorted = [...q4Agents].sort((x, y) => {
                const dispX = x.Dispersao_HO !== null ? x.Dispersao_HO : 0;
                const dispY = y.Dispersao_HO !== null ? y.Dispersao_HO : 0;
                return dispX - dispY; // worst first
            });

            if (q4AgentsSorted.length === 0) {
                q4OperatorsTableBody.innerHTML = `
                    <tr>
                        <td colspan="3" style="text-align: center; padding: 40px; color: var(--muted); font-weight: 600;">
                            🎉 Excelente! Nenhum operador no 4º Quartil nesta operação.
                        </td>
                    </tr>
                `;
            } else {
                q4OperatorsTableBody.innerHTML = q4AgentsSorted.map(itm => {
                    const hoValStr = itm.HO !== null ? itm.HO.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "—";
                    const dispVal = itm.Dispersao_HO !== null ? itm.Dispersao_HO : 0;
                    const dispStr = itm.Dispersao_HO !== null ? itm.Dispersao_HO.toFixed(1) + "%" : "—";
                    const dispColor = dispVal < 50 ? "text-danger" : "text-success";
                    
                    return `
                        <tr>
                            <td style="padding: 12px 8px; border-bottom: 1px solid #eef7f2;">
                                <div style="font-weight: 600; color: var(--text);">${itm.Agente}</div>
                                <div style="font-size: 0.7rem; color: var(--muted);">Matrícula: ${itm.Matricula}</div>
                            </td>
                            <td style="padding: 12px 8px; border-bottom: 1px solid #eef7f2;">
                                <span class="agent-card-op-badge" style="margin-top:0; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${itm.Operacao}">${itm.Operacao}</span>
                            </td>
                            <td style="padding: 12px 8px; border-bottom: 1px solid #eef7f2; text-align: right;">
                                <div style="font-weight: 700; color: var(--text);">${hoValStr}</div>
                                <div style="font-size: 0.72rem; font-weight: 600;" class="${dispColor}">${dispStr}</div>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        }

        // 1.5. Render portfolio summary cards
        const carteirasGrid = document.getElementById('carteirasGrid');
        if (carteirasGrid && originalStats.carteiras) {
            const filteredCarteiras = originalStats.carteiras.filter(c => opVal === 'all' || c.operacao === opVal);
            carteirasGrid.innerHTML = filteredCarteiras.map(c => {
                const hoProdStr = c.media_ho.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                const hoDispStr = c.media_dispersao_ho.toFixed(1) + "%";
                const hoFillWidth = c.media_dispersao_ho;
                
                const promProdStr = Math.round(c.media_promessas).toLocaleString('pt-BR');
                const promDispStr = c.media_dispersao_promessas.toFixed(1) + "%";
                const promFillWidth = c.media_dispersao_promessas;
                
                const getDispClass = (val) => {
                    if (val >= 75) return 'q1';
                    if (val >= 50) return 'q2';
                    if (val >= 25) return 'q3';
                    return 'q4';
                };
                
                const hoDispClass = getDispClass(c.media_dispersao_ho);
                const promDispClass = getDispClass(c.media_dispersao_promessas);
                
                let carteiraNomeAmigavel = c.operacao;
                if (c.operacao.includes('/')) {
                    carteiraNomeAmigavel = c.operacao.split('/')[1].trim();
                } else if (c.operacao.includes('-')) {
                    carteiraNomeAmigavel = c.operacao.split('-')[1].trim();
                }

                const renderQDisp = (qMap, qKey) => {
                    const val = qMap ? qMap[qKey] : null;
                    return val !== null && val !== undefined ? `${val.toFixed(1)}%` : "—";
                };

                const renderQProdHO = (qMap, qKey) => {
                    const val = qMap ? qMap[qKey] : null;
                    return val !== null && val !== undefined ? val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }) : "—";
                };

                const renderQProdProm = (qMap, qKey) => {
                    const val = qMap ? qMap[qKey] : null;
                    return val !== null && val !== undefined ? Math.round(val).toLocaleString('pt-BR') : "—";
                };

                const getQClass = (qMap, qKey, defaultClass) => {
                    const val = qMap ? qMap[qKey] : null;
                    return val !== null && val !== undefined ? defaultClass : "empty";
                };

                const hoQ1 = renderQDisp(c.ho_quartil_disp, "1º Quartil");
                const hoQ2 = renderQDisp(c.ho_quartil_disp, "2º Quartil");
                const hoQ3 = renderQDisp(c.ho_quartil_disp, "3º Quartil");
                const hoQ4 = renderQDisp(c.ho_quartil_disp, "4º Quartil");

                const hoProdQ1 = renderQProdHO(c.ho_quartil_prod, "1º Quartil");
                const hoProdQ2 = renderQProdHO(c.ho_quartil_prod, "2º Quartil");
                const hoProdQ3 = renderQProdHO(c.ho_quartil_prod, "3º Quartil");
                const hoProdQ4 = renderQProdHO(c.ho_quartil_prod, "4º Quartil");

                const promQ1 = renderQDisp(c.prom_quartil_disp, "1º Quartil");
                const promQ2 = renderQDisp(c.prom_quartil_disp, "2º Quartil");
                const promQ3 = renderQDisp(c.prom_quartil_disp, "3º Quartil");
                const promQ4 = renderQDisp(c.prom_quartil_disp, "4º Quartil");

                const promProdQ1 = renderQProdProm(c.prom_quartil_prod, "1º Quartil");
                const promProdQ2 = renderQProdProm(c.prom_quartil_prod, "2º Quartil");
                const promProdQ3 = renderQProdProm(c.prom_quartil_prod, "3º Quartil");
                const promProdQ4 = renderQProdProm(c.prom_quartil_prod, "4º Quartil");

                return `
                    <div class="carteira-card card">
                        <div class="carteira-header">
                            <span class="carteira-icon">💼</span>
                            <div style="display:flex; flex-direction:column;">
                                <h4 class="carteira-title">${carteiraNomeAmigavel}</h4>
                                <span style="font-size: 0.68rem; color: var(--muted); font-weight: 500;">${c.operacao} · ${c.qtd_agentes} operadores ativos</span>
                            </div>
                        </div>
                        <div class="carteira-body">
                            <!-- H.O Column -->
                            <div class="carteira-col">
                                <div class="indicator-title">Honorários (H.O)</div>
                                <div class="indicator-stats">
                                    <div class="stat-item">
                                        <span class="stat-label">Produção Média:</span>
                                        <span class="stat-val" style="color: var(--navy);">${hoProdStr}</span>
                                    </div>
                                    <div class="stat-item" style="margin-top: 4px;">
                                        <span class="stat-label">Dispersão Média:</span>
                                        <span class="stat-val ${c.media_dispersao_ho < 50 ? 'text-danger' : 'text-success'}">${hoDispStr}</span>
                                    </div>
                                </div>
                                <div class="dispersion-wrap" style="margin-top: 10px;">
                                    <div class="disp-bar-track" style="height: 6px;">
                                        <div class="disp-bar-fill ${hoDispClass}" style="width: ${hoFillWidth}%"></div>
                                    </div>
                                </div>
                                <div style="font-size: 0.62rem; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-top: 14px; border-top: 1.5px solid #eef7f2; padding-top: 8px; letter-spacing: 0.03em;">Média de Dispersão por Quartil</div>
                                <div class="quartil-disp-breakdown">
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_disp, "1º Quartil", "q1")}" title="1º Quartil H.O">Q1: ${hoQ1}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_disp, "2º Quartil", "q2")}" title="2º Quartil H.O">Q2: ${hoQ2}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_disp, "3º Quartil", "q3")}" title="3º Quartil H.O">Q3: ${hoQ3}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_disp, "4º Quartil", "q4")}" title="4º Quartil H.O">Q4: ${hoQ4}</span>
                                </div>
                                <div style="font-size: 0.62rem; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-top: 10px; border-top: 1.5px solid #eef7f2; padding-top: 8px; letter-spacing: 0.03em;">Média de Produção por Quartil</div>
                                <div class="quartil-disp-breakdown" style="margin-top: 6px;">
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_prod, "1º Quartil", "q1")}" title="1º Quartil H.O Produção">Q1: ${hoProdQ1}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_prod, "2º Quartil", "q2")}" title="2º Quartil H.O Produção">Q2: ${hoProdQ2}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_prod, "3º Quartil", "q3")}" title="3º Quartil H.O Produção">Q3: ${hoProdQ3}</span>
                                    <span class="q-mini-badge ${getQClass(c.ho_quartil_prod, "4º Quartil", "q4")}" title="4º Quartil H.O Produção">Q4: ${hoProdQ4}</span>
                                </div>
                            </div>
                            
                            <!-- Promessas Column -->
                            <div class="carteira-col">
                                <div class="indicator-title">Promessas de Pagamento</div>
                                <div class="indicator-stats">
                                    <div class="stat-item">
                                        <span class="stat-label">Produção Média:</span>
                                        <span class="stat-val" style="color: var(--navy);">${promProdStr} <span style="font-size:0.75rem; font-weight:500; color:var(--muted)">prom.</span></span>
                                    </div>
                                    <div class="stat-item" style="margin-top: 4px;">
                                        <span class="stat-label">Dispersão Média:</span>
                                        <span class="stat-val ${c.media_dispersao_promessas < 50 ? 'text-danger' : 'text-success'}">${promDispStr}</span>
                                    </div>
                                </div>
                                <div class="dispersion-wrap" style="margin-top: 10px;">
                                    <div class="disp-bar-track" style="height: 6px;">
                                        <div class="disp-bar-fill ${promDispClass}" style="width: ${promFillWidth}%"></div>
                                    </div>
                                </div>
                                <div style="font-size: 0.62rem; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-top: 14px; border-top: 1.5px solid #eef7f2; padding-top: 8px; letter-spacing: 0.03em;">Média de Dispersão por Quartil</div>
                                <div class="quartil-disp-breakdown">
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_disp, "1º Quartil", "q1")}" title="1º Quartil Promessas">Q1: ${promQ1}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_disp, "2º Quartil", "q2")}" title="2º Quartil Promessas">Q2: ${promQ2}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_disp, "3º Quartil", "q3")}" title="3º Quartil Promessas">Q3: ${promQ3}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_disp, "4º Quartil", "q4")}" title="4º Quartil Promessas">Q4: ${promQ4}</span>
                                </div>
                                <div style="font-size: 0.62rem; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-top: 10px; border-top: 1.5px solid #eef7f2; padding-top: 8px; letter-spacing: 0.03em;">Média de Produção por Quartil</div>
                                <div class="quartil-disp-breakdown" style="margin-top: 6px;">
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_prod, "1º Quartil", "q1")}" title="1º Quartil Promessas Produção">Q1: ${promProdQ1}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_prod, "2º Quartil", "q2")}" title="2º Quartil Promessas Produção">Q2: ${promProdQ2}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_prod, "3º Quartil", "q3")}" title="3º Quartil Promessas Produção">Q3: ${promProdQ3}</span>
                                    <span class="q-mini-badge ${getQClass(c.prom_quartil_prod, "4º Quartil", "q4")}" title="4º Quartil Promessas Produção">Q4: ${promProdQ4}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // 2. Update KPI values dynamically based on filtered records
        kpiTotalAgentes.textContent = filtered.length;
        
        // Calculate dynamic averages for filtered list
        const validHOs = filtered.filter(item => item.HO !== null).map(item => item.HO);
        const avgHO = validHOs.length > 0 ? (validHOs.reduce((a, b) => a + b, 0) / validHOs.length) : 0;
        kpiMediaHO.textContent = avgHO > 0 ? avgHO.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "—";

        const validProms = filtered.filter(item => item.Promessas !== null).map(item => item.Promessas);
        const avgProm = validProms.length > 0 ? (validProms.reduce((a, b) => a + b, 0) / validProms.length) : 0;
        kpiMediaPromessas.textContent = avgProm > 0 ? Math.round(avgProm).toLocaleString('pt-BR') : "—";

        const uniqueOps = [...new Set(filtered.map(item => item.Operacao))];
        kpiTotalOperacoes.textContent = uniqueOps.length;

        // 3. Update Quartil counts box (shows H.O / PROMESSAS counts side-by-side)
        const counts = {
            q1: { ho: 0, prom: 0 },
            q2: { ho: 0, prom: 0 },
            q3: { ho: 0, prom: 0 },
            q4: { ho: 0, prom: 0 }
        };

        filtered.forEach(item => {
            if (item.Quartil_HO.includes("1º")) counts.q1.ho++;
            if (item.Quartil_HO.includes("2º")) counts.q2.ho++;
            if (item.Quartil_HO.includes("3º")) counts.q3.ho++;
            if (item.Quartil_HO.includes("4º")) counts.q4.ho++;

            if (item.Quartil_Promessas.includes("1º")) counts.q1.prom++;
            if (item.Quartil_Promessas.includes("2º")) counts.q2.prom++;
            if (item.Quartil_Promessas.includes("3º")) counts.q3.prom++;
            if (item.Quartil_Promessas.includes("4º")) counts.q4.prom++;
        });

        q1Count.innerHTML = `<span style="font-size: 1.3rem;">${counts.q1.ho}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> HO</span> &nbsp;|&nbsp; <span style="font-size: 1.3rem;">${counts.q1.prom}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> PROM</span>`;
        q2Count.innerHTML = `<span style="font-size: 1.3rem;">${counts.q2.ho}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> HO</span> &nbsp;|&nbsp; <span style="font-size: 1.3rem;">${counts.q2.prom}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> PROM</span>`;
        q3Count.innerHTML = `<span style="font-size: 1.3rem;">${counts.q3.ho}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> HO</span> &nbsp;|&nbsp; <span style="font-size: 1.3rem;">${counts.q3.prom}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> PROM</span>`;
        q4Count.innerHTML = `<span style="font-size: 1.3rem;">${counts.q4.ho}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> HO</span> &nbsp;|&nbsp; <span style="font-size: 1.3rem;">${counts.q4.prom}</span><span style="font-size:0.75rem; font-weight:500; color:var(--muted)"> PROM</span>`;

        // 4. Render cards
        if (filtered.length === 0) {
            agentsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; color: var(--muted); padding: 40px; background: var(--card); border: 1px solid var(--border); border-radius: 14px;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">🔍</div>
                    <p style="font-weight: 600;">Nenhum operador encontrado com os filtros selecionados.</p>
                </div>
            `;
            return;
        }

        agentsGrid.innerHTML = filtered.map(item => {
            const hoClass = getQuartileClass(item.Quartil_HO);
            const promClass = getQuartileClass(item.Quartil_Promessas);

            const hoValStr = item.HO !== null ? item.HO.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "—";
            const hoDispStr = item.Dispersao_HO !== null ? item.Dispersao_HO.toFixed(1) + "%" : "—";
            const hoFillWidth = item.Dispersao_HO !== null ? item.Dispersao_HO : 0;
            const hoFillClass = item.Quartil_HO !== "—" ? hoClass : "q-empty";

            const promValStr = item.Promessas !== null ? item.Promessas.toLocaleString('pt-BR') : "—";
            const promDispStr = item.Dispersao_Promessas !== null ? item.Dispersao_Promessas.toFixed(1) + "%" : "—";
            const promFillWidth = item.Dispersao_Promessas !== null ? item.Dispersao_Promessas : 0;
            const promFillClass = item.Quartil_Promessas !== "—" ? promClass : "q-empty";

            const isQ4 = item.Quartil_HO.includes("4º") || item.Quartil_Promessas.includes("4º");
            const nameClass = isQ4 ? "agent-card-name q4-highlighted-name" : "agent-card-name";
            const nameBadge = isQ4 ? ` <span class="q4-alert-badge" title="Operador no 4º Quartil em pelo menos um indicador">⚠️ 4º Q</span>` : "";

            return `
                <div class="agent-card">
                    <div class="agent-card-header">
                        <div class="agent-card-info">
                            <div class="${nameClass}">${item.Agente}${nameBadge}</div>
                            <div class="agent-card-matricula">Matrícula: ${item.Matricula}</div>
                        </div>
                    </div>
                    <div class="agent-card-op-badge" title="${item.Operacao}">${item.Operacao}</div>
                    
                    <div class="agent-metric-section">
                        <!-- H.O Metric Group -->
                        <div class="agent-metric-row">
                            <div class="agent-metric-header">
                                <span class="agent-metric-title">Honorários (H.O)</span>
                                <span class="q-badge ${hoFillClass}">${item.Quartil_HO}</span>
                            </div>
                            <div class="agent-metric-value-box">
                                <span class="agent-metric-value">${hoValStr}</span>
                            </div>
                            <div class="dispersion-wrap">
                                <div class="dispersion-header-row">
                                    <span>Dispersão</span>
                                    <span class="dispersion-value">${hoDispStr}</span>
                                </div>
                                <div class="disp-bar-track">
                                    <div class="disp-bar-fill ${hoFillClass}" style="width: ${hoFillWidth}%"></div>
                                </div>
                            </div>
                        </div>

                        <!-- PROMESSAS Metric Group -->
                        <div class="agent-metric-row">
                            <div class="agent-metric-header">
                                <span class="agent-metric-title">Promessas de Pagamento</span>
                                <span class="q-badge ${promFillClass}">${item.Quartil_Promessas}</span>
                            </div>
                            <div class="agent-metric-value-box">
                                <span class="agent-metric-value">${promValStr}</span>
                                <span class="agent-metric-unit">prom.</span>
                            </div>
                            <div class="dispersion-wrap">
                                <div class="dispersion-header-row">
                                    <span>Dispersão</span>
                                    <span class="dispersion-value">${promDispStr}</span>
                                </div>
                                <div class="disp-bar-track">
                                    <div class="disp-bar-fill ${promFillClass}" style="width: ${promFillWidth}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
};
