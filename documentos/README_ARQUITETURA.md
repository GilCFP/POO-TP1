# Sistema de Restaurante - Implementação com Django

Este projeto implementa um sistema completo de restaurante usando Django, seguindo as melhores práticas de arquitetura e organização de código.

## Estrutura de Diretórios e Responsabilidades

### 📁 **Models** (`produto/models.py`)
- **Responsabilidade**: Definição das entidades e regras de dados
- **Contém**: Classes Django que representam as tabelas do banco de dados
- **Exemplos**: `Produto`, `Cliente`, `Pedido`, `Restaurante`, `Cozinha`

### 📁 **Services** (`produto/services/`)
- **Responsabilidade**: Lógica de negócio e regras específicas do domínio
- **Contém**: Classes que implementam operações complexas e validações
- **Exemplos**: `RestauranteService`, `PedidoService`, `PagamentoService`
- **Vantagens**: Reutilização de código, testabilidade, separação de responsabilidades

### 📁 **Views** (`produto/views.py`)
- **Responsabilidade**: Controllers que recebem requisições HTTP e retornam respostas
- **Contém**: Funções que processam requests, chamam services e renderizam templates
- **Exemplos**: `criar_cliente`, `processar_pagamento`, `gerenciar_cozinha`

### 📁 **Utils** (`produto/utils/`)
- **Responsabilidade**: Utilitários, validadores e funções auxiliares
- **Contém**: Funções reutilizáveis que não são específicas de uma entidade
- **Exemplos**: Validadores, formatadores, calculadoras

### 📁 **Templates** (`produto/templates/`)
- **Responsabilidade**: Apresentação visual e interface do usuário
- **Contém**: Arquivos HTML que definem como os dados são apresentados
- **Estrutura**: Organizado por funcionalidade

### 📁 **Admin** (`produto/admin.py`)
- **Responsabilidade**: Interface administrativa do Django
- **Contém**: Configurações para gerenciar dados via painel admin

### 📁 **URLs** (`produto/urls.py`)
- **Responsabilidade**: Roteamento de URLs para views
- **Contém**: Mapeamento entre URLs e functions/classes de view

## Como Implementar Regras de Negócio

### 1. **Identifique a Regra de Negócio**
Exemplo: "Um cliente não pode pedir um produto que conflite com suas restrições alimentares"

### 2. **Crie um Service**
```python
# produto/services/business_services.py
class PedidoService:
    @staticmethod
    def adicionar_item_ao_pedido(pedido_id, produto_id, quantidade):
        # Buscar entidades
        pedido = Pedido.objects.get(id=pedido_id)
        produto = Produto.objects.get(id=produto_id)
        
        # Aplicar regras de negócio
        if not ClienteService.verificar_restricoes_produto(pedido.cliente.id, produto_id):
            raise ValidationError("Cliente possui restrições para este produto")
        
        # Executar operação
        pedido.add_item(produto, quantidade)
        return pedido
```

### 3. **Use o Service na View**
```python
# produto/views.py
def editar_pedido(request, pedido_id):
    if request.method == 'POST':
        try:
            PedidoService.adicionar_item_ao_pedido(pedido_id, produto_id, quantidade)
            messages.success(request, 'Item adicionado!')
        except ValidationError as e:
            messages.error(request, str(e))
```

### 4. **Teste a Regra**
```python
# produto/tests.py
def test_restricao_alimentar():
    cliente = Cliente.objects.create(name="João")
    cliente.alimentary_restrictions.add(gluten)
    
    produto_com_gluten = Produto.objects.create(name="Pão")
    produto_com_gluten.alimento.alimentary_restrictions.add(gluten)
    
    with pytest.raises(ValidationError):
        PedidoService.adicionar_item_ao_pedido(pedido.id, produto_com_gluten.id, 1)
```

## Fluxo de Dados

```
HTTP Request → URL → View → Service → Model → Database
                ↓
Template ← View ← Service ← Model ← Database
```

## Exemplos de Regras de Negócio Implementadas

### 1. **Validação de Restrições Alimentares**
- **Local**: `ClienteService.verificar_restricoes_produto()`
- **Regra**: Cliente não pode consumir produto com restrições que possui

### 2. **Processamento de Pagamento**
- **Local**: `PagamentoService.processar_pagamento()`
- **Regra**: Cliente deve ter saldo suficiente para pagar o pedido

### 3. **Gerenciamento da Cozinha**
- **Local**: `CozinhaService.iniciar_proximo_pedido()`
- **Regra**: Cozinha não pode exceder sua capacidade máxima

### 4. **Controle de Status**
- **Local**: `StatusManager.can_transition_to()`
- **Regra**: Pedidos seguem fluxo específico de status

## URLs Disponíveis

- `/clientes/` - Lista de clientes
- `/clientes/criar/` - Criar novo cliente
- `/pedidos/` - Lista de pedidos
- `/pedidos/criar/<cliente_id>/` - Criar pedido para cliente
- `/cozinha/` - Gerenciar cozinha
- `/produtos/` - Lista de produtos
- `/api/verificar-restricoes/` - API para verificar restrições

## Comandos Úteis

### Criar Migrações
```bash
python manage.py makemigrations
```

### Aplicar Migrações
```bash
python manage.py migrate
```

### Criar Superusuário
```bash
python manage.py createsuperuser
```

### Executar Servidor
```bash
python manage.py runserver
```

### Executar Testes
```bash
python manage.py test
```

## Próximos Passos

1. **Implementar Testes**: Criar testes unitários para services e views
2. **Adicionar Logging**: Implementar logs detalhados para auditoria
3. **Criar APIs REST**: Usar Django REST Framework para APIs
4. **Implementar Cache**: Adicionar cache para melhor performance
5. **Configurar Celery**: Para tarefas assíncronas (arquivo `tasks.py` já preparado)

## Estrutura Completa

```
produto/
├── __init__.py
├── admin.py           # Configuração do painel admin
├── apps.py           # Configuração do app
├── models.py         # Entidades/Models
├── views.py          # Controllers/Views
├── urls.py           # Roteamento
├── tasks.py          # Tarefas assíncronas (opcional)
├── services/         # Lógica de negócio
│   ├── __init__.py
│   └── business_services.py
├── utils/            # Utilitários
│   ├── __init__.py
│   └── validators.py
├── templates/        # Templates HTML
│   └── produto/
│       ├── base.html
│       ├── listar_clientes.html
│       └── criar_cliente.html
├── migrations/       # Migrações do banco
└── tests.py         # Testes
```

Esta estrutura garante:
- ✅ **Separação de responsabilidades**
- ✅ **Código reutilizável**
- ✅ **Facilidade de teste**
- ✅ **Manutenibilidade**
- ✅ **Escalabilidade**