
    # migration.py - Execute este script ANTES de rodar o app.py atualizado
import sqlite3
from werkzeug.security import generate_password_hash

def migrate_database():
    """Migrar banco de dados existente para suportar sistema de permissões"""
    
    DATABASE = 'sistema.db'
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    print("Iniciando migração do banco de dados...")
    
    try:
        # 1. Verificar se a coluna 'ativo' existe na tabela usuarios
        cursor = conn.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ativo' not in columns:
            print("Adicionando coluna 'ativo' à tabela usuarios...")
            conn.execute('ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN DEFAULT TRUE')
            # Ativar todos os usuários existentes
            conn.execute('UPDATE usuarios SET ativo = 1 WHERE ativo IS NULL')
            print("✅ Coluna 'ativo' adicionada com sucesso!")
        else:
            print("✅ Coluna 'ativo' já existe na tabela usuarios")
        
        # 2. Verificar se a tabela usuario_permissoes existe
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario_permissoes'")
        if not cursor.fetchone():
            print("Criando tabela usuario_permissoes...")
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
            print("✅ Tabela usuario_permissoes criada com sucesso!")
        else:
            print("✅ Tabela usuario_permissoes já existe")
        
        # 3. Verificar se o usuário admin existe
        admin_user = conn.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',)).fetchone()
        
        if not admin_user:
            print("Criando usuário administrador...")
            hashed_password = generate_password_hash('admin123')
            cursor = conn.execute('INSERT INTO usuarios (username, password, nome, email, ativo) VALUES (?, ?, ?, ?, ?)',
                        ('admin', hashed_password, 'Administrador', 'admin@sistema.com', True))
            admin_id = cursor.lastrowid
            print("✅ Usuário admin criado!")
        else:
            admin_id = admin_user['id']
            print("✅ Usuário admin já existe")
        
        # 4. Definir permissões do admin
        modulos = ['agenda', 'contatos', 'emendas', 'demandas', 'cidades', 'grupos', 'usuarios']
        
        for modulo in modulos:
            # Verificar se a permissão já existe
            existing_perm = conn.execute('''
                SELECT id FROM usuario_permissoes 
                WHERE usuario_id = ? AND modulo = ?
            ''', (admin_id, modulo)).fetchone()
            
            if not existing_perm:
                conn.execute('''
                    INSERT INTO usuario_permissoes (usuario_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (admin_id, modulo, True, True, True, True))
                print(f"✅ Permissões do admin para '{modulo}' configuradas")
            else:
                # Atualizar permissões existentes para garantir que o admin tenha todas
                conn.execute('''
                    UPDATE usuario_permissoes 
                    SET pode_ver = ?, pode_adicionar = ?, pode_editar = ?, pode_excluir = ?
                    WHERE usuario_id = ? AND modulo = ?
                ''', (True, True, True, True, admin_id, modulo))
                print(f"✅ Permissões do admin para '{modulo}' atualizadas")
        
        # 5. Para outros usuários existentes, dar permissões básicas
        other_users = conn.execute('SELECT id FROM usuarios WHERE username != ?', ('admin',)).fetchall()
        
        for user in other_users:
            user_id = user['id']
            print(f"Configurando permissões básicas para usuário ID {user_id}...")
            
            for modulo in modulos:
                # Verificar se já tem permissões
                existing_perm = conn.execute('''
                    SELECT id FROM usuario_permissoes 
                    WHERE usuario_id = ? AND modulo = ?
                ''', (user_id, modulo)).fetchone()
                
                if not existing_perm:
                    # Dar apenas permissão de visualização por padrão (exceto usuários)
                    pode_ver = True if modulo != 'usuarios' else False
                    conn.execute('''
                        INSERT INTO usuario_permissoes (usuario_id, modulo, pode_ver, pode_adicionar, pode_editar, pode_excluir)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, modulo, pode_ver, False, False, False))
        
        # 6. Verificar outras colunas que podem estar faltando
        
        # Verificar coluna 'cidade' na tabela emendas
        cursor = conn.execute("PRAGMA table_info(emendas)")
        emendas_columns = [column[1] for column in cursor.fetchall()]
        
        if 'cidade' not in emendas_columns:
            print("Adicionando coluna 'cidade' à tabela emendas...")
            conn.execute('ALTER TABLE emendas ADD COLUMN cidade TEXT')
            print("✅ Coluna 'cidade' adicionada à tabela emendas!")
        
        if 'quem_vai_executar' not in emendas_columns:
            print("Adicionando coluna 'quem_vai_executar' à tabela emendas...")
            conn.execute('ALTER TABLE emendas ADD COLUMN quem_vai_executar TEXT')
            print("✅ Coluna 'quem_vai_executar' adicionada à tabela emendas!")
        
        conn.commit()
        print("\n🎉 Migração concluída com sucesso!")
        print("\nCredenciais do administrador:")
        print("Usuário: admin")
        print("Senha: admin123")
        print("\nAgora você pode executar o app.py atualizado.")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()