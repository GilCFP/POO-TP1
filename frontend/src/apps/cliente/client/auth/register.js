import React from 'react';
import { createRoot } from 'react-dom/client';
import RegisterApp from './RegisterApp.jsx';

// Debug: Log quando o script é carregado
console.log('Register bundle loaded');

// Verificar se React e ReactDOM estão disponíveis
console.log('React available:', typeof React !== 'undefined');
console.log('createRoot available:', typeof createRoot !== 'undefined');

// Função para tentar renderizar
function tryRender() {
  console.log('Trying to render register...');
  const container = document.getElementById('register-root');
  console.log('Container found:', container);
  
  if (container) {
    try {
      console.log('Creating React root for register...');
      const root = createRoot(container);
      console.log('Rendering RegisterApp...');
      root.render(<RegisterApp />);
      console.log('React register app rendered successfully');
    } catch (error) {
      console.error('Error rendering React register app:', error);
    }
  } else {
    console.error('Container register-root not found!');
    // List all elements with IDs for debugging
    const elementsWithIds = document.querySelectorAll('[id]');
    console.log('Elements with IDs:', Array.from(elementsWithIds).map(el => el.id));
  }
}

// Múltiplas estratégias para garantir que o DOM está pronto
if (document.readyState === 'loading') {
  console.log('DOM is loading, waiting for DOMContentLoaded...');
  document.addEventListener('DOMContentLoaded', tryRender);
} else {
  console.log('DOM is ready, rendering immediately...');
  tryRender();
}

// Fallback adicional
setTimeout(() => {
  console.log('Fallback timeout triggered for register');
  tryRender();
}, 1000);