#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar a tabela de corretores no banco de dados
Execute este script uma vez para configurar o banco de dados
"""

import psycopg2
from werkzeug.security import generate_password_hash

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'grupoband',
    'user': 'postgres',
    'password': 'julio'
}

def criar_tabela_corretores():
    """
    Cria a tabela de corretores se não existir
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Criar tabela de corretores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corretores (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            telefone VARCHAR(20),
            tipo VARCHAR(20) DEFAULT 'corretor',
            ativo BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✓ Tabela 'corretores' criada com sucesso!")
    
    cursor.close()
    conn.close()

def criar_corretor_admin():
    """
    Cria um corretor administrador padrão
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Verificar se já existe
    cursor.execute("SELECT id FROM corretores WHERE username = 'admin'")
    if cursor.fetchone():
        print("! Usuário 'admin' já existe.")
    else:
        # Criar usuário admin
        senha_hash = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO corretores (username, senha, nome, email, tipo)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', senha_hash, 'Administrador', 'admin@grupoband.com', 'admin'))
        conn.commit()
        print("✓ Usuário 'admin' criado com sucesso!")
        print("  Username: admin")
        print("  Senha: admin123")
    
    cursor.close()
    conn.close()

def criar_corretor_teste():
    """
    Cria um corretor de teste
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Verificar se já existe
    cursor.execute("SELECT id FROM corretores WHERE username = 'corretor1'")
    if cursor.fetchone():
        print("! Usuário 'corretor1' já existe.")
    else:
        # Criar corretor teste
        senha_hash = generate_password_hash('corretor123')
        cursor.execute("""
            INSERT INTO corretores (username, senha, nome, email, tipo)
            VALUES (%s, %s, %s, %s, %s)
        """, ('corretor1', senha_hash, 'João Silva', 'joao@grupoband.com', 'corretor'))
        conn.commit()
        print("✓ Usuário 'corretor1' criado com sucesso!")
        print("  Username: corretor1")
        print("  Senha: corretor123")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print("="*50)
    print("CONFIGURAÇÃO DO BANCO DE DADOS")
    print("Portal Web Corretores - Grupo Bandeirantes")
    print("="*50)
    print()
    
    try:
        criar_tabela_corretores()
        criar_corretor_admin()
        criar_corretor_teste()
        
        print()
        print("="*50)
        print("CONFIGURAÇÃO CONCLUÍDA!")
        print("="*50)
        print()
        print("Agora você pode executar o portal com:")
        print("  python app.py")
        print()
        print("Acesse: http://localhost:5000")
        print()
    except Exception as e:
        print(f"ERRO: {e}")
