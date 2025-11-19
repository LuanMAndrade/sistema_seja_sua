# Sistema Seja Sua

Sistema completo de gestão para loja de roupas, desenvolvido com Django e PostgreSQL.

## Visão Geral

O **Sistema Seja Sua** é uma aplicação web (desktop) para gerenciamento completo de negócios de confecção, incluindo:

- **Coleções** - Gerenciamento de coleções, peças, tecidos e acessórios
- **Estoque** - Controle de inventário integrado com Tiny ERP
- **Finanças** - Fluxo de caixa, entradas, saídas e previsões
- **Calendário** - Cronograma de produção com integração Google Calendar
- **Estatísticas** - Análise de vendas e previsões com ciência de dados
- **Marketing** - Campanhas e gestão de redes sociais
- **Anotações** - Bloco de notas com salvamento automático
- **Configurações** - Fornecedores, categorias e prazos padrão

## Tecnologias

- **Backend:** Django 5.0
- **Banco de Dados:** PostgreSQL
- **Frontend:** Django Templates, HTML, CSS, JavaScript
- **APIs:** Google Calendar API, Tiny ERP API
- **Análise de Dados:** NumPy, Pandas, SciPy

## Instalação

### 1. Pré-requisitos

- Python 3.10+
- PostgreSQL 14+
- Git

### 2. Clone o Repositório

```bash
git clone <repository-url>
cd "Sistema Seja Sua"
```

### 3. Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 4. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurar Banco de Dados PostgreSQL

```bash
# Criar banco de dados
createdb store_management_db

# Ou via psql:
psql -U postgres
CREATE DATABASE store_management_db;
\q
```

### 6. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# Configure pelo menos:
# - DB_PASSWORD (sua senha do PostgreSQL)
# - TINY_ERP_API_TOKEN (se disponível)
```

### 7. Executar Migrações

```bash
python manage.py migrate
```

### 8. Criar Superusuário

```bash
python manage.py createsuperuser
```

### 9. Executar Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse:
- **Home:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

## Configuração de APIs

### Google Calendar API

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a Google Calendar API
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo `credentials.json`
6. Coloque `credentials.json` na raiz do projeto
7. Na primeira execução, você será solicitado a autorizar o acesso

### Tiny ERP API

1. Acesse sua conta no [Tiny ERP](https://www.tiny.com.br/)
2. Vá em Configurações > Integrações > API
3. Copie seu token de API
4. Cole no arquivo `.env` em `TINY_ERP_API_TOKEN`

## Comandos de Sincronização

### Sincronizar Estoque

```bash
python manage.py sync_inventory
```

Sincroniza peças de estoque do Tiny ERP.

### Sincronizar Finanças

```bash
python manage.py sync_finance
```

Sincroniza entradas e saídas financeiras do Tiny ERP.

### Sincronizar Vendas

```bash
python manage.py sync_sales
```

Sincroniza dados de vendas do Tiny ERP.

### Sincronizar Calendário

```bash
python manage.py sync_calendar
```

Sincroniza eventos com Google Calendar.

Opções:
- `--all`: Sincroniza todos os eventos (não apenas novos)
- `--verbose`: Mostra saída detalhada

## Funcionalidades Automáticas

### Triggers Automáticos ao Salvar Coleção

Quando uma coleção é salva com data de lançamento, o sistema automaticamente:

1. **Cria eventos no calendário** para cada etapa da produção:
   - Modelagem
   - Peça Piloto
   - Peça Teste
   - Produção
   - Preparação
   - Transporte
   - Lançamento

2. **Calcula datas** retroativamente a partir da data de lançamento

3. **Sincroniza com Google Calendar** (se configurado)

4. **Atualiza estatísticas** da coleção

### Auto-save em Notas

O sistema salva automaticamente suas anotações após 2 segundos de inatividade ao digitar.

## Estrutura do Projeto

```
Sistema Seja Sua/
├── store_management/       # Configurações do projeto Django
├── business_settings/      # Fornecedores, categorias, prazos
├── store_collections/      # Coleções, peças, tecidos
├── inventory/              # Estoque e integração Tiny ERP
├── finance/                # Finanças e integração Tiny ERP
├── calendar_app/           # Calendário e Google Calendar
├── sales_stats/            # Estatísticas e previsões
├── marketing/              # Campanhas e redes sociais
├── notes/                  # Anotações
├── templates/              # Templates HTML
├── static/                 # CSS, JavaScript, imagens
├── media/                  # Uploads de arquivos
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não versionado)
└── manage.py               # CLI do Django
```

## Workflow de Uso

### 1. Configuração Inicial

1. Acesse Admin Django: http://localhost:8000/admin/
2. Configure **Business Settings**:
   - Adicione fornecedores
   - Crie categorias de peças
   - Defina prazos padrão de produção

### 2. Criar Coleção

1. Vá em **Coleções** > **Add Collection**
2. Preencha:
   - Nome da coleção
   - Status (Aguardando Modelador, etc.)
   - Data esperada de lançamento
   - Prazos de produção (ou use prazos padrão)
3. Salvar

**Resultado:** Sistema cria automaticamente eventos no calendário!

### 3. Adicionar Peças à Coleção

1. Crie tecidos (se necessário)
2. Adicione peças à coleção:
   - Categoria
   - Tecido
   - Consumo por tamanho (P, M, G, GG)
   - Preço de venda
   - Custo total
   - Quantidades iniciais

### 4. Sincronizar Dados Externos

Execute regularmente (ou configure cron):

```bash
# Diariamente
python manage.py sync_inventory
python manage.py sync_finance
python manage.py sync_sales

# Após criar/editar eventos
python manage.py sync_calendar
```

### 5. Acompanhar Estatísticas

- Acesse **Estatísticas** no menu
- Veja vendas por peça, coleção e tecido
- Analise previsões de vendas

## Comandos Úteis

```bash
# Criar nova migração
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell interativo
python manage.py shell

# Testes
python manage.py test
```

## Segurança

### Dados Sensíveis

Os seguintes arquivos **NÃO** devem ser commitados no Git:
- `.env` - Variáveis de ambiente
- `credentials.json` - Credenciais Google Calendar
- `token.json` - Token OAuth Google
- `db.sqlite3` - Banco de dados local
- `media/` - Uploads de usuários

Todos estão listados no `.gitignore`.

### Produção

Para deploy em produção:

1. Configure `DEBUG=False` no `.env`
2. Altere `SECRET_KEY` para uma chave única
3. Configure `ALLOWED_HOSTS` adequadamente
4. Use HTTPS
5. Configure backup automático do PostgreSQL

## Suporte

Para documentação adicional, consulte:
- `CLAUDE.md` - Documentação técnica para desenvolvimento
- Django Docs: https://docs.djangoproject.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/

## Licença

Proprietário - Sistema desenvolvido para uso exclusivo da Seja Sua.
