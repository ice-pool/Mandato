# app.py - Arquivo principal da aplicação
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Mude para uma chave mais segura em produção

# Dados dos usuários (em produção, use um banco de dados)
users = {
    'admin': generate_password_hash('admin'),
    'usuario': generate_password_hash('admin123')
}

# Template HTML principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Gestão</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
        }

        /* Sidebar */
        .sidebar {
            width: 250px;
            background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            left: 0;
            top: 0;
            transition: all 0.3s ease;
        }

        .sidebar-header {
            padding: 30px 20px;
            border-bottom: 1px solid #34495e;
            text-align: center;
        }

        .sidebar-header h2 {
            color: #ecf0f1;
            font-size: 24px;
            font-weight: 300;
        }

        .sidebar-menu {
            padding: 20px 0;
        }

        .menu-item {
            display: block;
            padding: 15px 25px;
            color: #bdc3c7;
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
            font-size: 16px;
        }

        .menu-item:hover, .menu-item.active {
            background: rgba(52, 152, 219, 0.1);
            color: #3498db;
            border-left-color: #3498db;
            transform: translateX(5px);
        }

        .menu-item i {
            margin-right: 12px;
            width: 20px;
        }

        .logout-btn {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            padding: 12px;
            background: #e74c3c;
            color: white;
            text-decoration: none;
            text-align: center;
            border-radius: 5px;
            transition: background 0.3s ease;
        }

        .logout-btn:hover {
            background: #c0392b;
        }

        /* Main Content */
        .main-content {
            margin-left: 250px;
            flex: 1;
            padding: 30px;
            background: rgba(255, 255, 255, 0.95);
            min-height: 100vh;
        }

        .page-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
        }

        .page-title {
            font-size: 32px;
            color: #2c3e50;
            font-weight: 300;
        }

        .content-card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        /* Login Page */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .login-form {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }

        .login-form h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #2c3e50;
            font-weight: 300;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #3498db;
        }

        .btn-login {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .btn-login:hover {
            transform: translateY(-2px);
        }

        .btn-primary {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s ease;
            margin-right: 10px;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            color: white;
            text-decoration: none;
        }

        .btn-danger {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s ease;
            font-size: 14px;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            color: white;
            text-decoration: none;
        }

        .btn-success {
            background: linear-gradient(135deg, #27ae60, #229954);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s ease;
        }

        .btn-success:hover {
            transform: translateY(-2px);
            color: white;
            text-decoration: none;
        }

        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .user-table th,
        .user-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }

        .user-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }

        .user-table tbody tr:hover {
            background: #f8f9fa;
        }

        .form-inline {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .form-inline .form-group {
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 10px;
        }

        .form-inline input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }

        .form-inline input:focus {
            outline: none;
            border-color: #3498db;
        }

        .alert-success {
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 5px;
            background: #d1eddd;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert {
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 5px;
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .main-content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    {% if session.logged_in %}
    <div class="sidebar">
        <div class="sidebar-header">
            <h2>Sistema</h2>
        </div>
        <nav class="sidebar-menu">
            <a href="{{ url_for('agenda') }}" class="menu-item {{ 'active' if request.endpoint == 'agenda' }}">
                📅 Agenda
            </a>
            <a href="{{ url_for('contatos') }}" class="menu-item {{ 'active' if request.endpoint == 'contatos' }}">
                👥 Contatos
            </a>
            <a href="{{ url_for('emendas') }}" class="menu-item {{ 'active' if request.endpoint == 'emendas' }}">
                📋 Emendas
            </a>
            <a href="{{ url_for('demandas') }}" class="menu-item {{ 'active' if request.endpoint == 'demandas' }}">
                📊 Demandas
            </a>
            <a href="{{ url_for('usuarios') }}" class="menu-item {{ 'active' if request.endpoint == 'usuarios' }}">
                👤 Usuários
            </a>
        </nav>
        <a href="{{ url_for('logout') }}" class="logout-btn">Sair</a>
    </div>

    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">{{ page_title }}</h1>
        </div>
        
        <div class="content-card">
            {{ content | safe }}
        </div>
    </div>
    {% else %}
    <div class="login-container">
        <form method="POST" class="login-form">
            <h2>Login do Sistema</h2>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert {% if category == 'success' %}alert-success{% else %}alert{% endif %}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="form-group">
                <label for="username">Usuário:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Senha:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">Entrar</button>
            
            <div style="margin-top: 20px; font-size: 14px; color: #666; text-align: center;">
                <strong>Usuários de teste:</strong><br>
                admin / admin<br>
                usuario / admin123
            </div>
        </form>
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('agenda'))
        else:
            flash('Usuário ou senha incorretos!')
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/agenda')
@login_required
def agenda():
    content = """
    <h3>📅 Agenda de Compromissos</h3>
    <p>Bem-vindo à seção de Agenda! Aqui você pode gerenciar seus compromissos e eventos.</p>
    
    <div style="margin-top: 30px;">
        <h4>Próximos Compromissos:</h4>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 15px;">
            <div style="border-left: 4px solid #3498db; padding-left: 15px; margin-bottom: 15px;">
                <strong>Reunião com a equipe</strong><br>
                <small style="color: #666;">Hoje, 14:00 - Sala de Conferências</small>
            </div>
            <div style="border-left: 4px solid #e74c3c; padding-left: 15px; margin-bottom: 15px;">
                <strong>Apresentação do projeto</strong><br>
                <small style="color: #666;">Amanhã, 09:30 - Auditório Principal</small>
            </div>
            <div style="border-left: 4px solid #f39c12; padding-left: 15px;">
                <strong>Revisão mensal</strong><br>
                <small style="color: #666;">Sexta-feira, 16:00 - Online</small>
            </div>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, page_title="Agenda", content=content)

@app.route('/contatos')
@login_required
def contatos():
    content = """
    <h3>👥 Gerenciamento de Contatos</h3>
    <p>Gerencie todos os seus contatos importantes em um só lugar.</p>
    
    <div style="margin-top: 30px;">
        <h4>Contatos Recentes:</h4>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 15px;">
            <div style="display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #dee2e6;">
                <div style="width: 50px; height: 50px; background: #3498db; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 15px;">
                    JS
                </div>
                <div>
                    <strong>João Silva</strong><br>
                    <small style="color: #666;">joao.silva@email.com | (11) 99999-9999</small>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #dee2e6;">
                <div style="width: 50px; height: 50px; background: #e74c3c; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 15px;">
                    MO
                </div>
                <div>
                    <strong>Maria Oliveira</strong><br>
                    <small style="color: #666;">maria.oliveira@email.com | (11) 88888-8888</small>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 15px;">
                <div style="width: 50px; height: 50px; background: #f39c12; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 15px;">
                    PS
                </div>
                <div>
                    <strong>Pedro Santos</strong><br>
                    <small style="color: #666;">pedro.santos@email.com | (11) 77777-7777</small>
                </div>
            </div>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, page_title="Contatos", content=content)

