import React from 'react';
import { createRoot } from 'react-dom/client';
import CheckoutApp from './CheckoutApp';
import '@shared/styles/client.css';
import './checkout.css';

/**
 * Entry point para o app de checkout do cliente
 * Conecta com o template Django checkout.html
 */
document.addEventListener('DOMContentLoaded', () => {
  // Verifica se os elementos necessários existem
  const container = document.getElementById('checkout-root');
  const dataElement = document.getElementById('checkout-data');
  console.log('Elemento de dados do checkout:', dataElement);
  const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');

  if (!container) {
    console.error('Container #checkout-root não encontrado');
    return;
  }

  if (!dataElement) {
    console.error('Elemento #checkout-data não encontrado');
    return;
  }

  if (!csrfElement) {
    console.error('Token CSRF não encontrado');
    return;
  }

  try {
    // Parse dos dados do Django
    const checkoutData = JSON.parse(dataElement.textContent);
    const csrfToken = csrfElement.value;

    // Criar root do React 18
    const root = createRoot(container);

    // Renderizar aplicação
    root.render(
      <CheckoutApp 
        pedidoData={checkoutData.pedido}
        enderecosData={checkoutData}
        csrfToken={csrfToken}
      />
    );

    console.log('✅ Checkout App inicializado com sucesso');
    
  } catch (error) {
    console.error('❌ Erro ao inicializar Checkout App:', error);
    
    // Fallback: mostrar mensagem de erro
    container.innerHTML = `
      <div class="alert alert-danger">
        <h4>Erro ao carregar checkout</h4>
        <p>Ocorreu um erro ao inicializar a aplicação. Por favor, recarregue a página.</p>
        <button onclick="location.reload()" class="btn btn-primary">Recarregar</button>
      </div>
    `;
  }
});