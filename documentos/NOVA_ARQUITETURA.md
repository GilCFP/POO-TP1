# Sistema de Restaurante - Arquitetura Modular

## Estrutura de Apps por Domínio

### 📱 **Frontend Separado**
- **Frontend Cliente**: Interface para clientes fazerem pedidos
- **Frontend Restaurante**: Dashboard para cozinheiros e balconistas

### 🏗️ **Backend Django - Apps Modulares**

```
fast_food_system/                 # Projeto Django principal
├── config/                       # Configurações do projeto
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py              # Configurações base
│   │   ├── development.py       # Desenvolvimento
│   │   ├── production.py        # Produção
│   │   └── testing.py           # Testes
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                         # Todos os apps modulares
│   ├── __init__.py
│   │
│   ├── core/                     # App central - funcionalidades compartilhadas
│   │   ├── __init__.py
│   │   ├── models.py            # Models abstratos e compartilhados
│   │   ├── utils.py             # Utilitários gerais
│   │   ├── permissions.py       # Permissões customizadas
│   │   ├── exceptions.py        # Exceções customizadas
│   │   └── mixins.py            # Mixins reutilizáveis
│   │
│   ├── produto/                  # App de Produtos
│   │   ├── __init__.py
│   │   ├── models.py            # Produto, Alimento, Bebida, Comida, Combo, RestricaoAlimentar
│   │   ├── admin.py
│   │   ├── services.py          # ProdutoService, AlimentoService
│   │   ├── serializers.py       # Para APIs
│   │   ├── views.py             # ViewSets para API
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   ├── cliente/                  # App de Clientes
│   │   ├── __init__.py
│   │   ├── models.py            # Cliente
│   │   ├── admin.py
│   │   ├── services.py          # ClienteService
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   ├── pedido/                   # App de Pedidos
│   │   ├── __init__.py
│   │   ├── models.py            # Pedido, ItemPedido, StatusPedido
│   │   ├── admin.py
│   │   ├── services.py          # PedidoService, PagamentoService
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   ├── signals.py           # Sinais para notificações
│   │   └── migrations/
│   │
│   ├── restaurante/              # App de Restaurante (Cozinha, Caixa)
│   │   ├── __init__.py
│   │   ├── models.py            # Restaurante, Cozinha, Caixa
│   │   ├── admin.py
│   │   ├── services.py          # RestauranteService, CozinhaService
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   ├── api/                      # App de APIs centralizadas
│   │   ├── __init__.py
│   │   ├── v1/                  # Versão 1 da API
│   │   │   ├── __init__.py
│   │   │   ├── urls.py          # URLs da API v1
│   │   │   ├── cliente_urls.py  # URLs específicas do cliente
│   │   │   └── restaurante_urls.py # URLs específicas do restaurante
│   │   ├── permissions.py       # Permissões específicas da API
│   │   ├── authentication.py   # Autenticação customizada
│   │   └── utils.py
│   │
│   └── websocket/               # App para WebSockets (tempo real)
│       ├── __init__.py
│       ├── consumers.py         # Consumidores WebSocket
│       ├── routing.py           # Roteamento WebSocket
│       └── utils.py
│
├── frontend/                     # Frontends separados
│   ├── cliente/                 # Frontend do Cliente
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/        # Chamadas para API
│   │   │   ├── utils/
│   │   │   └── App.jsx
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── restaurante/             # Frontend do Restaurante
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   │   ├── Kanban/      # Componente de arrastar e soltar
│       │   │   ├── PedidoCard/
│       │   │   └── Dashboard/
│       │   ├── pages/
│       │   │   ├── Cozinha.jsx  # Dashboard da cozinha
│       │   │   ├── Caixa.jsx    # Dashboard do caixa
│       │   │   └── Gerencia.jsx # Dashboard de gerência
│       │   ├── services/
│       │   ├── utils/
│       │   └── App.jsx
│       ├── package.json
│       └── vite.config.js
│
├── static/                       # Arquivos estáticos
├── media/                        # Upload de arquivos
├── requirements/                 # Dependências separadas por ambiente
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
├── docker/                       # Configurações Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── scripts/                      # Scripts de automação
├── docs/                         # Documentação
├── manage.py
└── README.md
```

