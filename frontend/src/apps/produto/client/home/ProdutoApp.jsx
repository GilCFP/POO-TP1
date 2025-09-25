
import React, { useState, useEffect } from 'react';
import './produto.css';

// Filtra os produtos para mostrar apenas os disponíveis
const getAvailableProducts = (allProducts) => {
    return allProducts.filter(p => p.available);
};

const ProdutoApp = () => {
    const [produtos, setProdutos] = useState([]);

    useEffect(() => {
        const produtosDataElement = document.getElementById('produtos-data');
        if (produtosDataElement) {
            const produtosData = JSON.parse(produtosDataElement.textContent);
            setProdutos(getAvailableProducts(produtosData));
        }
    }, []);

    // Não precisamos mais do estado de 'loading', pois os dados já estão na página.
    // O componente renderiza imediatamente com os dados ou com a mensagem de "nenhum produto".

    return (
        <div className="product-container">
            <h1>Nossos Produtos</h1>
            {produtos.length > 0 ? (
                <div className="product-grid">
                    {produtos.map(produto => (
                        <div key={produto.id} className="product-card">
                            <img src={produto.image || 'https://placehold.co/600x400?text=Produto'} alt={produto.name} />
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

export default ProdutoApp;
