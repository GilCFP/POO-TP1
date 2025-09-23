import React from 'react';
import { createRoot } from 'react-dom/client';
import HistoricoApp from './HistoricoApp';

// Função para inicializar a aplicação
function initHistoricoApp() {
  const container = document.getElementById('historico-root');
  if (!container) {
    console.error('Container #historico-root não encontrado');
    return;
  }

  // Obter dados do Django
  const historicoDataElement = document.getElementById('historico-data');
  const historicoData = historicoDataElement ? JSON.parse(historicoDataElement.textContent) : {};
  
  // Obter CSRF token
  const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

  // Criar root e renderizar aplicação
  const root = createRoot(container);
  root.render(
    <HistoricoApp 
      historicoData={historicoData}
      csrfToken={csrfToken}
    />
  );
}

// Inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initHistoricoApp);
} else {
  initHistoricoApp();
}