import React, { useState } from 'react';
import './produto.css'; // Importa o CSS para estilização

/**
 * Componente principal que renderiza a lista de produtos do cardápio.
 * @param {object} props
 * @param {Array} props.produtosData - A lista de produtos vinda do Django.
 */
const CardapioApp = ({ produtosData }) => {
    const [selectedProduto, setSelectedProduto] = useState(null);

    const handleCardClick = (produto) => {
        setSelectedProduto(produto);
    };

    const handleCloseModal = () => {
        setSelectedProduto(null);
    };

    if (!produtosData || produtosData.length === 0) {
        return <p>Nenhum produto disponível no momento. Volte mais tarde!</p>;
    }

    return (
        <>
            <div className="product-container">
                <div className="product-grid">
                    {produtosData.map(produto => (
                        <div key={produto.id} className="product-card" onClick={() => handleCardClick(produto)}>
                            <img src={produto.image_url || 'https://placehold.co/600x400?text=Produto'} alt={produto.name} />
                            <h2>{produto.name}</h2>
                            <p className="price">R$ {produto.price}</p>
                            <button onClick={(e) => { e.stopPropagation(); /* Adicionar lógica do carrinho aqui */ }}>
                                Adicionar ao Carrinho
                            </button>
                        </div>
                    ))}
                </div>
            </div>

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
                                <p className="dialog-description">{selectedProduto.description || "Este produto não possui uma descrição detalhada."}</p>
                                {/* Aqui você pode adicionar mais informações relevantes que vierem do backend */}
                                <p className="dialog-price">R$ {selectedProduto.price}</p>
                            </div>
                        </div>
                        <div className="dialog-actions">
                            <button className="dialog-add-to-cart-button">
                                Adicionar ao Carrinho
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default CardapioApp;
