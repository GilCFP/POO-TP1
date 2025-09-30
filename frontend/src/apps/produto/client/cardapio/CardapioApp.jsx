import React, { useState, useEffect } from 'react';
import AdicionarCarrinhoButton from '../components/AdicionarCarrinhoButton';
import CarrinhoIndicador from '@pedido/client/components/CarrinhoIndicador';
import { CarrinhoProvider } from '@pedido/shared/hooks/useCarrinho';
import './produto.css'; // Importa o CSS para estilização

/**
 * Componente principal que renderiza a lista de produtos do cardápio.
 * @param {object} props
 * @param {Array} props.produtosData - A lista de produtos vinda do Django.
 */
const CardapioApp = ({ produtosData }) => {
    const [selectedProduto, setSelectedProduto] = useState(null);
    const [csrfToken, setCsrfToken] = useState('');

    // Obtém CSRF token na inicialização
    useEffect(() => {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            setCsrfToken(tokenElement.value);
        }
    }, []);

    const handleCardClick = (produto) => {
        setSelectedProduto(produto);
    };

    const handleCloseModal = () => {
        setSelectedProduto(null);
    };

    const handleAdicionadoAoCarrinho = (resultado) => {
        if (resultado.success) {
            console.log('Produto adicionado com sucesso:', resultado);
            // Fechar modal após adicionar se estiver aberto
            if (selectedProduto) {
                setSelectedProduto(null);
            }
        }
    };

    const handleErroCarrinho = (erro) => {
        console.error('Erro ao adicionar ao carrinho:', erro);
        alert(erro.error || 'Erro ao adicionar produto ao carrinho');
    };

    const handleViewCarrinho = (pedidoAtivo) => {
        // Redirecionar para página de checkout
        window.location.href = '/pedido/checkout/';
    };

    if (!produtosData || produtosData.length === 0) {
        return (
            <CarrinhoProvider csrfToken={csrfToken}>
                <div className="product-container">
                    <p className="no-products">Nenhum produto disponível no momento. Volte mais tarde!</p>
                </div>
            </CarrinhoProvider>
        );
    }

    return (
        <CarrinhoProvider csrfToken={csrfToken}>
            <div className="product-container">
                <div className="product-grid">
                    {produtosData.map(produto => (
                        <div key={produto.id} className="product-card">
                            <div className="product-image" onClick={() => handleCardClick(produto)}>
                                <img 
                                    src={produto.image_url || 'https://placehold.co/600x400?text=Produto'} 
                                    alt={produto.name} 
                                />
                            </div>
                            <div className="product-info" onClick={() => handleCardClick(produto)}>
                                <h2 className="product-name">{produto.name}</h2>
                                <p className="product-price">R$ {produto.price}</p>
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
            </div>

            {/* Indicador do carrinho fixo */}
            <CarrinhoIndicador 
                onViewCarrinho={handleViewCarrinho}
                showTotal={true}
                showItemCount={true}
            />

            {/* Modal de detalhes do produto */}
            {selectedProduto && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
                        <div className="dialog-header">
                            <h2 className="dialog-title">{selectedProduto.name}</h2>
                            <button className="dialog-close-button" onClick={handleCloseModal} aria-label="Fechar">
                                &times;
                            </button>
                        </div>
                        <div className="dialog-body">
                            <div className="dialog-image-container">
                                <img 
                                    src={selectedProduto.image_url || 'https://placehold.co/600x400?text=Produto'} 
                                    alt={selectedProduto.name} 
                                    className="dialog-image"
                                />
                            </div>
                            <div className="dialog-details">
                                <p className="dialog-description">
                                    {selectedProduto.description || "Este produto não possui uma descrição detalhada."}
                                </p>
                                <p className="dialog-price">R$ {selectedProduto.price}</p>
                            </div>
                        </div>
                        <div className="dialog-actions">
                            <AdicionarCarrinhoButton
                                produto={selectedProduto}
                                onSuccess={handleAdicionadoAoCarrinho}
                                onError={handleErroCarrinho}
                                className="dialog-add-button"
                            />
                        </div>
                    </div>
                </div>
            )}
        </CarrinhoProvider>
    );
};

export default CardapioApp;
