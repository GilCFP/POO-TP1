import React from 'react';
import { createRoot } from 'react-dom/client';
import StatusApp from './StatusApp';

// Função para inicializar a aplicação
function initStatusApp() {
  const container = document.getElementById('status-root');
  if (!container) {
    console.error('Container #status-root não encontrado');
    return;
  }

  // Obter dados do Django
  const statusDataElement = document.getElementById('status-data');
  const statusData = statusDataElement ? JSON.parse(statusDataElement.textContent) : {};
  
  // Obter CSRF token
  const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

  // Criar root e renderizar aplicação
  const root = createRoot(container);
  root.render(
    <StatusApp 
      statusData={statusData}
      csrfToken={csrfToken}
    />
  );
}

// Inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initStatusApp);
} else {
  initStatusApp();
}