/**
 * DashboardService - Serviço para comunicação com APIs do dashboard
 */

class DashboardService {
    /**
     * Busca métricas completas do dashboard
     * @param {number} days - Número de dias para filtrar (padrão: 7)
     * @param {number} restauranteId - ID do restaurante (padrão: 1)
     * @returns {Promise<Object>} Dados completos do dashboard
     */
    static async fetchMetrics(days = 7, restauranteId = 1) {
        try {
            const url = new URL(window.DASHBOARD_CONFIG.apiBaseUrl);
            url.searchParams.append('days', days.toString());
            url.searchParams.append('restaurante_id', restauranteId.toString());
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.DASHBOARD_CONFIG.csrfToken
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result.data || result;
            
        } catch (error) {
            console.error('Erro ao buscar métricas do dashboard:', error);
            throw error;
        }
    }
    
    /**
     * Busca dados para o gráfico de vendas
     * @param {number} days - Número de dias para filtrar
     * @param {number} restauranteId - ID do restaurante
     * @returns {Promise<Object>} Dados do gráfico de vendas
     */
    static async fetchSalesChart(days = 7, restauranteId = 1) {
        try {
            const url = new URL(window.DASHBOARD_CONFIG.salesChartUrl);
            url.searchParams.append('days', days.toString());
            url.searchParams.append('restaurante_id', restauranteId.toString());
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.DASHBOARD_CONFIG.csrfToken
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result.data || result;
            
        } catch (error) {
            console.error('Erro ao buscar dados do gráfico:', error);
            throw error;
        }
    }
    
    /**
     * Busca produtos mais vendidos
     * @param {number} days - Número de dias para filtrar
     * @param {number} restauranteId - ID do restaurante
     * @param {number} limit - Limite de produtos a retornar
     * @returns {Promise<Object>} Lista dos produtos mais vendidos
     */
    static async fetchTopProducts(days = 7, restauranteId = 1, limit = 5) {
        try {
            const url = new URL(window.DASHBOARD_CONFIG.topProductsUrl);
            url.searchParams.append('days', days.toString());
            url.searchParams.append('restaurante_id', restauranteId.toString());
            url.searchParams.append('limit', limit.toString());
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.DASHBOARD_CONFIG.csrfToken
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result.data || result;
            
        } catch (error) {
            console.error('Erro ao buscar top produtos:', error);
            throw error;
        }
    }
    
    /**
     * Busca todas as métricas em paralelo
     * @param {number} days - Número de dias
     * @param {number} restauranteId - ID do restaurante
     * @returns {Promise<Object>} Objeto com todos os dados
     */
    static async fetchAllData(days = 7, restauranteId = 1) {
        try {
            const [metrics, salesChart, topProducts] = await Promise.allSettled([
                this.fetchMetrics(days, restauranteId),
                this.fetchSalesChart(days, restauranteId),
                this.fetchTopProducts(days, restauranteId)
            ]);
            
            const result = {};
            
            // Processar resultados
            if (metrics.status === 'fulfilled') {
                result.metrics = metrics.value;
            } else {
                console.error('Erro ao buscar métricas:', metrics.reason);
                result.metrics = null;
                result.metricsError = metrics.reason.message;
            }
            
            if (salesChart.status === 'fulfilled') {
                result.salesChart = salesChart.value;
            } else {
                console.error('Erro ao buscar gráfico:', salesChart.reason);
                result.salesChart = null;
                result.salesChartError = salesChart.reason.message;
            }
            
            if (topProducts.status === 'fulfilled') {
                result.topProducts = topProducts.value;
            } else {
                console.error('Erro ao buscar top produtos:', topProducts.reason);
                result.topProducts = null;
                result.topProductsError = topProducts.reason.message;
            }
            
            return result;
            
        } catch (error) {
            console.error('Erro ao buscar dados do dashboard:', error);
            throw error;
        }
    }
    
    /**
     * Valida se a configuração do dashboard está disponível
     * @returns {boolean} True se configuração está válida
     */
    static isConfigValid() {
        return (
            window.DASHBOARD_CONFIG &&
            window.DASHBOARD_CONFIG.apiBaseUrl &&
            window.DASHBOARD_CONFIG.salesChartUrl &&
            window.DASHBOARD_CONFIG.topProductsUrl
        );
    }
    
    /**
     * Formata valor monetário
     * @param {number} value - Valor a ser formatado
     * @returns {string} Valor formatado em reais
     */
    static formatCurrency(value) {
        if (typeof value !== 'number') {
            value = parseFloat(value) || 0;
        }
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }
    
    /**
     * Formata data para exibição
     * @param {string|Date} date - Data a ser formatada
     * @returns {string} Data formatada
     */
    static formatDate(date) {
        if (!date) return '';
        
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(dateObj);
    }
    
    /**
     * Calcula percentual de variação
     * @param {number} current - Valor atual
     * @param {number} previous - Valor anterior
     * @returns {Object} Objeto com percentual e direção
     */
    static calculatePercentageChange(current, previous) {
        if (!previous || previous === 0) {
            return { percentage: 0, direction: 'neutral', isValid: false };
        }
        
        const percentage = ((current - previous) / previous) * 100;
        const direction = percentage > 0 ? 'positive' : percentage < 0 ? 'negative' : 'neutral';
        
        return {
            percentage: Math.abs(percentage).toFixed(1),
            direction,
            isValid: true
        };
    }
}

export default DashboardService;