/**
 * SalesChart - Componente para exibir gráfico de vendas
 */

import React, { useEffect, useRef } from 'react';

const SalesChart = ({ data, loading, period }) => {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    
    // Fallback para dados vazios
    const defaultData = {
        sales_by_hour: Array.from({ length: 24 }, (_, i) => ({ hour: i, count: 0 }))
    };
    
    const chartData = data?.sales_by_hour || defaultData.sales_by_hour;
    
    /**
     * Renderiza gráfico simples com Canvas (fallback se Chart.js não estiver disponível)
     */
    const renderSimpleChart = () => {
        const canvas = chartRef.current;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const { width, height } = canvas;
        
        // Limpar canvas
        ctx.clearRect(0, 0, width, height);
        
        // Configurações
        const padding = 40;
        const chartWidth = width - (padding * 2);
        const chartHeight = height - (padding * 2);
        
        // Encontrar valor máximo
        const maxValue = Math.max(...chartData.map(d => d.count), 1);
        
        // Cores
        const barColor = '#667eea';
        const textColor = '#343a40';
        const gridColor = '#e9ecef';
        
        // Desenhar grid
        ctx.strokeStyle = gridColor;
        ctx.lineWidth = 1;
        
        // Linhas horizontais
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Calcular largura das barras
        const barWidth = chartWidth / chartData.length;
        const barPadding = barWidth * 0.1;
        const actualBarWidth = barWidth - barPadding;
        
        // Desenhar barras
        ctx.fillStyle = barColor;
        chartData.forEach((item, index) => {
            const barHeight = (item.count / maxValue) * chartHeight;
            const x = padding + (index * barWidth) + (barPadding / 2);
            const y = height - padding - barHeight;
            
            ctx.fillRect(x, y, actualBarWidth, barHeight);
        });
        
        // Desenhar labels do eixo X (a cada 4 horas)
        ctx.fillStyle = textColor;
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        for (let i = 0; i < 24; i += 4) {
            const x = padding + (i * barWidth) + (barWidth / 2);
            const y = height - 10;
            ctx.fillText(`${i}h`, x, y);
        }
        
        // Desenhar labels do eixo Y
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const value = Math.round((maxValue / 5) * (5 - i));
            const y = padding + (chartHeight / 5) * i + 4;
            ctx.fillText(value.toString(), padding - 10, y);
        }
        
        // Título
        ctx.textAlign = 'center';
        ctx.font = 'bold 14px Arial';
        ctx.fillText('Vendas por Hora', width / 2, 20);
    };
    
    /**
     * Inicializa Chart.js se disponível
     */
    const initChartJS = () => {
        if (typeof Chart === 'undefined') {
            renderSimpleChart();
            return;
        }
        
        const ctx = chartRef.current.getContext('2d');
        
        // Destruir instância anterior
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }
        
        // Configurar dados
        const labels = chartData.map(item => `${item.hour}h`);
        const values = chartData.map(item => item.count);
        
        chartInstance.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Número de Vendas',
                    data: values,
                    backgroundColor: '#667eea',
                    borderColor: '#4c63d2',
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Vendas por Hora',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const hour = context[0].label.replace('h', '');
                                return `${hour}:00 - ${parseInt(hour) + 1}:00`;
                            },
                            label: function(context) {
                                const count = context.parsed.y;
                                return `${count} ${count === 1 ? 'venda' : 'vendas'}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Hora do Dia'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Número de Vendas'
                        },
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    };
    
    // Renderizar gráfico quando dados mudarem
    useEffect(() => {
        if (!loading && chartData) {
            // Aguardar um pouco para garantir que o canvas esteja pronto
            setTimeout(() => {
                initChartJS();
            }, 100);
        }
        
        // Cleanup ao desmontar
        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
                chartInstance.current = null;
            }
        };
    }, [chartData, loading]);
    
    // Calcular estatísticas
    const totalSales = chartData.reduce((sum, item) => sum + item.count, 0);
    const peakHour = chartData.reduce((max, item) => item.count > max.count ? item : max, { hour: 0, count: 0 });
    const avgPerHour = totalSales / 24;
    
    return (
        <div className="sales-chart">
            <div className="chart-header">
                <h3>📈 Vendas por Hora</h3>
                
                {!loading && (
                    <div className="chart-stats">
                        <div className="stat-item">
                            <span className="stat-value">{totalSales}</span>
                            <span className="stat-label">Total</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{peakHour.hour}h</span>
                            <span className="stat-label">Pico</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{avgPerHour.toFixed(1)}</span>
                            <span className="stat-label">Média/h</span>
                        </div>
                    </div>
                )}
            </div>
            
            <div className="chart-container">
                {loading ? (
                    <div className="chart-loading">
                        <div className="chart-skeleton">
                            <div className="skeleton-bars">
                                {Array.from({ length: 12 }).map((_, i) => (
                                    <div 
                                        key={i} 
                                        className="skeleton-bar" 
                                        style={{ height: `${Math.random() * 80 + 20}%` }}
                                    ></div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    <canvas
                        ref={chartRef}
                        width="800"
                        height="400"
                        style={{ maxWidth: '100%', height: '300px' }}
                    />
                )}
            </div>
            
            {!loading && totalSales === 0 && (
                <div className="chart-empty">
                    <div className="empty-icon">📊</div>
                    <p>Nenhuma venda encontrada para este período</p>
                    <small>Tente selecionar um período diferente</small>
                </div>
            )}
            
            {!loading && totalSales > 0 && (
                <div className="chart-insights">
                    <p>
                        <strong>Horário de pico:</strong> {peakHour.hour}:00 com {peakHour.count} vendas
                    </p>
                    {period?.days && (
                        <p>
                            <strong>Média diária:</strong> {(totalSales / period.days).toFixed(1)} vendas/dia
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

export default SalesChart;