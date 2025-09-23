# Frontend Structure - POO TP1

Este diretório contém toda a estrutura frontend moderna do projeto, organizada por **apps** e **escopos** (client/admin).

## 📁 Estrutura de Pastas

```
frontend/
├── src/
│   ├── apps/                    # Apps Django
│   │   ├── pedido/             # App de pedidos
│   │   │   ├── client/         # Interface do cliente
│   │   │   │   ├── checkout/   # Checkout do pedido
│   │   │   │   ├── status/     # Status do pedido
│   │   │   │   ├── historico/  # Histórico de pedidos
│   │   │   │   └── components/ # Componentes específicos
│   │   │   ├── admin/          # Interface do admin
│   │   │   │   ├── dashboard/  # Dashboard de pedidos
│   │   │   │   ├── gerenciar/  # Gerenciar pedidos
│   │   │   │   └── components/ # Componentes admin
│   │   │   └── shared/         # Compartilhado do app
│   │   │       └── hooks/      # Hooks personalizados
│   │   │
│   │   ├── produto/            # App de produtos
│   │   │   ├── client/         # Interface do cliente
│   │   │   │   ├── cardapio/   # Cardápio
│   │   │   │   ├── detalhes/   # Detalhes do produto
│   │   │   │   └── components/ # Componentes específicos
│   │   │   ├── admin/          # Interface do admin
│   │   │   │   ├── crud/       # CRUD de produtos
│   │   │   │   ├── estoque/    # Gestão de estoque
│   │   │   │   └── components/ # Componentes admin
│   │   │   └── shared/         # Compartilhado do app
│   │   │
│   │   ├── cliente/            # App de clientes
│   │   │   ├── client/         # Interface do cliente
│   │   │   │   ├── perfil/     # Perfil do cliente
│   │   │   │   ├── auth/       # Autenticação
│   │   │   │   └── components/ # Componentes específicos
│   │   │   ├── admin/          # Interface do admin
│   │   │   │   ├── gerenciar/  # Gerenciar clientes
│   │   │   │   └── components/ # Componentes admin
│   │   │   └── shared/         # Compartilhado do app
│   │   │
│   │   └── restaurante/        # App do restaurante
│   │       ├── admin/          # Interface do admin
│   │       │   ├── dashboard/  # Dashboard geral
│   │       │   ├── configuracoes/ # Configurações
│   │       │   └── components/ # Componentes admin
│   │       └── shared/         # Compartilhado do app
│   │
│   └── shared/                 # Recursos globais
│       ├── components/         # Componentes reutilizáveis
│       │   ├── client/         # Componentes para cliente
│       │   ├── admin/          # Componentes para admin
│       │   └── common/         # Componentes comuns
│       ├── hooks/              # Hooks personalizados globais
│       ├── services/           # Serviços (API, etc.)
│       ├── utils/              # Utilitários
│       └── styles/             # Estilos globais
│
├── package.json                # Dependências Node.js
├── webpack.config.js           # Configuração do Webpack
├── babel.config.js             # Configuração do Babel
└── README.md                   # Este arquivo
```

## 🎯 Conceitos da Arquitetura

### 1. **Separação por Escopo**
- **Client**: Interface para o usuário final (clientes do restaurante)
- **Admin**: Interface para administração (funcionários, gerentes)
- **Shared**: Componentes e recursos compartilhados entre escopos

### 2. **Organização por App**
Cada app Django tem sua própria pasta no frontend:
- `pedido/` - Gestão de pedidos
- `produto/` - Gestão de produtos/cardápio
- `cliente/` - Gestão de clientes
- `restaurante/` - Configurações gerais

### 3. **Build System**
- **Webpack** compila cada página como um bundle separado
- **Babel** transpila JSX e ES6+ para compatibilidade
- **CSS Modules** para estilos isolados por componente

## 🚀 Como Usar

### Instalação
```bash
cd frontend/
npm install
```

