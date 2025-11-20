# Guia de Configuração - Google Calendar API

## ✅ O que você já tem configurado

1. **Arquivo `credentials.json`** - Criado com suas credenciais OAuth do Google Cloud
2. **Variáveis no `.env`** - Configuradas corretamente
3. **Serviço de integração** - Já implementado no sistema

## 📋 Próximos Passos para Ativar a Integração

### Passo 1: Instalar as Bibliotecas Necessárias

Execute no terminal:

```bash
source venv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Passo 2: Primeira Autenticação (OAuth)

Execute o comando de teste que criamos:

```bash
python manage.py test_google_calendar
```

**O que vai acontecer:**

1. Uma janela do navegador será aberta automaticamente
2. Você será solicitado a fazer login na sua conta Google
3. O Google vai pedir permissão para o app acessar seu calendário
4. Clique em "Permitir" ou "Allow"
5. Um arquivo `token.json` será criado automaticamente
6. O comando vai testar a conexão e mostrar seus próximos eventos

### Passo 3: Verificar se Funcionou

Após a autenticação, você verá uma mensagem de sucesso:

```
✓ Serviço autenticado com sucesso!
✓ Acesso ao calendário confirmado!
✓ Encontrados X eventos futuros
```

## 🔄 Como Funciona a Sincronização Automática

Após a configuração, o sistema vai **automaticamente**:

1. **Criar eventos no Google Calendar** quando você criar uma Coleção com data prevista de lançamento
2. **Atualizar eventos** quando você editar as datas
3. **Deletar eventos** quando você remover a coleção

## 📝 Arquivos Importantes

- `credentials.json` - Credenciais OAuth (NÃO compartilhe!)
- `token.json` - Token de acesso (será criado automaticamente na primeira autenticação)
- Ambos os arquivos devem ficar na raiz do projeto

## ⚠️ Importante

1. **Não compartilhe** o arquivo `credentials.json` - ele contém informações sensíveis
2. O arquivo `token.json` será criado automaticamente na primeira execução
3. Se precisar reautenticar, delete o `token.json` e execute o comando novamente
4. A autenticação precisa ser feita apenas UMA VEZ

## 🔧 Solução de Problemas

### Erro: "credentials.json not found"
- Verifique se o arquivo está na raiz do projeto
- Confirme que o nome está correto (sem espaços)

### Erro: "Invalid credentials"
- Verifique se copiou as credenciais corretamente do Google Cloud Console
- Certifique-se de que a API do Google Calendar está ativada no seu projeto

### Erro: "Access denied"
- Durante a autenticação, clique em "Allow/Permitir"
- Se negou acesso, delete o `token.json` e tente novamente

### Navegador não abre automaticamente
- Copie o link que aparece no terminal e cole no navegador
- Complete a autenticação manualmente

## 🎯 Testando a Integração

Depois de autenticar, teste criando uma nova coleção:

1. Acesse: http://localhost:8000/collections/new/
2. Preencha o nome e a data prevista de lançamento
3. Salve a coleção
4. Verifique no seu Google Calendar - o evento foi criado automaticamente!

## 📚 Recursos Adicionais

- [Documentação Google Calendar API](https://developers.google.com/calendar/api/guides/overview)
- [Google Cloud Console](https://console.cloud.google.com/)
