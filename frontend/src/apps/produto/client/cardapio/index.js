import React from 'react';
import { createRoot } from 'react-dom/client';
import CardapioApp from './CardapioApp';

/**
 * Ponto de entrada (entry point) para a aplicação React do Cardápio.
 * Este script é responsável por ler os dados injetados pelo Django
 * e renderizar o componente principal do React.
 */
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('cardapio-root');
    const dataElement = document.getElementById('produtos-data');

    if (!container) {
        console.error('Container React #cardapio-root não foi encontrado no DOM.');
        return;
    }

    if (!dataElement) {
        console.error('Elemento de dados #produtos-data não foi encontrado.');
        container.innerHTML = '<p style="color: red;">Erro: Não foi possível carregar os dados dos produtos.</p>';
        return;
    }

    try {
        // 1. Lê os dados do script JSON injetado pelo Django.
        const produtosData = JSON.parse(dataElement.textContent);

        // 2. Cria a raiz da aplicação React no container.
        const root = createRoot(container);

        // 3. Renderiza o componente principal, passando os dados como props.
        root.render(<CardapioApp produtosData={produtosData} />);

        console.log('✅ Aplicação de Cardápio React inicializada com sucesso!');

    } catch (error) {
        console.error('❌ Falha ao inicializar a aplicação de Cardápio React:', error);
        container.innerHTML = '<p style="color: red;">Ocorreu um erro ao carregar o cardápio. Tente recarregar a página.</p>';
    }
});
