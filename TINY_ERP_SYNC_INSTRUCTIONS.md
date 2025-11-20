# 📦 Instruções de Sincronização com Tiny ERP

## 🎯 Como Usar a Sincronização de Estoque

### Passo 1: Sincronizar Produtos do Tiny ERP

Antes de vincular peças, você precisa importar os produtos do Tiny ERP:

```bash
python manage.py sync_inventory
```

Este comando busca todos os produtos cadastrados no Tiny ERP e os salva no banco de dados local.

### Passo 2: Criar ou Editar uma Peça

1. Acesse o formulário de criação/edição de peça
2. Preencha todos os campos normais (coleção, categoria, tecido, etc.)
3. **Na seção "🔗 Integração com Tiny ERP"**, você verá:
   - Um dropdown com todas as peças disponíveis do Tiny ERP
   - A opção "--- Selecione uma peça do Tiny ERP (opcional) ---"

4. Selecione a peça do Tiny ERP correspondente
5. Salve a peça

### Passo 3: Sincronizar o Estoque

Após vincular a peça ao Tiny ERP, sincronize o estoque usando um dos comandos:

#### Sincronizar todas as peças vinculadas:
```bash
python manage.py sync_piece_stock
```

#### Sincronizar uma peça específica:
```bash
python manage.py sync_piece_stock --piece <ID_DA_PEÇA>
```

#### Sincronizar todas as peças de uma coleção:
```bash
python manage.py sync_piece_stock --collection <ID_DA_COLEÇÃO>
```

#### Modo verbose (mostra detalhes):
```bash
python manage.py sync_piece_stock --verbose
```

#### Sincronizar inventário antes do estoque:
```bash
python manage.py sync_piece_stock --sync-inventory-first
```

### Passo 4: Verificar o Estoque Sincronizado

Ao editar a peça novamente, você verá:
- ✓ "Esta peça está vinculada ao Tiny ERP"
- Nome do produto vinculado
- Data da última sincronização
- Estoque atual por tamanho (P, M, G, GG)
- Estoque total

---

## 🔄 Sincronização Automática (Opcional)

Para sincronizar automaticamente o estoque em intervalos regulares, configure um cron job:

### Windows (Task Scheduler):

1. Abra o "Agendador de Tarefas"
2. Crie uma nova tarefa básica
3. Configure para executar a cada 4 horas (ou conforme necessário)
4. Ação: Iniciar um programa
5. Programa: `C:\caminho\para\python.exe`
6. Argumentos: `manage.py sync_piece_stock`
7. Iniciar em: `C:\caminho\do\projeto`

### Linux/Mac (crontab):

```bash
# Editar crontab
crontab -e

# Adicionar linha para sincronizar a cada 4 horas
0 */4 * * * cd /caminho/do/projeto && source venv/bin/activate && python manage.py sync_piece_stock

# Ou diariamente às 2h da manhã
0 2 * * * cd /caminho/do/projeto && source venv/bin/activate && python manage.py sync_piece_stock --verbose
```

---

## 📊 Sincronização pelo Django Admin

Você também pode sincronizar peças diretamente pelo admin do Django:

1. Acesse: `http://localhost:8000/admin/store_collections/piece/`
2. Selecione as peças que deseja sincronizar (marque as checkboxes)
3. No menu "Ação", selecione **"Sincronizar estoque do Tiny ERP"**
4. Clique em "Executar"

O sistema mostrará quantas peças foram sincronizadas com sucesso.

---

## 📋 Informações Importantes

### Como o Estoque é Distribuído

Por padrão, o estoque total da peça no Tiny ERP é **distribuído igualmente** entre os 4 tamanhos (P, M, G, GG).

**Exemplo:**
- Estoque no Tiny ERP: 100 unidades
- Distribuição: P=25, M=25, G=25, GG=25

### Customizar a Distribuição de Estoque

Se você quiser uma distribuição diferente (por exemplo, baseada em variantes do Tiny ou proporções específicas), edite o arquivo:

`store_collections/tiny_erp_sync.py` - linhas 25-36

### Campos Somente Leitura

Os seguintes campos são **somente leitura** e só podem ser atualizados pela sincronização:
- `current_stock_p`
- `current_stock_m`
- `current_stock_g`
- `current_stock_gg`
- `stock_last_synced`

---

## 🔍 Verificação Rápida

### Verificar se há peças do Tiny ERP disponíveis:

```bash
python manage.py shell
```

```python
from inventory.models import InventoryPiece
print(f"Peças disponíveis do Tiny ERP: {InventoryPiece.objects.count()}")
for piece in InventoryPiece.objects.all()[:5]:
    print(f"- {piece.name} (SKU: {piece.sku}) - Estoque: {piece.quantity}")
```

### Verificar peças vinculadas:

```python
from store_collections.models import Piece
linked = Piece.objects.filter(tiny_erp_piece__isnull=False)
print(f"Peças vinculadas ao Tiny ERP: {linked.count()}")
for piece in linked:
    print(f"- {piece} -> {piece.tiny_erp_piece.name} (Estoque: {piece.total_current_stock})")
```

---

## ❓ Solução de Problemas

### "Nenhuma peça do Tiny ERP aparece no dropdown"

**Solução:** Execute primeiro o comando para sincronizar o inventário:
```bash
python manage.py sync_inventory
```

### "Erro ao sincronizar: API credentials not configured"

**Solução:** Configure as credenciais do Tiny ERP no arquivo `.env`:
```
TINY_ERP_API_TOKEN=seu_token_aqui
TINY_ERP_API_URL=https://api.tiny.com.br/api2
```

### "Estoque não atualizou após sincronizar"

**Solução:**
1. Verifique se a peça está realmente vinculada ao Tiny ERP
2. Execute o comando em modo verbose para ver erros:
   ```bash
   python manage.py sync_piece_stock --piece <ID> --verbose
   ```
3. Verifique os logs do Django para mensagens de erro

---

## 📞 Suporte

Se você encontrar problemas, verifique:
1. Os logs do Django (console onde o servidor está rodando)
2. Se as credenciais do Tiny ERP estão corretas
3. Se o inventário foi sincronizado antes
4. Se a peça está vinculada corretamente

---

**Última atualização:** $(date)