@app.route('/emendas')
@login_required
def emendas():
    content = """
    <h3>📋 Controle de Emendas</h3>
    <p>Acompanhe o status e progresso das emendas parlamentares.</p>
    
    <div style="margin-top: 30px;">
        <h4>Emendas em Andamento:</h4>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 15px;">
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #27ae60;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <strong>Emenda Nº 2024/001 - Saúde Pública</strong>
                    <span style="background: #27ae60; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">APROVADA</span>
                </div>
                <p style="color: #666; margin-bottom: 10px;">Recursos para ampliação de UBS no município</p>
                <small style="color: #888;">Valor: R$ 2.500.000,00 | Prazo: 30/06/2025</small>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #f39c12;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <strong>Emenda Nº 2024/002 - Educação</strong>
                    <span style="background: #f39c12; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">ANÁLISE</span>
                </div>
                <p style="color: #666; margin-bottom: 10px;">Construção de creche municipal</p>
                <small style="color: #888;">Valor: R$ 1.800.000,00 | Prazo: 15/08/2025</small>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <strong>Emenda Nº 2024/003 - Infraestrutura</strong>
                    <span style="background: #3498db; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">TRAMITANDO</span>
                </div>
                <p style="color: #666; margin-bottom: 10px;">Pavimentação de vias urbanas</p>
                <small style="color: #888;">Valor: R$ 3.200.000,00 | Prazo: 20/09/2025</small>
            </div>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, page_title="Emendas", content=content)

@app.route('/demandas')
@login_required
def demandas():
    content = """
    <h3>📊 Gestão de Demandas</h3>
    <p>Controle e acompanhamento de todas as demandas recebidas.</p>
    
    <div style="margin-top: 30px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div style="background: #3498db; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin: 0; font-size: 36px;">47</h2>
                <p style="margin: 5px 0 0 0;">Total de Demandas</p>
            </div>
            <div style="background: #27ae60; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin: 0; font-size: 36px;">23</h2>
                <p style="margin: 5px 0 0 0;">Resolvidas</p>
            </div>
            <div style="background: #f39c12; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin: 0; font-size: 36px;">18</h2>
                <p style="margin: 5px 0 0 0;">Em Andamento</p>
            </div>
            <div style="background: #e74c3c; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin: 0; font-size: 36px;">6</h2>
                <p style="margin: 5px 0 0 0;">Pendentes</p>
            </div>
        </div>
        
        <h4>Demandas Recentes:</h4>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 15px;">
            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #e74c3c;">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div>
                        <strong>Demanda #2024-089</strong> - Iluminação Pública<br>
                        <small style="color: #666;">Rua das Flores, 123 | Solicitante: Ana Costa</small>
                    </div>
                    <span style="background: #e74c3c; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">URGENTE</span>
                </div>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #f39c12;">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div>
                        <strong>Demanda #2024-088</strong> - Buraco na Via<br>
                        <small style="color: #666;">Av. Principal, 456 | Solicitante: Carlos Lima</small>
                    </div>
                    <span style="background: #f39c12; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">PROGRESSO</span>
                </div>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div>
                        <strong>Demanda #2024-087</strong> - Poda de Árvore<br>
                        <small style="color: #666;">Rua Verde, 789 | Solicitante: Maria Silva</small>
                    </div>
                    <span style="background: #27ae60; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">CONCLUÍDA</span>
                </div>
            </div>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, page_title="Demandas", content=content)

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        if not username or not password:
            flash('Usuário e senha são obrigatórios!', 'error')
        elif username in users:
            flash('Usuário já existe!', 'error')
        else:
            users[username] = generate_password_hash(password)
            flash(f'Usuário "{username}" criado com sucesso!', 'success')
    
    users_list = []
    for username in users.keys():
        users_list.append({
            'username': username,
            'can_delete': username != session.get('username')  # Não pode deletar a si mesmo
        })
    
    content = f"""
    <h3>👤 Gerenciamento de Usuários</h3>
    <p>Adicione ou remova usuários do sistema.</p>
    
    <div class="form-inline">
        <h4 style="margin-bottom: 20px;">Adicionar Novo Usuário</h4>
        <form method="POST" style="display: flex; align-items: end; gap: 15px; flex-wrap: wrap;">
            <div class="form-group">
                <label for="username" style="display: block; margin-bottom: 5px; font-weight: 500;">Usuário:</label>
                <input type="text" id="username" name="username" required placeholder="Digite o usuário">
            </div>
            <div class="form-group">
                <label for="password" style="display: block; margin-bottom: 5px; font-weight: 500;">Senha:</label>
                <input type="password" id="password" name="password" required placeholder="Digite a senha">
            </div>
            <div class="form-group">
                <button type="submit" class="btn-success">
                    ➕ Adicionar Usuário
                </button>
            </div>
        </form>
    </div>
    
    <h4>Usuários Cadastrados</h4>
    <table class="user-table">
        <thead>
            <tr>
                <th>👤 Usuário</th>
                <th>📅 Status</th>
                <th>⚙️ Ações</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for user in users_list:
        status_badge = '🟢 Ativo' if user['username'] == session.get('username') else '🔵 Ativo'
        delete_button = ''
        if user['can_delete']:
            delete_button = f'''
                <a href="/delete_user/{user['username']}" 
                   class="btn-danger" 
                   onclick="return confirm('Tem certeza que deseja excluir o usuário {user['username']}?')">
                    🗑️ Excluir
                </a>
            '''
        else:
            delete_button = '<span style="color: #999; font-size: 12px;">Usuário atual</span>'
            
        content += f"""
            <tr>
                <td><strong>{user['username']}</strong></td>
                <td>{status_badge}</td>
                <td>{delete_button}</td>
            </tr>
        """
    
    content += """
        </tbody>
    </table>
    
    <div style="margin-top: 30px; padding: 20px; background: #e8f4f8; border-radius: 8px; border-left: 4px solid #3498db;">
        <h5 style="margin: 0 0 10px 0; color: #2c3e50;">💡 Dicas de Segurança:</h5>
        <ul style="margin: 0; color: #555;">
            <li>Use senhas fortes com pelo menos 8 caracteres</li>
            <li>Evite usar informações pessoais nas senhas</li>
            <li>Remova usuários que não precisam mais de acesso</li>
            <li>Você não pode excluir seu próprio usuário</li>
        </ul>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE, page_title="Usuários", content=content)

@app.route('/delete_user/<username>')
@login_required
def delete_user(username):
    if username == session.get('username'):
        flash('Você não pode excluir seu próprio usuário!', 'error')
    elif username not in users:
        flash('Usuário não encontrado!', 'error')
    else:
        del users[username]
        flash(f'Usuário "{username}" excluído com sucesso!', 'success')
    
    return redirect(url_for('usuarios'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)