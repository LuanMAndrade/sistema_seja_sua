# 🔄 Guia de Variações do Tiny ERP

## 📦 Como Funciona Agora

O sistema foi atualizado para suportar **variações de tamanho** do Tiny ERP!

### ✨ O Que Mudou

1. **Busca Detalhada de Produtos**
   - Ao vincular um produto, o sistema busca os detalhes completos do Tiny ERP
   - Inclui todas as variações de tamanho do produto

2. **Mapeamento Automático de Tamanhos**
   - Variações do Tiny ERP são mapeadas para P, M, G, GG
   - O estoque de cada variação é salvo separadamente

3. **Sincronização Inteligente**
   - Se o produto tem variações → usa o estoque específico de cada tamanho
   - Se o produto não tem variações → distribui o estoque igualmente

---

## 🎯 Produtos com Variações

### Exemplo: Camiseta Básica

**No Tiny ERP:**
```
Produto: Camiseta Básica Branca (ID: 12345)
  Variação 1: P - Estoque: 25
  Variação 2: M - Estoque: 30
  Variação 3: G - Estoque: 28
  Variação 4: GG - Estoque: 17
  Total: 100 unidades
```

**No Sistema:**
```
Após vincular e sincronizar:
  P: 25
  M: 30
  G: 28
  GG: 17
  Total: 100
```

### Mapeamento de Tamanhos

O sistema reconhece as seguintes nomenclaturas (case insensitive):

| Tamanho | Variações Reconhecidas |
|---------|------------------------|
| **P**   | P, PP, PEQUENO, SMALL, S |
| **M**   | M, MEDIO, MÉDIO, MEDIUM |
| **G**   | G, GRANDE, LARGE, L |
| **GG**  | GG, XG, XL, EXTRA GRANDE, EXTRA LARGE, XXL |

### Exemplo de Nomes Aceitos

✅ **Reconhecidos como P:**
- "Camiseta - Tamanho P"
- "Vestido PP Vermelho"
- "Blusa Pequeno"
- "T-Shirt Small"

✅ **Reconhecidos como GG:**
- "Camiseta GG"
- "Vestido Extra Grande"
- "Blusa XL"
- "T-Shirt XXL"

---

## 🔧 Como Usar

### 1. Vincular Produto com Variações

1. Acesse criar/editar peça
2. Busque o produto no Tiny ERP
3. Selecione o **produto pai** (não as variações individuais)
4. Clique em "Vincular"
5. O sistema automaticamente:
   - Busca os detalhes do produto
   - Identifica as variações
   - Mapeia os tamanhos
   - Salva os estoques separadamente

### 2. Sincronizar Estoque

```bash
python manage.py sync_piece_stock --piece <ID> --verbose
```

Você verá no log:
```
Fetching product details for ID: 12345
Product has 4 variations, total stock: 100
Mapped variation stock: {'P': 25, 'M': 30, 'G': 28, 'GG': 17}
Using variation stock for piece 1: P:25, M:30, G:28, GG:17
Successfully synced stock for piece 1 (Verão 2024): Total=100
```

### 3. Verificar no Formulário

Ao editar a peça, você verá:
```
✓ Esta peça está vinculada ao Tiny ERP
Produto vinculado: Camiseta Básica Branca
Última sincronização: 20/11/2025 14:30

Estoque Atual:
┌────┬────┬────┬────┬───────┐
│ P  │ M  │ G  │ GG │ Total │
├────┼────┼────┼────┼───────┤
│ 25 │ 30 │ 28 │ 17 │  100  │
└────┴────┴────┴────┴───────┘
```

---

## 📊 Produtos SEM Variações

### Exemplo: Lenço Básico

**No Tiny ERP:**
```
Produto: Lenço Básico (ID: 67890)
  Estoque: 80 unidades
  (sem variações de tamanho)
```

**No Sistema:**
```
Após vincular e sincronizar:
  P: 20
  M: 20
  G: 20
  GG: 20
  Total: 80 (distribuído igualmente)
```

O sistema detecta automaticamente que não há variações e distribui o estoque igualmente entre os 4 tamanhos.

---

## 🔍 Verificar Variações no Banco

### Via Django Shell

```bash
python manage.py shell
```

```python
from inventory.models import InventoryPiece

# Ver produtos com variações
pieces_with_variations = InventoryPiece.objects.filter(has_variations=True)
for piece in pieces_with_variations:
    print(f"{piece.name}:")
    print(f"  P: {piece.stock_p}")
    print(f"  M: {piece.stock_m}")
    print(f"  G: {piece.stock_g}")
    print(f"  GG: {piece.stock_gg}")
    print(f"  Total: {piece.quantity}")
    print()

# Ver dados brutos das variações
piece = InventoryPiece.objects.get(external_id='12345')
print(piece.variations_data)
```

### Via Django Admin

1. Acesse: `http://localhost:8000/admin/inventory/inventorypiece/`
2. Clique em um produto
3. Veja os campos:
   - **Has variations:** ✓ (se tiver variações)
   - **Stock P, M, G, GG:** estoques individuais
   - **Variations data:** JSON com dados brutos

---

## 🛠️ Estrutura Técnica

