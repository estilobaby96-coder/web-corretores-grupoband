#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir/atualizar senha do corretor
"""

import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'grupoband',
    'user': 'postgres',
    'password': 'julio'
}

def listar_corretores():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nome, senha FROM corretores")
    corretores = cursor.fetchall()
    print("\n=== CORRETORES CADASTRADOS ===")
    for c in corretores:
        print(f"ID: {c[0]} | Username: {c[1]} | Nome: {c[2]}")
        print(f"   Senha hash: {c[3][:50]}...")
    cursor.close()
    conn.close()
    return corretores

def atualizar_senha(username, nova_senha):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    senha_hash = generate_password_hash(nova_senha)
    print(f"\nNovo hash gerado: {senha_hash[:50]}...")
    
    cursor.execute(
        "UPDATE corretores SET senha = %s WHERE username = %s",
        (senha_hash, username)
    )
    conn.commit()
    
    # Verificar
    cursor.execute("SELECT senha FROM corretores WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        print(f"Verificando senha...")
        if check_password_hash(result[0], nova_senha):
            print(f"✓ Senha atualizada com sucesso para '{username}'!")
            print(f"  Nova senha: {nova_senha}")
        else:
            print("ERRO: Verificação falhou!")
    
    cursor.close()
    conn.close()

def verificar_ativo(username):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nome, ativo FROM corretores WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        print(f"\nCorretor encontrado: {result[2]}")
        print(f"Ativo: {result[3]}")
        if not result[3]:
            print("Ativando corretor...")
            cursor.execute("UPDATE corretores SET ativo = true WHERE username = %s", (username,))
            conn.commit()
            print("✓ Corretor ativado!")
    else:
        print(f"Corretor '{username}' não encontrado!")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print("="*50)
    print("CORREÇÃO DE SENHA - Portal Corretores")
    print("="*50)
    
    listar_corretores()
    
    print("\n--- Verificando e ativando corretor ---")
    verificar_ativo('fredsonmesquita@grupoband.com')
    
    print("\n--- Atualizando senha do corretor ---")
    atualizar_senha('fredsonmesquita@grupoband.com', '123456789')
    
    print("\n" + "="*50)
    print("CONCLUÍDO!")
    print("="*50)
