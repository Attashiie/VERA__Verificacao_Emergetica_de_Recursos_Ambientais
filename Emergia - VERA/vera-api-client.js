/**
 * vera-api-client.js
 * Cliente JavaScript para conectar o HTML com a API Flask
 * Coloque esse script no HTML antes do script principal
 */

const API_URL = 'http://localhost:5000/api';

/**
 * Cliente da API VERA
 */
const VeraAPI = {
    /**
     * Calcula emergia
     */
    async calcular(projeto) {
        try {
            const response = await fetch(`${API_URL}/calcular`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projeto)
            });
            
            if (!response.ok) {
                const erro = await response.json();
                throw new Error(erro.erro || 'Erro na requisição');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao calcular:', error);
            throw error;
        }
    },
    
    /**
     * Obtém lista de UEVs
     */
    async obterUEVs() {
        try {
            const response = await fetch(`${API_URL}/uevs`);
            if (!response.ok) throw new Error('Erro ao obter UEVs');
            return await response.json();
        } catch (error) {
            console.error('Erro ao obter UEVs:', error);
            throw error;
        }
    },
    
    /**
     * Busca UEV específica
     */
    async buscarUEV(recurso) {
        try {
            const response = await fetch(`${API_URL}/uevs/buscar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recurso })
            });
            if (!response.ok) throw new Error('UEV não encontrado');
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar UEV:', error);
            throw error;
        }
    },
    
    /**
     * Salva projeto
     */
    async salvarProjeto(projeto, nomeArquivo = 'projeto.json') {
        try {
            const response = await fetch(`${API_URL}/salvar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...projeto, nome_arquivo: nomeArquivo })
            });
            if (!response.ok) throw new Error('Erro ao salvar projeto');
            return await response.json();
        } catch (error) {
            console.error('Erro ao salvar projeto:', error);
            throw error;
        }
    },
    
    /**
     * Lista projetos salvos
     */
    async listarProjetos() {
        try {
            const response = await fetch(`${API_URL}/projetos`);
            if (!response.ok) throw new Error('Erro ao listar projetos');
            return await response.json();
        } catch (error) {
            console.error('Erro ao listar projetos:', error);
            throw error;
        }
    },
    
    /**
     * Carrega projeto
     */
    async carregarProjeto(nome) {
        try {
            const response = await fetch(`${API_URL}/projeto/${encodeURIComponent(nome)}`);
            if (!response.ok) throw new Error('Projeto não encontrado');
            return await response.json();
        } catch (error) {
            console.error('Erro ao carregar projeto:', error);
            throw error;
        }
    },
    
    /**
     * Valida matriz
     */
    async validarMatriz(A, n) {
        try {
            const response = await fetch(`${API_URL}/validar-matriz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ A, n })
            });
            return await response.json();
        } catch (error) {
            console.error('Erro ao validar matriz:', error);
            throw error;
        }
    },
    
    /**
     * Obtém status da API
     */
    async obterStatus() {
        try {
            const response = await fetch(`${API_URL}/status`);
            if (!response.ok) throw new Error('Erro ao obter status');
            return await response.json();
        } catch (error) {
            console.error('Erro ao obter status:', error);
            throw error;
        }
    }
};

/**
 * Integração com o sistema VERA existente
 * Substitui a função runCalculation para usar a API
 */
function runCalculationViaAPI() {
    if (!state.current) {
        setStatus('Nenhum projeto carregado. Crie ou selecione um projeto.', 'err');
        return;
    }
    
    const { n, A, R, uevs, types, processNames, name } = state.current;
    
    // Prepara dados para enviar
    const projeto = {
        name: name,
        n: n,
        A: A,
        R: R,
        uevs: uevs,
        types: types,
        process_names: processNames
    };
    
    // Mostra indicador de carregamento
    setStatus('Calculando emergia via API...', 'info');
    
    // Chama API
    VeraAPI.calcular(projeto)
        .then(resultado => {
            if (resultado.sucesso) {
                // Processa resultado
                state.results = {
                    E_phys: resultado.processos.map(p => p.E_fisico),
                    E_solar: resultado.processos.map(p => p.E_solar),
                    totalEm: resultado.indicadores.emergia_total,
                    renEm: resultado.indicadores.emergia_renovavel,
                    nonRenEm: resultado.indicadores.emergia_nao_renovavel,
                    EYR: resultado.indicadores.EYR,
                    ELR: resultado.indicadores.ELR,
                    ESI: resultado.indicadores.ESI,
                    EDE: resultado.indicadores.EDE,
                    processNames: processNames,
                    types: types,
                    name: name,
                    n: n
                };
                
                setStatus(resultado.mensagem_sucesso, 'ok');
                renderResults();
                showView('results');
            } else {
                setStatus('Erro: ' + resultado.erro, 'err');
            }
        })
        .catch(error => {
            setStatus('Erro na API: ' + error.message, 'err');
        });
}

/**
 * Carrega UEVs do banco de dados
 */
function carregarUEVsDoServidor() {
    setStatus('Carregando UEVs...', 'info');
    
    VeraAPI.obterUEVs()
        .then(resultado => {
            if (resultado.sucesso) {
                // Converte para formato esperado
                const uevs = [];
                for (const categoria in resultado.categorias) {
                    uevs.push(...resultado.categorias[categoria]);
                }
                
                state.uevDb = uevs;
                setStatus(`Carregadas ${resultado.total} transformidades do servidor`, 'ok');
            }
        })
        .catch(error => {
            setStatus('Erro ao carregar UEVs: ' + error.message, 'err');
        });
}

/**
 * Salva projeto no servidor
 */
function salvarProjetoNoServidor() {
    if (!state.current) {
        setStatus('Nenhum projeto carregado para salvar.', 'err');
        return;
    }
    
    const { n, A, R, uevs, types, processNames, name } = state.current;
    
    const projeto = {
        name: name,
        n: n,
        A: A,
        R: R,
        uevs: uevs,
        types: types,
        process_names: processNames
    };
    
    setStatus('Salvando projeto...', 'info');
    
    VeraAPI.salvarProjeto(projeto)
        .then(resultado => {
            if (resultado.sucesso) {
                setStatus(resultado.mensagem, 'ok');
            } else {
                setStatus('Erro: ' + resultado.erro, 'err');
            }
        })
        .catch(error => {
            setStatus('Erro ao salvar: ' + error.message, 'err');
        });
}

/**
 * Inicializa a integração com a API
 * Verifica se o servidor está rodando
 */
function inicializarAPI() {
    VeraAPI.obterStatus()
        .then(resultado => {
            console.log('API conectada:', resultado);
            setStatus('Conectado ao servidor VERA (Python)', 'ok');
        })
        .catch(error => {
            console.warn('API não disponível. Usando modo local.');
            setStatus('Usando modo local (sem servidor Python)', 'warn');
        });
}

// Sobrescreve a função original se a API estiver disponível
document.addEventListener('DOMContentLoaded', function() {
    // Tenta conectar à API
    VeraAPI.obterStatus()
        .then(() => {
            // API disponível - sobrescreve funções
            window.runCalculation = runCalculationViaAPI;
            window.salvarProjetoNoServidor = salvarProjetoNoServidor;
            
            console.log('[VERA] Conectado ao servidor Flask - usando API Python');
        })
        .catch(() => {
            // API não disponível - usa modo local
            console.log('[VERA] Servidor Flask não encontrado - usando modo local');
        });
});

// Exporta para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VeraAPI;
}
