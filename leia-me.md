# Sistema de Gestão - Python Flask

Sistema web completo desenvolvido em Python com Flask para gerenciamento de agenda, contatos, emendas, demandas e usuários.

## Características

- **Interface moderna**: Design responsivo com menu lateral
- **Autenticação**: Sistema de login seguro
- **Módulos completos**: Agenda, Contatos, Emendas, Demandas, Usuários, Cidades e Grupos
- **Banco de dados**: SQLite integrado
- **Exportação**: Excel e impressão
- **Pesquisa**: Sistema de busca em todos os módulos

## Estrutura do Projeto

```
sistema_gestao/
├── app.py                  # Aplicação principal
├── requirements.txt        # Dependências
├── sistema.db             # Banco de dados (criado automaticamente)
├── templates/             # Templates HTML
│   ├── base.html          # Template base
│   ├── login.html         # Página de login
│   ├── dashboard.html     # Dashboard principal
│   ├── agenda.html        # Lista de agenda
│   ├── agenda_form.html   # Formulário de agenda
│   ├── contatos.html      # Lista de contatos
│   ├── contatos_form.html # Formulário de contatos
│   ├── emendas.html       # Lista de emendas
│   ├── emendas_form.html  # Formulário de emendas
│   ├── demandas.html      # Lista de demandas
│   ├── demandas_form.html # Formulário de demandas
│   ├── usuarios.html      # Lista de usuários
│   ├── usuarios_form.html # Formulário de usuários
│   ├── cidades.html       # Lista de cidades
│   ├── cidades_form.html  # Formulário de cidades
│   ├── grupos.html        # Lista de grupos
│   └── grupos_form.html   # Formulário de grupos
└── static/               # Arquivos estáticos (CSS, JS, imagens)
```

## Instalação

1. **Clone ou baixe os arquivos**
   ```bash
   mkdir sistema_gestao
   cd sistema_gestao
   ```

2. **Crie um ambiente virtual** (recomendado)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse o sistema**
   - Abra o navegador e vá para: `http://localhost:5000`
   - **Usuário padrão**: admin
   - **Senha padrão**: admin123

## Módulos do Sistema

### 1. Agenda
- **Campos**: Compromisso, Data, Local, Horário, Status (Realizada/Pendente)
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar, Imprimir

### 2. Contatos
- **Campos**: Nome, Apelido, Endereço, Complemento, Bairro, CEP, Grupo, Aniversário, Lembrete, Empresa, Cargo, Nome do Pai, Nome da Mãe, UF, Cidade
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar, Imprimir

### 3. Emendas
- **Campos**: Número, Ano, Objeto, Proposta, Convênio, Valor, Situação, Valor Pago, Data Pagamento, Ordem Bancária, CNPJ, Assessor, Região, Votos
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar, Importar Excel, Exportar Excel, Imprimir

### 4. Demandas
- **Campos**: Demanda, Solicitante, Data Inicial, Data Final, Andamento, Situação (Aberta/Concluída)
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar, Imprimir

### 5. Usuários
- **Campos**: Nome, Usuário, Email, Senha
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar

### 6. Configurações

#### Cidades
- **Campos**: Cidade, Região, Assessor, Apoiador, Prefeito, Vice-Prefeito, Vereador, Presidente do Partido, Votos
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar, Imprimir

#### Grupos
- **Campos**: Grupo, Subgrupo
- **Funcionalidades**: Pesquisar, Inserir, Excluir, Alterar, Salvar

## Funcionalidades Especiais

### Exportação Excel
- Sistema de exportação para Excel nas Emendas
- Arquivo baixado automaticamente com data no nome

### Sistema de Lembretes
- Lembretes de aniversário (diário ou semanal) nos Contatos

### Pesquisa Avançada
- Sistema de busca em todos os módulos
- Pesquisa por múltiplos campos

### Segurança
- Senhas criptografadas
- Sessões seguras
- Proteção contra acesso não autorizado

## Personalização

### Cores e Visual
- Edite o CSS no arquivo `templates/base.html`
- Gradient principal: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

### Adicionar Campos
1. Modifique a estrutura da tabela em `init_db()`
2. Atualize os formulários HTML
3. Ajuste as rotas no `app.py`

### Novos Módulos
1. Crie novas tabelas no banco
2. Adicione rotas no `app.py`
3. Crie templates HTML
4. Adicione links no menu lateral

## Tecnologias Utilizadas

- **Backend**: Python 3.7+, Flask 2.3+
- **Banco de Dados**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Estilo**: CSS customizado com gradients e glassmorphism
- **Ícones**: Font Awesome 6.0
- **Fontes**: Google Fonts (Inter)

## Troubleshooting

### Erro de Banco de Dados
- Certifique-se de que o arquivo `sistema.db` tem permissões de escrita
- Delete o arquivo `sistema.db` para recriar o banco

### Erro de Dependências
```bash
pip install --upgrade -r requirements.txt
```

### Porta em Uso
- Mude a porta no final do arquivo `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## Suporte

Para dúvidas e suporte:
1. Verifique se todas as dependências estão instaladas
2. Confirme se o Python 3.7+ está sendo usado
3. Verifique as permissões de arquivo no diretório

## Licença

Este projeto é fornecido como está, para uso educacional e comercial.