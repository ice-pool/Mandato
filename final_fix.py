# final_fix.py - Execute este script para corrigir definitivamente o banco
import sqlite3

def fix_database():
    """Corrigir banco de dados para funcionar com o novo sistema"""
    
    DATABASE = 'sistema.db'
    conn = sqlite3.connect(DATABASE)
    
    try:
        print("🔧 Iniciando correção do banco de dados...")
        
        # 1. Verificar e adicionar coluna 'ativo' na tabela usuarios
        cursor = conn.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ativo' not in columns:
            print("📝 Adicionando coluna 'ativo' à tabela usuarios...")
            conn.execute('ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN DEFAULT 1')
            conn.execute('UPDATE usuarios SET ativo = 1')
            print("✅ Coluna 'ativo' adicionada!")
        else:
            print("✅ Coluna 'ativo' já existe")
        
        # 2. Verificar e criar tabela usuario_permissoes
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario_permissoes'")
        if not cursor.fetchone():
            print("📝 Criando tabela usuario_permissoes...")
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
            print("✅ Tabela usuario_permissoes criada!")
        else:
            print("✅ Tabela usuario_permissoes já existe")
        
        # 3. Verificar outras colunas na tabela emendas
        cursor = conn.execute("PRAGMA table_info(emendas)")
        emendas_columns = [column[1] for column in cursor.fetchall()]
        
        if 'cidade' not in emendas_columns:
            print("📝 Adicionando coluna 'cidade' à tabela emendas...")
            conn.execute('ALTER TABLE emendas ADD COLUMN cidade TEXT')
            print("✅ Coluna 'cidade' adicionada!")
        else:
            print("✅ Coluna 'cidade' já existe na tabela emendas")
        
        if 'quem_vai_executar' not in emendas_columns:
            print("📝 Adicionando coluna 'quem_vai_executar' à tabela emendas...")
            conn.execute('ALTER TABLE emendas ADD COLUMN quem_vai_executar TEXT')
            print("✅ Coluna 'quem_vai_executar' adicionada!")
        else:
            print("✅ Coluna 'quem_vai_executar' já existe na tabela emendas")
        
        # 4. Verificar se existe pelo menos um usuário ativo
        usuarios = conn.execute('SELECT COUNT(*) as total FROM usuarios WHERE ativo = 1').fetchone()
        if usuarios['total'] == 0:
            print("⚠️ Nenhum usuário ativo encontrado. Ativando todos os usuários...")
            conn.execute('UPDATE usuarios SET ativo = 1')
            print("✅ Usuários ativados!")
        
        conn.commit()
        print("\n🎉 Banco de dados corrigido com sucesso!")
        print("\n📋 O que foi feito:")
        print("   ✅ Coluna 'ativo' adicionada à tabela usuarios")
        print("   ✅ Tabela 'usuario_permissoes' verificada/criada")
        print("   ✅ Colunas extras da tabela emendas verificadas")
        print("   ✅ Usuários existentes marcados como ativos")
        print("\n🚀 Agora você pode executar seu app.py normalmente!")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()