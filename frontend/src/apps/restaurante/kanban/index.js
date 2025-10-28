import React from 'react';
import ReactDOM from 'react-dom/client';
import RestauranteKanban from './components/RestauranteKanban';
import './kanban.css';

/**
 * Inicializa o componente Kanban do Restaurante
 */
function initializeRestauranteKanban() {
    // Aguarda o DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeKanban);
    } else {
        initializeKanban();
    }
}

function initializeKanban() {
    const kanbanRoot = document.getElementById('restaurante-kanban-root');
    
    if (kanbanRoot) {
        // Busca dados iniciais do script tag
        const initialDataScript = document.getElementById('kanban-initial-data');
        let initialData = {};
        
        if (initialDataScript) {
            try {
                initialData = JSON.parse(initialDataScript.textContent);
            } catch (error) {
                console.error('Erro ao parsear dados iniciais do kanban:', error);
            }
        }
        
        // Cria o root do React e renderiza o componente
        const root = ReactDOM.createRoot(kanbanRoot);
        root.render(<RestauranteKanban initialData={initialData} />);
    } else {
        console.warn('Elemento #restaurante-kanban-root não encontrado');
    }
}

// Exporta a função de inicialização para uso global
window.initializeRestauranteKanban = initializeRestauranteKanban;

// Inicializa automaticamente se o script for carregado
initializeRestauranteKanban();

export default RestauranteKanban;