import React from 'react';
import './produto.css'; // Importa o CSS para estilização

/**
 * Componente principal que renderiza a lista de produtos do cardápio.
 * @param {object} props
 * @param {Array} props.produtosData - A lista de produtos vinda do Django.
 */
const CardapioApp = ({ produtosData }) => {
    if (!produtosData || produtosData.length === 0) {
        return <p>Nenhum produto disponível no momento. Volte mais tarde!</p>;
    }

    return (
        <div className="product-container">
            {/* O título já está no template do Django, então não precisamos repetir aqui. */}
            {produtosData.length > 0 ? (
                <div className="product-grid">
                    {produtosData.map(produto => (
                        <div key={produto.id} className="product-card">
                            <img src={produto.image_url || 'https://placehold.co/600x400?text=Produto'} alt={produto.name} />
                            <h2>{produto.name}</h2>
                            <p>{produto.description}</p>
                            <p className="price">R$ {produto.price}</p>
                            <button>Adicionar ao Carrinho</button>
                        </div>
                    ))}
                </div>
            ) : (
                <p>Nenhum produto disponível no momento. Volte mais tarde!</p>
            )}
        </div>
    );
};

export default CardapioApp;
