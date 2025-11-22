# Configuração do Celery - Sincronização Automática de Estoque

Este documento explica como configurar e usar o sistema de sincronização automática de estoque com histórico.

## 📋 Pré-requisitos

### 1. Instalar Redis

O Celery precisa do Redis como broker de mensagens.

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows (WSL):**
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Verificar se Redis está rodando:**
```bash
redis-cli ping
# Deve retornar: PONG
```

### 2. Instalar Dependências Python

```bash
cd "/mnt/c/Users/Luan/Desktop/VScode Projetos/Sistema Seja Sua"
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Aplicar Migrations do Django Celery Beat

```bash
python manage.py migrate django_celery_beat
```

## 🚀 Como Rodar

### Modo Desenvolvimento (3 terminais)

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A store_management worker -l info
```

**Terminal 3 - Celery Beat (agendador):**
```bash
celery -A store_management beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Modo Produção (com Supervisor ou systemd)

Criar arquivo de service para o worker e beat. Exemplos em `/docs/celery_production.md`

## 🔧 Comandos Úteis

### Testar Sincronização Manual (com histórico)

```bash
python manage.py sync_stock_daily
```

### Testar Sincronização Manual (sem histórico - dry-run)

```bash
python manage.py sync_stock_daily --dry-run
```

### Testar Sincronização com Output Detalhado

```bash
python manage.py sync_stock_daily --verbose
```

### Verificar Tasks Agendadas

```bash
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.all()
```

### Executar Task Manualmente (sem esperar agendamento)

```bash
python manage.py shell
>>> from store_collections.tasks import sync_stock_daily_task
>>> sync_stock_daily_task.delay()
```

## 📊 Como Funciona

### Agendamento
- **Horário:** Todo dia às 00:00 (meia-noite)
- **Timezone:** America/Sao_Paulo
- **Configurado em:** `store_management/celery.py`

### Processo de Sincronização

1. **Busca peças vinculadas** ao Tiny ERP (`tiny_parent_id` não nulo)
2. **Para cada peça e cada tamanho (P, M, G, GG):**
   - Captura estoque atual no banco
   - Busca novo estoque do Tiny ERP via API
   - **Se houver diferença:**
     - Calcula quantidade movimentada
     - Define tipo: "entrada", "saída" ou "inicial"
     - Salva registro em `StockHistory`
     - Atualiza `current_stock_*` na peça
   - **Se não houver diferença:**
     - Não salva histórico (economiza espaço)
     - Apenas atualiza `stock_last_synced`

### Estrutura do Histórico

```python
StockHistory:
  - piece: Qual peça
  - size: P, M, G ou GG
  - quantity: Quantidade movimentada (sempre positivo)
  - movement_type: 'entrada', 'saida' ou 'inicial'
  - stock_after_movement: Estoque após a movimentação
  - date: Data/hora da movimentação
```

## 📁 Ver Histórico no Admin

Acesse: http://localhost:8000/admin/store_collections/stockhistory/

**Filtros disponíveis:**
- Por tipo de movimentação
- Por tamanho
- Por data
- Busca por peça/coleção

**Permissões:**
- Histórico é READ-ONLY
- Não pode adicionar manualmente
- Não pode editar
- Não pode deletar

## 🔍 Consultas Úteis no Django Shell

```python
from store_collections.models import StockHistory, Piece
from datetime import datetime, timedelta
from django.utils import timezone

# Total de saídas no último mês
last_month = timezone.now() - timedelta(days=30)
saidas = StockHistory.objects.filter(
    movement_type='saida',
    date__gte=last_month
)
total_saidas = sum(h.quantity for h in saidas)

# Histórico de uma peça específica
piece = Piece.objects.get(id=1)
historico = piece.stock_history.all()
for h in historico:
    print(f"{h.date} | {h.size} | {h.movement_type} | {h.quantity} un | Estoque após: {h.stock_after_movement}")

# Peças com mais saídas hoje
hoje = timezone.now().date()
from django.db.models import Sum
top_saidas = StockHistory.objects.filter(
    movement_type='saida',
    date__date=hoje
).values('piece__name').annotate(
    total=Sum('quantity')
).order_by('-total')[:10]
```

## ⚙️ Variáveis de Ambiente (.env)

```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🐛 Troubleshooting

### Redis não está rodando
```bash
# Verificar status
sudo systemctl status redis

# Iniciar Redis
sudo systemctl start redis
```

### Celery não está processando tasks
```bash
# Verificar se worker está rodando
celery -A store_management inspect active

# Verificar logs do worker
celery -A store_management worker -l debug
```

### Task não está agendada
```bash
# Ver tasks agendadas no Django Admin
http://localhost:8000/admin/django_celery_beat/periodictask/

# Ou via shell
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.filter(enabled=True)
```

### Forçar execução imediata (sem esperar 00:00)
```bash
python manage.py sync_stock_daily --verbose
```

## 📈 Performance

- **Índices otimizados** para consultas por período
- **Registro seletivo** - só salva quando há mudança
- **Campos mínimos** - apenas o essencial
- **Ideal para:** Consultas por data, peça, tipo de movimento

## 🔐 Segurança

- Histórico é **read-only** no admin
- Apenas sistema pode criar/alterar registros
- Logs de todas as sincronizações
- Retry automático em caso de falha (max 3 tentativas)