### Campos Adicionados em InventoryPiece

```python
has_variations = BooleanField  # True se tem variações
stock_p = IntegerField         # Estoque tamanho P
stock_m = IntegerField         # Estoque tamanho M
stock_g = IntegerField         # Estoque tamanho G
stock_gg = IntegerField        # Estoque tamanho GG
variations_data = JSONField    # Dados brutos das variações
```

### Endpoint da API Tiny

**Buscar Produtos:**
```
GET https://api.tiny.com.br/api2/produtos.pesquisa.php
Params: token, formato=json, pesquisa=<nome>
```

**Obter Detalhes (com variações):**
```
GET https://api.tiny.com.br/api2/produto.obter.php
Params: token, formato=json, id=<product_id>

Response:
{
  "retorno": {
    "produto": {
      "id": "12345",
      "nome": "Camiseta Básica",
      "variacoes": [
        {
          "grade": {"nome": "P"},
          "saldo": 25
        },
        {
          "grade": {"nome": "M"},
          "saldo": 30
        },
        ...
      ]
    }
  }
}
```

### Fluxo de Vinculação

```
1. Usuário busca "Camiseta"
   ↓
2. API retorna lista de produtos
   ↓
3. Usuário seleciona produto pai
   ↓
4. Sistema faz segunda requisição: produto.obter.php
   ↓
5. Obtém variações do produto
   ↓
6. Mapeia variações para P, M, G, GG
   ↓
7. Salva no InventoryPiece:
   - has_variations = True
   - stock_p, stock_m, stock_g, stock_gg
   - variations_data (JSON)
   ↓
8. Vincula ao Piece
   ↓
9. Sincronização usa os estoques mapeados
```

---

## ❓ Troubleshooting

### "Estoque aparece como 0 mesmo com estoque no Tiny"

**Causas possíveis:**

1. **Nomes de variação não reconhecidos**
   - Solução: Verifique os nomes das variações no Tiny
   - Adicione novos nomes em `tiny_search.py:164-169`

2. **Campo de estoque errado**
   - O sistema usa o campo `saldo` das variações
   - Verifique se o Tiny retorna esse campo

3. **Produto sem variações**
   - Se o produto não tem variações, o estoque é distribuído igualmente
   - Verifique `has_variations` no admin

### "Variações não estão sendo mapeadas corretamente"

**Debug:**

```bash
python manage.py shell
```

```python
from store_collections.tiny_search import TinyERPSearch

tiny = TinyERPSearch()

# Buscar produto
produtos = tiny.search_products("camiseta")
print(produtos)

# Obter detalhes
detalhes = tiny.get_product_details("12345")
print(detalhes.get('variacoes'))

# Testar mapeamento
variacoes = detalhes.get('variacoes', [])
mapeamento = tiny.map_size_variations(variacoes)
print(mapeamento)  # {'P': X, 'M': Y, 'G': Z, 'GG': W}
```

### "Produto tem variações mas estoque está zerado"

1. **Verifique o log ao vincular:**
   ```
   Mapped variation stock: {'P': 0, 'M': 0, 'G': 0, 'GG': 0}
   ```

2. **Possíveis causas:**
   - Nomes das variações não foram reconhecidos
   - Campo `grade.nome` está vazio ou diferente

3. **Solução:**
   - Adicione log para debug:
   ```python
   # Em tiny_search.py, linha 171
   print(f"Checking variation: {variation}")
   print(f"Grade nome: {variation_name}")
   print(f"Estoque: {estoque}")
   ```

### "Como adicionar novos tamanhos?"

Edite `tiny_search.py:164-169`:

```python
size_mappings = {
    'P': ['P', 'PP', 'PEQUENO', 'SMALL', 'S', 'XS'],  # Adicione aqui
    'M': ['M', 'MEDIO', 'MÉDIO', 'MEDIUM'],
    'G': ['G', 'GRANDE', 'LARGE', 'L'],
    'GG': ['GG', 'XG', 'XL', 'EXTRA GRANDE', 'EXTRA LARGE', 'XXL', '2XL', '3XL']
}
```

---

## 📈 Logs Úteis

### Logs ao Vincular

```
INFO: Searching Tiny ERP for: 'camiseta'
INFO: Found 5 products matching 'camiseta'
INFO: Fetching product details for ID: 12345
INFO: Product has 4 variations, total stock: 100
INFO: Mapped variation stock: {'P': 25, 'M': 30, 'G': 28, 'GG': 17}
INFO: Created InventoryPiece: Camiseta Básica (P:25, M:30, G:28, GG:17)
```

### Logs ao Sincronizar

```
INFO: Using variation stock for piece 1: P:25, M:30, G:28, GG:17
INFO: Successfully synced stock for piece 1 (Verão 2024): Total=100
```

---

## 🎉 Benefícios

✅ **Estoque Real:** Usa o estoque exato de cada tamanho do Tiny
✅ **Automático:** Mapeamento automático de variações
✅ **Flexível:** Funciona com ou sem variações
✅ **Rastreável:** Logs detalhados de cada operação
✅ **Extensível:** Fácil adicionar novos mapeamentos de tamanho

---

**Última atualização:** Novembro 2025
