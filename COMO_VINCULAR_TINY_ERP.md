# 🔗 Como Vincular Produtos do Tiny ERP

## 📋 Passo a Passo

### 1. Acesse o Formulário de Peça

- Acesse o sistema: `http://localhost:8000/`
- Vá em **Coleções** → **Peças**
- Clique em **Nova Peça** ou edite uma peça existente

### 2. Preencha os Dados da Peça

Preencha todos os campos obrigatórios:
- Coleção
- Categoria
- Tecido
- Status
- Preço de Venda
- Custo Total
- Consumo de tecido por tamanho
- Quantidade inicial por tamanho
- Acessórios (opcional)

### 3. Buscar Produto no Tiny ERP

Role até a seção **🔗 Integração com Tiny ERP** (no final do formulário).

1. **Digite o nome do produto** no campo de busca
   - Exemplo: "Camiseta", "Vestido", etc.
   - Precisa ter pelo menos 2 caracteres

2. **Clique no botão "🔍 Buscar"** (ou pressione Enter)
   - Um spinner de carregamento aparecerá
   - A busca é feita em tempo real na API do Tiny ERP

3. **Aguarde os resultados**
   - Se encontrar produtos, uma lista aparecerá
   - Cada item mostra: Nome - SKU - Estoque

4. **Selecione o produto desejado**
   - Clique no produto na lista
   - O botão "✓ Vincular Produto Selecionado" ficará ativo

5. **Clique em "✓ Vincular Produto Selecionado"**
   - O sistema vincula o produto do Tiny ao banco de dados local
   - Uma mensagem de sucesso aparecerá

6. **Salve o formulário**
   - Clique no botão "Criar Peça" ou "Salvar" no final do formulário
   - A vinculação será salva permanentemente

### 4. Sincronizar o Estoque

Após vincular e salvar a peça, sincronize o estoque:

```bash
python manage.py sync_piece_stock --piece <ID_DA_PEÇA>
```

Ou sincronize todas as peças vinculadas:

```bash
python manage.py sync_piece_stock
```

### 5. Verificar Estoque Sincronizado

- Edite a peça novamente
- Na seção **🔗 Integração com Tiny ERP** você verá:
  - ✓ "Esta peça está vinculada ao Tiny ERP"
  - Nome do produto vinculado
  - Data da última sincronização
  - Estoque atual por tamanho (P, M, G, GG)

---

## 🎯 Exemplo Prático

### Cenário: Criar uma peça de "Camiseta Básica"

1. **Criar nova peça:**
   - Coleção: "Verão 2024"
   - Categoria: "Camisetas"
   - Tecido: "Algodão"
   - Preço: R$ 59,90
   - Custo: R$ 25,00

2. **Buscar no Tiny ERP:**
   - Digite: "camiseta"
   - Clique em **Buscar**
   - Resultados aparecem:
     ```
     Camiseta Básica Branca - SKU: CAM001 - Estoque: 150
     Camiseta Premium - SKU: CAM002 - Estoque: 80
     Camiseta Estampada - SKU: CAM003 - Estoque: 45
     ```

3. **Selecionar e Vincular:**
   - Clique em "Camiseta Básica Branca"
   - Clique em **Vincular Produto Selecionado**
   - Mensagem: "✓ Produto 'Camiseta Básica Branca' vinculado com sucesso!"

4. **Salvar:**
   - Clique em **Criar Peça**
   - Peça salva com vinculação

5. **Sincronizar:**
   ```bash
   python manage.py sync_piece_stock --piece 1
   ```

6. **Verificar:**
   - Edite a peça
   - Veja o estoque sincronizado: P=37, M=38, G=38, GG=37 (Total: 150)

---

## ⚙️ Configuração Necessária

### Credenciais do Tiny ERP

Configure o arquivo `.env` com suas credenciais:

```env
TINY_ERP_API_TOKEN=seu_token_aqui
TINY_ERP_API_URL=https://api.tiny.com.br/api2
```

### Como obter o Token do Tiny ERP:

