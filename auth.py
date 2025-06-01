# auth.py - Sistema de autenticação e permissões

import sqlite3
import hashlib
from functools import wraps
from flask import session, flash, redirect, url_for, request, g

# Configuração do banco
DATABASE = 'sistema.db'

def conectar_db():
    """Conecta ao banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """Obtém conexão do banco para o contexto da aplicação"""
    if 'db' not in g:
        g.db = conectar_db()
    return g.db

def close_db():
    """Fecha a conexão do banco"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Funções de autenticação
def hash_password(password):
    """Gera hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    """Verifica login do usuário"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    cursor.execute('''
        SELECT id, username, nome, email, ativo 
        FROM usuarios 
        WHERE username = ? AND password = ? AND ativo = 1
    ''', (username, password_hash))
    
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {
            'id': usuario['id'],
            'username': usuario['username'],
            'nome': usuario['nome'],
            'email': usuario['email']
        }
    return None

def obter_permissoes_usuario(user_id):
    """Obtém todas as permissões do usuário"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir 
        FROM permissoes_usuarios 
        WHERE user_id = ? AND ativo = 1
    ''', (user_id,))
    
    permissoes = {}
    for row in cursor.fetchall():
        permissoes[row['modulo']] = {
            'pode_ver': bool(row['pode_ver']),
            'pode_adicionar': bool(row['pode_adicionar']),
            'pode_editar': bool(row['pode_editar']),
            'pode_excluir': bool(row['pode_excluir'])
        }
    
    conn.close()
    return permissoes

def tem_permissao(modulo, acao='ver'):
    """Verifica se o usuário atual tem permissão específica"""
    if 'user_id' not in session:
        return False
    
    permissoes = obter_permissoes_usuario(session['user_id'])
    
    if modulo not in permissoes:
        return False
    
    chave_acao = f'pode_{acao}'
    return permissoes[modulo].get(chave_acao, False)

# Decoradores de proteção
def login_required(f):
    """Decorador para exigir login"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def verificar_permissao(modulo, acao='ver'):
    """Decorador para verificar permissões específicas"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Primeiro verifica se está logado
            if 'user_id' not in session:
                flash('Acesso negado. Faça login primeiro.', 'error')
                return redirect(url_for('login'))
            
            # Verifica permissão específica
            if not tem_permissao(modulo, acao):
                flash(f'Você não tem permissão para {acao} no módulo {modulo}.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Funções para gerenciar usuários
def criar_usuario(username, nome, email, password, permissoes_dict):
    """Cria novo usuário com permissões"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        # Verificar se username já existe
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
        if cursor.fetchone():
            return False, "Nome de usuário já existe"
        
        # Criar usuário
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO usuarios (username, nome, email, password, ativo)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, nome, email, password_hash, True))
        
        user_id = cursor.lastrowid
        
        # Salvar permissões
        salvar_permissoes_usuario(cursor, user_id, permissoes_dict)
        
        conn.commit()
        return True, "Usuário criado com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao criar usuário: {str(e)}"
    
    finally:
        conn.close()

def atualizar_usuario(user_id, username, nome, email, password, ativo, permissoes_dict):
    """Atualiza usuário existente"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        # Verificar se username já existe (exceto para o próprio usuário)
        cursor.execute('SELECT id FROM usuarios WHERE username = ? AND id != ?', (username, user_id))
        if cursor.fetchone():
            return False, "Nome de usuário já existe"
        
        # Atualizar dados básicos
        if password:
            password_hash = hash_password(password)
            cursor.execute('''
                UPDATE usuarios 
                SET username=?, nome=?, email=?, password=?, ativo=?
                WHERE id=?
            ''', (username, nome, email, password_hash, ativo, user_id))
        else:
            cursor.execute('''
                UPDATE usuarios 
                SET username=?, nome=?, email=?, ativo=?
                WHERE id=?
            ''', (username, nome, email, ativo, user_id))
        
        # Remover permissões antigas
        cursor.execute('DELETE FROM permissoes_usuarios WHERE user_id = ?', (user_id,))
        
        # Salvar novas permissões
        salvar_permissoes_usuario(cursor, user_id, permissoes_dict)
        
        conn.commit()
        return True, "Usuário atualizado com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao atualizar usuário: {str(e)}"
    
    finally:
        conn.close()

def salvar_permissoes_usuario(cursor, user_id, permissoes_dict):
    """Salva permissões do usuário"""
    modulos = ['agenda', 'contatos', 'emendas', 'demandas', 'cidades', 'grupos', 'usuarios']
    
    for modulo in modulos:
        pode_ver = permissoes_dict.get(f'{modulo}_ver', False)
        pode_adicionar = permissoes_dict.get(f'{modulo}_adicionar', False)
        pode_editar = permissoes_dict.get(f'{modulo}_editar', False)
        pode_excluir = permissoes_dict.get(f'{modulo}_excluir', False)
        
        # Só salva se tem pelo menos uma permissão
        if any([pode_ver, pode_adicionar, pode_editar, pode_excluir]):
            cursor.execute('''
                INSERT INTO permissoes_usuarios 
                (user_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir, True))

def obter_usuario_por_id(user_id):
    """Obtém dados do usuário por ID"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, nome, email, ativo
        FROM usuarios 
        WHERE id = ?
    ''', (user_id,))
    
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {
            'id': usuario['id'],
            'username': usuario['username'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'ativo': bool(usuario['ativo'])
        }
    return None

def listar_usuarios():
    """Lista todos os usuários"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, nome, email, ativo, data_criacao
        FROM usuarios 
        ORDER BY nome
    ''')
    
    usuarios = []
    for row in cursor.fetchall():
        usuarios.append({
            'id': row['id'],
            'username': row['username'],
            'nome': row['nome'],
            'email': row['email'],
            'ativo': bool(row['ativo']),
            'data_criacao': row['data_criacao']
        })
    
    conn.close()
    return usuarios

def excluir_usuario(user_id):
    """Exclui usuário e suas permissões"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        # Verificar se não é o último admin
        cursor.execute('''
            SELECT COUNT(*) as total_admins
            FROM usuarios u
            JOIN permissoes_usuarios p ON u.id = p.user_id
            WHERE u.ativo = 1 AND p.modulo = 'usuarios' 
            AND p.pode_adicionar = 1 AND p.pode_editar = 1 AND p.pode_excluir = 1
        ''')
        
        total_admins = cursor.fetchone()['total_admins']
        
        # Verificar se o usuário a ser excluído é admin
        cursor.execute('''
            SELECT COUNT(*) as eh_admin
            FROM permissoes_usuarios 
            WHERE user_id = ? AND modulo = 'usuarios' 
            AND pode_adicionar = 1 AND pode_editar = 1 AND pode_excluir = 1
        ''', (user_id,))
        
        eh_admin = cursor.fetchone()['eh_admin'] > 0
        
        if eh_admin and total_admins <= 1:
            return False, "Não é possível excluir o último administrador do sistema"
        
        # Excluir usuário (as permissões serão excluídas automaticamente por CASCADE)
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
        
        if cursor.rowcount == 0:
            return False, "Usuário não encontrado"
        
        conn.commit()
        return True, "Usuário excluído com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao excluir usuário: {str(e)}"
    
    finally:
        conn.close()