### Desenvolvimento
```bash
# Watch mode (recompila automaticamente)
npm run dev

# Build de desenvolvimento
npm run build:dev

# Build de produção
npm run build

# Servidor de desenvolvimento com hot reload
npm run serve
```

### Integração com Django

#### 1. No Template Django
```html
<!-- apps/pedido/templates/client/checkout.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<!-- Dados para o React -->
{{ checkout_data|json_script:"checkout-data" }}
<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">

<!-- Container do React -->
<div id="checkout-root"></div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'pedido/client/checkout.bundle.js' %}"></script>
{% endblock %}
```

#### 2. Na View Django
```python
# apps/pedido/views.py
def checkout_view(request):
    pedido = get_object_or_404(Pedido, usuario=request.user)
    
    checkout_data = {
        'pedido': {
            'id': pedido.id,
            'items': [...],
            'total': float(pedido.total_price)
        }
    }
    
    return render(request, 'client/checkout.html', {
        'checkout_data': checkout_data
    })
```

## 📦 Bundles Gerados

O Webpack gera os seguintes bundles:

```
apps/
├── pedido/
│   ├── client/
│   │   ├── checkout.bundle.js
│   │   ├── status.bundle.js
│   │   └── historico.bundle.js
│   └── admin/
│       ├── dashboard.bundle.js
│       └── gerenciar.bundle.js
├── produto/
│   ├── client/
│   │   ├── cardapio.bundle.js
│   │   └── detalhes.bundle.js
│   └── admin/
│       ├── crud.bundle.js
│       └── estoque.bundle.js
└── shared/
    ├── client/
    │   └── vendor.bundle.js
    └── admin/
        └── vendor.bundle.js
```

## 🛠️ Tecnologias

- **React 18** - Biblioteca principal
- **Webpack 5** - Bundler
- **Babel** - Transpilador
- **CSS Modules** - Estilos isolados
- **clsx** - Conditional classes

## 📝 Convenções

### Nomenclatura de Arquivos
- **Componentes**: `PascalCase.jsx` (ex: `CheckoutApp.jsx`)
- **Hooks**: `camelCase.js` com prefixo `use` (ex: `useCheckout.js`)
- **Utilitários**: `camelCase.js` (ex: `formatters.js`)
- **Estilos**: `kebab-case.css` (ex: `checkout.css`)

### Estrutura de Componentes
```jsx
// apps/pedido/client/checkout/CheckoutApp.jsx
import React from 'react';
import { useCheckout } from '@pedido/shared/hooks/useCheckout';
import OrderSummary from '../components/OrderSummary';
import './checkout.css';

const CheckoutApp = ({ pedidoData, csrfToken }) => {
  // Lógica do componente
  return (
    <div className="checkout-container">
      {/* JSX */}
    </div>
  );
};

export default CheckoutApp;
```

### Aliases de Import
```jsx
import Component from '@components/common/Component';
import { useApi } from '@shared/hooks/useApi';
import { apiService } from '@services/api';
import CheckoutApp from '@pedido/client/checkout/CheckoutApp';
```

## 🔄 Fluxo de Desenvolvimento

1. **Desenvolvimento**: Editar arquivos em `src/`
2. **Build**: Webpack compila para `apps/*/static/*/js/`
3. **Django**: Serve os bundles nos templates
4. **Browser**: Executa o React integrado com Django

## 🎨 Customização

### Temas por Escopo
- **Client**: Cores vibrantes, UX amigável
- **Admin**: Interface profissional, foco em produtividade

### Responsividade
Todos os componentes são mobile-first e responsivos.

### Acessibilidade
- Suporte a teclado
- ARIA labels
- Contrast adequado
- Focus visível

## 📈 Performance

- **Code splitting** por página
- **Lazy loading** de componentes
- **Tree shaking** para bundles menores
- **CSS minificado** em produção
- **Source maps** para debug

Esta estrutura permite desenvolvimento moderno mantendo integração total com Django! 🚀