## 🎯 **Separação de Responsabilidades por App**

### **1. Core App**
```python
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class BaseService:
    """Classe base para todos os services"""
    pass
```

### **2. Produto App**
```python
# apps/produto/models.py
class Produto(TimeStampedModel):
    # Apenas funcionalidades relacionadas a produtos
    pass

class Alimento(Produto):
    # Funcionalidades específicas de alimentos
    pass
```

### **3. Cliente App**
```python
# apps/cliente/models.py
class Cliente(TimeStampedModel):
    # Apenas funcionalidades relacionadas a clientes
    pass

# apps/cliente/services.py
class ClienteService:
    @staticmethod
    def criar_cliente(dados):
        # Lógica específica de cliente
        pass
```

### **4. Pedido App**
```python
# apps/pedido/models.py
class Pedido(TimeStampedModel):
    cliente = models.ForeignKey('cliente.Cliente', on_delete=models.CASCADE)
    # Lógica de pedidos
    pass

# apps/pedido/services.py
class PedidoService:
    @staticmethod
    def criar_pedido(cliente_id):
        # Lógica específica de pedidos
        pass
```

### **5. Restaurante App**
```python
# apps/restaurante/models.py
class Cozinha(TimeStampedModel):
    # Lógica da cozinha
    pass

class Caixa(TimeStampedModel):
    # Lógica do caixa
    pass
```

## 🌐 **APIs Separadas por Contexto**

### **API do Cliente**
```python
# apps/api/v1/cliente_urls.py
urlpatterns = [
    path('menu/', MenuView.as_view()),
    path('pedidos/', PedidoClienteView.as_view()),
    path('pedidos/<int:id>/status/', StatusPedidoView.as_view()),
]
```

### **API do Restaurante**
```python
# apps/api/v1/restaurante_urls.py
urlpatterns = [
    path('cozinha/pedidos/', PedidosCozinhaView.as_view()),
    path('cozinha/pedidos/<int:id>/mover/', MoverPedidoView.as_view()),
    path('caixa/vendas/', VendasView.as_view()),
]
```

## 🎨 **Frontend Moderno com React**

### **Frontend do Restaurante - Kanban**
```jsx
// frontend/restaurante/src/components/Kanban/KanbanBoard.jsx
import { DndProvider } from 'react-dnd'
import PedidoCard from './PedidoCard'

export default function KanbanBoard() {
  const [pedidos, setPedidos] = useState({
    fila: [],
    preparando: [],
    pronto: []
  })

  const moverPedido = (pedidoId, novoStatus) => {
    // API call para mover pedido
    api.post(`/api/v1/restaurante/cozinha/pedidos/${pedidoId}/mover/`, {
      status: novoStatus
    })
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="kanban-board">
        <Column title="Fila" pedidos={pedidos.fila} />
        <Column title="Preparando" pedidos={pedidos.preparando} />
        <Column title="Pronto" pedidos={pedidos.pronto} />
      </div>
    </DndProvider>
  )
}
```

## 🔄 **WebSocket para Tempo Real**
```python
# apps/websocket/consumers.py
class CozinhaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("cozinha", self.channel_name)
        await self.accept()

    async def pedido_update(self, event):
        # Enviar atualização em tempo real para frontend
        await self.send(text_data=json.dumps(event))
```

## 📱 **Vantagens desta Estrutura**

### ✅ **Modularidade**
- Cada app tem responsabilidade única
- Facilita manutenção e testes
- Permite desenvolvimento paralelo por equipes

### ✅ **Escalabilidade**
- Apps podem virar microserviços no futuro
- Frontend e backend totalmente desacoplados
- Suporte a múltiplos frontends

### ✅ **Experiência do Usuário**
- Interface moderna com React
- Drag & drop para cozinheiros
- Atualizações em tempo real via WebSocket
- Mobile-first design

### ✅ **Separação de Contextos**
- API específica para clientes
- API específica para restaurante
- Permissões granulares
- Autenticação separada

Quer que eu implemente essa nova estrutura? Posso migrar o código atual para essa arquitetura modular!