import sqlite3

NOME_BANCO = "biblioteca.db"


def conectar_banco():
    conn = sqlite3.connect(NOME_BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas():
    """Cria as tabelas caso ainda não existam (não altera dados existentes)."""
    conn = conectar_banco()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS autores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nacionalidade TEXT
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                ano INTEGER,
                autor_id INTEGER NOT NULL,
                FOREIGN KEY (autor_id) REFERENCES autores (id)
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'usuario'
            )""")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()