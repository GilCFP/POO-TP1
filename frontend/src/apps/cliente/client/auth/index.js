import React from 'react';
import { createRoot } from 'react-dom/client';
import LoginApp from './LoginApp.jsx';

// Debug: Log quando o script é carregado
console.log('Auth bundle loaded');

// Verificar se React e ReactDOM estão disponíveis
console.log('React available:', typeof React !== 'undefined');
console.log('createRoot available:', typeof createRoot !== 'undefined');

// Função para tentar renderizar
function tryRender() {
  console.log('Trying to render...');
  const container = document.getElementById('login-root');
  console.log('Container found:', container);
  
  if (container) {
    try {
      console.log('Creating React root...');
      const root = createRoot(container);
      console.log('Rendering LoginApp...');
      root.render(<LoginApp />);
      console.log('React app rendered successfully');
    } catch (error) {
      console.error('Error rendering React app:', error);
    }
  } else {
    console.error('Container login-root not found!');
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
  console.log('Fallback timeout triggered');
  tryRender();
}, 1000);