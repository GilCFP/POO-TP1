/**
 * TopProducts - Componente para exibir produtos mais vendidos
 */

import React, { useState } from 'react';

const TopProducts = ({ products, loading, period }) => {
    const [sortBy, setSortBy] = useState('quantity'); // 'quantity' ou 'revenue'
    
    // Fallback para dados vazios
    const defaultProducts = [];
    const productList = products?.top_products || defaultProducts;
    
    /**
     * Ordena produtos baseado no critério selecionado
     */
    const getSortedProducts = () => {
        if (!productList || productList.length === 0) return [];
        
        return [...productList].sort((a, b) => {
            if (sortBy === 'quantity') {
                return b.total_sold - a.total_sold;
            }
            // Por enquanto só temos quantidade, mas pode ser expandido para receita
            return b.total_sold - a.total_sold;
        });
    };
    
    /**
     * Calcula percentual de participação
     */
    const calculatePercentage = (value, total) => {
        if (total === 0) return 0;
        return ((value / total) * 100).toFixed(1);
    };
    
    const sortedProducts = getSortedProducts();
    const totalQuantity = sortedProducts.reduce((sum, product) => sum + product.total_sold, 0);
    
    /**
     * Componente de item de produto
     */
    const ProductItem = ({ product, index, total }) => {
        const percentage = calculatePercentage(product.total_sold, total);
        const barWidth = total > 0 ? (product.total_sold / sortedProducts[0]?.total_sold * 100) : 0;
        
        return (
            <div className="product-item">
                <div className="product-rank">#{index + 1}</div>
                
                <div className="product-info">
                    <div className="product-name" title={product.produto_nome}>
                        {product.produto_nome}
                    </div>
                    
                    <div className="product-metrics">
                        <span className="product-quantity">
                            {product.total_sold} vendidos
                        </span>
                        <span className="product-percentage">
                            {percentage}% do total
                        </span>
                    </div>
                    
                    <div className="product-bar">
                        <div 
                            className="product-bar-fill" 
                            style={{ width: `${barWidth}%` }}
                        ></div>
                    </div>
                </div>
            </div>
        );
    };
    
    /**
     * Componente de item de loading
     */
    const ProductItemSkeleton = () => (
        <div className="product-item skeleton">
            <div className="product-rank skeleton-text"></div>
            <div className="product-info">
                <div className="product-name skeleton-text"></div>
                <div className="product-metrics">
                    <div className="skeleton-text short"></div>
                    <div className="skeleton-text short"></div>
                </div>
                <div className="product-bar skeleton-bar"></div>
            </div>
        </div>
    );
    
    return (
        <div className="top-products">
            <div className="products-header">
                <h3>🏆 Produtos Mais Vendidos</h3>
                
                {!loading && sortedProducts.length > 0 && (
                    <div className="products-controls">
                        <select 
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                            className="sort-select"
                        >
                            <option value="quantity">Por Quantidade</option>
                            {/* Futuro: <option value="revenue">Por Receita</option> */}
                        </select>
                    </div>
                )}
            </div>
            
            <div className="products-list">
                {loading ? (
                    // Estado de loading
                    Array.from({ length: 5 }).map((_, index) => (
                        <ProductItemSkeleton key={index} />
                    ))
                ) : sortedProducts.length > 0 ? (
                    // Lista de produtos
                    sortedProducts.map((product, index) => (
                        <ProductItem
                            key={`${product.produto_nome}-${index}`}
                            product={product}
                            index={index}
                            total={totalQuantity}
                        />
                    ))
                ) : (
                    // Estado vazio
                    <div className="products-empty">
                        <div className="empty-icon">🛍️</div>
                        <h4>Nenhum produto encontrado</h4>
                        <p>Não há dados de produtos vendidos para o período selecionado.</p>
                        <small>Verifique se há pedidos finalizados no período.</small>
                    </div>
                )}
            </div>
            
            {/* Resumo */}
            {!loading && sortedProducts.length > 0 && (
                <div className="products-summary">
                    <div className="summary-stats">
                        <div className="summary-item">
                            <strong>Total de itens vendidos:</strong> {totalQuantity.toLocaleString('pt-BR')}
                        </div>
                        
                        <div className="summary-item">
                            <strong>Produtos únicos:</strong> {sortedProducts.length}
                        </div>
                        
                        {period?.days && (
                            <div className="summary-item">
                                <strong>Média por dia:</strong> {(totalQuantity / period.days).toFixed(1)} itens
                            </div>
                        )}
                    </div>
                    
                    {/* Top 3 insights */}
                    {sortedProducts.length >= 3 && (
                        <div className="top-insights">
                            <p>
                                <strong>Top 3 produtos</strong> representam{' '}
                                {calculatePercentage(
                                    sortedProducts.slice(0, 3).reduce((sum, p) => sum + p.total_sold, 0),
                                    totalQuantity
                                )}% das vendas
                            </p>
                        </div>
                    )}
                </div>
            )}
            
            {/* Link para ver mais (futuro) */}
            {!loading && sortedProducts.length >= 5 && (
                <div className="products-footer">
                    <button className="btn btn-outline btn-sm" disabled>
                        Ver todos os produtos
                    </button>
                </div>
            )}
        </div>
    );
};

export default TopProducts;