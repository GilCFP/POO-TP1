# Script de Inicialização do Projeto

Este projeto possui um script Python universal para inicializar automaticamente o frontend e backend.

## Como usar:

### Qualquer Sistema Operacional (Windows/Mac/Linux):
```bash
python start.py
```

ou

```bash
python3 start.py
```

## O que os scripts fazem:

1. **Build do Frontend**: Executa `npm run build:dev` na pasta frontend
2. **Inicia o Backend**: Executa `python manage.py runserver` na raiz do projeto
3. **Feedback Visual**: Mostra o progresso de cada etapa

## Requisitos:

- **Node.js e npm** instalados (para o frontend)
- **Python e Django** instalados (para o backend)
- **Dependências do projeto** instaladas (`npm install` no frontend e `pip install -r requirements.txt` no backend)

## Troubleshooting:

- **Windows**: Use `python start.py`
- **Mac/Linux**: Use `python3 start.py` se `python start.py` não funcionar