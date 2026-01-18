#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurações do Portal Web Corretores - GrupoBand
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (se existir)
load_dotenv()


class Config:
    """
    Configurações da aplicação
    """
    # Chave secreta para sessões
    SECRET_KEY = os.environ.get('SECRET_KEY', 'grupoband-secret-key-2024')
    
    # Configurações do banco de dados PostgreSQL
    # Railway fornece DATABASE_URL automaticamente
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Se DATABASE_URL existir, usar ela; senão usar configurações locais
    if DATABASE_URL:
        # Railway usa postgres:// mas psycopg2 precisa de postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        
        # Extrair componentes da URL para uso direto com psycopg2
        import urllib.parse
        result = urllib.parse.urlparse(DATABASE_URL)
        DB_HOST = result.hostname
        DB_PORT = str(result.port) if result.port else '5432'
        DB_NAME = result.path[1:]  # Remove a barra inicial
        DB_USER = result.username
        DB_PASSWORD = result.password
    else:
        # Configurações locais (desenvolvimento)
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_NAME = os.environ.get('DB_NAME', 'grupoband')
        DB_USER = os.environ.get('DB_USER', 'postgres')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'julio')
        
        SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações da aplicação
    APP_NAME = 'Portal Corretores'
    APP_VERSION = '1.0.0'
    COMPANY_NAME = 'Grupo Bandeirantes - Imobiliária'
