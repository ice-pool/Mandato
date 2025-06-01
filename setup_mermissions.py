# setup_permissions.py - Execute para configurar o sistema de permissões
import sqlite3
from werkzeug.security import generate_password_hash

def setup_permission_system():
    """Configurar o sistema de permissões completo"""
    
    DATABASE = 'sistema.db'
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    try:
        print("🚀 Configurando sistema de permissões...")
        
        # 1. Adicionar coluna 'ativo' se não existir
        cursor = conn.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ativo' not in columns:
            print("📝 Adicionando coluna 'ativo'...")
            conn.execute('ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN DEFAULT 1')
            conn.execute('UPDATE usuarios SET ativo = 1')
            print("✅ Coluna 'ativo' adicionada!")
        
        # 2. Criar tabela de permissões
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario_permissoes'")
        if not cursor.fetchone():
            print("📝 Criando tabela de permissões...")
            conn.execute('''
                CREATE TABLE usuario_permissoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    modulo TEXT NOT NULL,
                    pode_ver BOOLEAN DEFAULT FALSE,
                    pode_adicionar BOOLEAN DEFAULT FALSE,
                    pode_editar BOOLEAN DEFAULT FALSE,
                    pode_excluir BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                    UNIQUE(usuario_id, modulo)
                )
            ''')
            print("✅ Tabela de permissões criada!")
        
        # 3. Verificar/Criar usuário admin
        admin_user = conn.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',)).fetchone()
        
        if not admin_user:
            print("👤 Criando usuário administrador...")
            hashed_password = generate_password_hash('admin123')
            cursor = conn.execute('''
                INSERT INTO usuarios (username, password, nome, email, ativo) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', hashed_password, 'Administrador', 'admin@sistema.com', True))
            admin_id = cursor.lastrowid
            print("✅ Usuário admin criado!")
        else:
            admin_id = admin_user['id']
            print("✅ Usuário admin já existe")
        
        # 4. Configurar permissões do admin
        modulos = ['agenda', 'contatos', 'emendas', 'demandas', 'cidades', 'grupos', 'usuarios']
        
        for modulo in modulos:
            conn.execute('''
                INSERT OR REPLACE INTO usuario_permissoes 
                (usuario_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, modulo, True, True, True, True))
        
        print(f"✅ Permissões do admin configuradas para {len(modulos)} módulos")
        
        # 5. Configurar permissões básicas para outros usuários
        other_users = conn.execute('''
            SELECT id, username FROM usuarios WHERE username != ?
        ''', ('admin',)).fetchall()
        
        if other_users:
            print(f"👥 Configurando permissões básicas para {len(other_users)} usuário(s)...")
            
            for user in other_users:
                user_id = user['id']
                username = user['username']
                print(f"   - Configurando permissões para: {username}")
                
                for modulo in modulos:
                    # Verificar se já tem permissões
                    existing = conn.execute('''
                        SELECT id FROM usuario_permissoes 
                        WHERE usuario_id = ? AND modulo = ?
                    ''', (user_id, modulo)).fetchone()
                    
                    if not existing:
                        # Dar permissões básicas (apenas visualização, exceto para módulo usuários)
                        pode_ver = True if modulo != 'usuarios' else False
                        
                        conn.execute('''
                            INSERT INTO usuario_permissoes 
                            (usuario_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (user_id, modulo, pode_ver, False, False, False))
        
        conn.commit()
        
        print("\n🎉 Sistema de permissões configurado com sucesso!")
        print("\n📋 Resumo:")
        print("✅ Coluna 'ativo' adicionada à tabela usuarios")
        print("✅ Tabela 'usuario_permissoes' criada")
        print("✅ Usuário admin com todas as permissões")
        print("✅ Outros usuários com permissões básicas")
        
        print("\n🔑 Credenciais do Administrador:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
        print("\n📌 Próximos passos:")
        print("1. Faça login como admin")
        print("2. Vá em 'Usuários' para gerenciar permissões")
        print("3. Edite cada usuário para definir suas permissões específicas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    setup_permission_system()