1. Acesse: https://www.tiny.com.br/
2. Faça login na sua conta
3. Vá em: **Configurações** → **Integrações** → **API**
4. Copie seu **Token de Autenticação**
5. Cole no arquivo `.env`

---

## 🔄 Como Funciona

### Fluxo da Busca:

1. **Frontend (JavaScript):**
   - Usuário digita o nome do produto
   - Clica em "Buscar"
   - JavaScript faz requisição AJAX para `/api/tiny/search/?q=nome`

2. **Backend (Django View):**
   - Recebe o termo de busca
   - Chama a API do Tiny ERP: `https://api.tiny.com.br/api2/produtos.pesquisa.php`
   - Parâmetros: `token`, `formato=json`, `pesquisa=nome`
   - Retorna lista de produtos em JSON

3. **Exibição dos Resultados:**
   - JavaScript recebe os produtos
   - Popula o seletor com os resultados
   - Mostra: Nome - SKU - Estoque

4. **Vinculação:**
   - Usuário seleciona um produto
   - Clica em "Vincular"
   - JavaScript faz requisição POST para `/api/tiny/link/`
   - Backend cria/atualiza `InventoryPiece` no banco de dados
   - Retorna o ID do `InventoryPiece`
   - JavaScript atualiza o campo oculto `tiny_erp_piece`

5. **Salvamento:**
   - Usuário clica em "Salvar/Criar Peça"
   - Formulário é submetido com o `tiny_erp_piece_id`
   - Peça é salva com a vinculação

### Distribuição de Estoque:

O estoque total do Tiny ERP é distribuído **igualmente** entre os 4 tamanhos:

- **Estoque Total:** 100 unidades
- **Distribuição:** P=25, M=25, G=25, GG=25

Para customizar essa lógica, edite: `store_collections/tiny_erp_sync.py`

---

## ❓ Solução de Problemas

### "Erro 404: Not Found"

**Problema:** Token inválido ou URL incorreta

**Solução:**
1. Verifique se o token está correto no `.env`
2. Verifique se a URL é: `https://api.tiny.com.br/api2`
3. Teste o token diretamente na API do Tiny

### "Nenhum produto encontrado"

**Problema:** Produto não existe no Tiny ou termo de busca incorreto

**Solução:**
1. Verifique se o produto está cadastrado no Tiny ERP
2. Tente buscar por um termo mais genérico
3. Verifique a ortografia

### "Erro ao buscar produtos"

**Problema:** Credenciais não configuradas ou API fora do ar

**Solução:**
1. Verifique se o `.env` tem as credenciais
2. Reinicie o servidor Django: `python manage.py runserver`
3. Teste a API do Tiny diretamente

### "Produto vinculado mas estoque não aparece"

**Problema:** Estoque não foi sincronizado

**Solução:**
```bash
python manage.py sync_piece_stock --piece <ID> --verbose
```

---

## 📊 Endpoints da API

### Buscar Produtos
```
GET /api/tiny/search/?q=<termo>
Response: {
    "success": true,
    "products": [
        {
            "id": "123",
            "name": "Produto",
            "sku": "SKU123",
            "price": 50.00,
            "quantity": 100,
            "unit": "UN"
        }
    ],
    "count": 1
}
```

### Vincular Produto
```
POST /api/tiny/link/
Body: {
    "product": {
        "id": "123",
        "name": "Produto",
        "sku": "SKU123",
        "price": 50.00,
        "quantity": 100
    }
}
Response: {
    "success": true,
    "inventory_piece_id": 5,
    "inventory_piece_name": "Produto",
    "message": "Produto vinculado com sucesso!"
}
```

---

## 🎉 Pronto!

Agora você pode:
- ✅ Buscar produtos do Tiny ERP em tempo real
- ✅ Vincular produtos às peças do sistema
- ✅ Sincronizar estoques automaticamente
- ✅ Visualizar estoque por tamanho

**Dica:** Configure um cron job para sincronizar o estoque automaticamente a cada X horas!
