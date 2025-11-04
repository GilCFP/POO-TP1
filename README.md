# Sistema de Restaurante - POO TP1

## Visão Geral

Aplicação web para gerenciamento de restaurante desenvolvida em Django, implementando conceitos avançados de Programação Orientada a Objetos (POO).

## Estrutura do Projeto

```
POO-TP1/
├── Classes/                    # Classes Python puras (domínio)
│   ├── EntidadeBase.py        # Classe abstrata base
│   ├── Produto.py             # Hierarquia de produtos
│   ├── Alimento.py
│   ├── Comida.py
│   ├── Bebida.py
│   ├── Combo.py
│   ├── Cliente.py             # Gestão de clientes
│   ├── Pedido.py              # Sistema de pedidos
│   ├── Cozinha.py             # Gerenciamento de cozinha
│   ├── Caixa.py               # Registradora
│   ├── Restaurante.py         # Entidade agregadora
│   ├── StatusPedido.py        # Enumerações
│   └── RestricaoAlimentar.py
│
├── apps/                       # Aplicações Django
│   ├── cliente/               # App de clientes
│   ├── produto/               # App de produtos
│   ├── pedido/                # App de pedidos
│   ├── restaurante/           # App de restaurante
│   └── core/                  # Funcionalidades compartilhadas
│
├── frontend/                   # Frontend React
│   ├── src/
│   └── package.json
│
├── documentos/                 # Documentação técnica
│   ├── GUIA_PROFESSORA.md     # Guia de navegação
│   ├── CORRECOES.md           # Checklist de correções
│   ├── NOVA_ARQUITETURA.md    # Proposta de arquitetura
│   ├── README_ARQUITETURA.md  # Explicação de estrutura
│   └── README_SCRIPTS.md      # Scripts disponíveis
│
├── manage.py                   # Gerenciador Django
├── requirements.txt            # Dependências Python
├── db.sqlite3                  # Banco de dados (desenvolvimento)
└── start.py                    # Script de inicialização

```

## Requisitos

- Python 3.8+
- Django 3.0+
- Node.js 14+ (para frontend)

## Instalação

### Backend (Django)

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser
```

### Frontend (React)

```bash
cd frontend

# Instalar dependências
npm install

# Compilar assets
npm run build
```

## Executando o Projeto

### Servidor de Desenvolvimento

```bash
# Iniciar servidor Django
python manage.py runserver

# Em outro terminal, iniciar frontend (se necessário)
cd frontend
npm start
```

O aplicativo estará disponível em `http://localhost:8000`

## Scripts Disponíveis

- `start.py` - Script de inicialização personalizado
- Consulte `documentos/README_SCRIPTS.md` para detalhes

## Documentação

- **[GUIA_PROFESSORA.md](documentos/GUIA_PROFESSORA.md)** - Introdução e navegação do projeto
- **[CORRECOES.md](documentos/CORRECOES.md)** - Lista de correções implementadas
- **[NOVA_ARQUITETURA.md](documentos/NOVA_ARQUITETURA.md)** - Proposta arquitetônica
- **[README_ARQUITETURA.md](documentos/README_ARQUITETURA.md)** - Explicação da estrutura

## Estrutura de Classes

As classes principais localizam-se em `Classes/`:

- **EntidadeBase** - Classe abstrata base (define `validar()`)
- **Produto** - Classe hierárquica para produtos
  - Alimento
    - Comida
    - Bebida
  - Combo
- **Cliente** - Gerenciamento de clientes
- **Pedido** - Representação de pedidos
- **Cozinha** - Controle de preparação
- **Caixa** - Gestão de transações
- **Restaurante** - Entidade agregadora

## Padrões Implementados

- **Abstract Base Class** - Classe abstrata para contrato comum
- **Encapsulation** - Atributos privados com propriedades
- **Inheritance** - Hierarquia de classes bem definida
- **Validation** - Validações robustas em operações críticas
- **Type Hints** - Tipos definidos em todos os métodos

## Suporte

Para dúvidas sobre:
- Estrutura do projeto: consulte `GUIA_PROFESSORA.md`
- Correções realizadas: consulte `CORRECOES.md`
- Arquitetura técnica: consulte `NOVA_ARQUITETURA.md`
