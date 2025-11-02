
import React, { useState, useEffect } from 'react';
import AdicionarCarrinhoButton from '../components/AdicionarCarrinhoButton';
import CarrinhoIndicador from '@pedido/client/components/CarrinhoIndicador';
import { CarrinhoProvider } from '@pedido/shared/hooks/useCarrinho';
import './produto.css';

// Filtra os produtos para mostrar apenas os disponíveis
const getAvailableProducts = (allProducts) => {
    return allProducts.filter(p => p.available);
};

const ProdutoApp = () => {
    const [produtos, setProdutos] = useState([]);
    const [csrfToken, setCsrfToken] = useState('');

    useEffect(() => {
        // Carrega produtos
        const produtosDataElement = document.getElementById('produtos-data');
        if (produtosDataElement) {
            const produtosData = JSON.parse(produtosDataElement.textContent);
            setProdutos(getAvailableProducts(produtosData));
        }

        // Obtém CSRF token
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            setCsrfToken(tokenElement.value);
        }
    }, []);

    const handleAdicionadoAoCarrinho = (resultado) => {
        if (resultado.success) {
            console.log('Produto adicionado com sucesso:', resultado);
            // Aqui poderia mostrar uma notificação ou atualizar algum contador
        }
    };

    const handleErroCarrinho = (erro) => {
        console.error('Erro ao adicionar ao carrinho:', erro);
        // Aqui poderia mostrar uma mensagem de erro para o usuário
        alert(erro.error || 'Erro ao adicionar produto ao carrinho');
    };

    const handleViewCarrinho = (pedidoAtivo) => {
        // Redirecionar para página de checkout
        window.location.href = '/pedidos/checkout/';
    };

    return (
        <CarrinhoProvider csrfToken={csrfToken}>
            <div className="product-container">
                {/* DEBUG: Sempre mostrar esta caixa para verificar se o React está funcionando */}
                <div style={{
                    position: 'fixed',
                    top: '20px',
                    right: '20px',
                    background: 'lime',
                    padding: '10px',
                    border: '2px solid green',
                    borderRadius: '5px',
                    zIndex: 9999
                }}>
                    <p>✅ ProdutoApp Carregado!</p>
                    <p>Produtos: {produtos.length}</p>
                    <p>CSRF: {csrfToken ? '✓' : '✗'}</p>
                </div>
                
                <h1>Nossos Produtos</h1>
                {produtos.length > 0 ? (
                    <div className="product-grid">
                        {produtos.map(produto => (
                            <div key={produto.id} className="product-card">
                                <div className="product-image">
                                    <img 
                                        src={produto.image || 'https://placehold.co/600x400?text=Produto'} 
                                        alt={produto.name} 
                                    />
                                </div>
                                <div className="product-info">
                                    <h2 className="product-name">{produto.name}</h2>
                                    <p className="product-description">{produto.description}</p>
                                    <div className="product-price">R$ {produto.price}</div>
                                </div>
                                <div className="product-actions">
                                    <AdicionarCarrinhoButton
                                        produto={produto}
                                        onSuccess={handleAdicionadoAoCarrinho}
                                        onError={handleErroCarrinho}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="no-products">Nenhum produto disponível no momento. Volte mais tarde!</p>
                )}
                
                {/* Indicador do carrinho fixo */}
                <CarrinhoIndicador 
                    onViewCarrinho={handleViewCarrinho}
                    showTotal={true}
                    showItemCount={true}
                />
            </div>
        </CarrinhoProvider>
    );
};

export default ProdutoApp;
