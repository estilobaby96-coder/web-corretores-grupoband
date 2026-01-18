#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerenciador de Banco de Dados - Portal Web Corretores
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config


class DatabaseManager:
    """
    Gerenciador de conexão com o banco de dados PostgreSQL
    """
    
    def __init__(self):
        self.config = Config()
        self.connection = None
    
    def connect(self):
        """
        Estabelece conexão com o banco de dados
        """
        try:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        """
        Fecha a conexão com o banco de dados
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """
        Executa uma query e retorna os resultados
        """
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Erro na query: {e}")
            # Fazer rollback para limpar o estado da transação
            if self.connection:
                self.connection.rollback()
            return []
    
    # ==================== CORRETORES ====================
    
    def get_corretor_by_username(self, username):
        """
        Busca um corretor pelo username
        """
        query = """
            SELECT * FROM corretores 
            WHERE username = %s AND ativo = true
        """
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def get_corretor_by_id(self, corretor_id):
        """
        Busca um corretor pelo ID
        """
        query = "SELECT * FROM corretores WHERE id = %s"
        result = self.execute_query(query, (corretor_id,))
        return result[0] if result else None
    
    # ==================== LOTEAMENTOS ====================
    
    def get_loteamentos(self):
        """
        Retorna todos os loteamentos
        """
        query = """
            SELECT id, nome
            FROM loteamentos 
            ORDER BY nome
        """
        return self.execute_query(query)
    
    def get_loteamento_by_id(self, loteamento_id):
        """
        Retorna um loteamento pelo ID
        """
        query = "SELECT * FROM loteamentos WHERE id = %s"
        result = self.execute_query(query, (loteamento_id,))
        return result[0] if result else None
    
    # ==================== QUADRAS ====================
    
    def get_quadras_by_loteamento(self, loteamento_id):
        """
        Retorna todas as quadras de um loteamento
        """
        query = """
            SELECT id, loteamento_id, numero_quadra
            FROM quadras 
            WHERE loteamento_id = %s 
            ORDER BY numero_quadra
        """
        return self.execute_query(query, (loteamento_id,))
    
    # ==================== LOTES ====================
    
    def get_lotes_by_quadra(self, quadra_id):
        """
        Retorna todos os lotes de uma quadra
        """
        query = """
            SELECT id, quadra_id, numero_lote, metragem, status
            FROM lotes 
            WHERE quadra_id = %s 
            ORDER BY numero_lote
        """
        return self.execute_query(query, (quadra_id,))
    
    def get_lotes_disponiveis_by_quadra(self, quadra_id):
        """
        Retorna apenas os lotes disponíveis de uma quadra
        """
        query = """
            SELECT id, quadra_id, numero_lote, metragem, status
            FROM lotes 
            WHERE quadra_id = %s AND status = 'disponivel'
            ORDER BY numero_lote
        """
        return self.execute_query(query, (quadra_id,))
    
    # ==================== DISPONIBILIDADE COMPLETA ====================
    
    def get_disponibilidade_completa(self, filtros=None):
        """
        Retorna todos os lotes disponíveis com informações completas
        Aceita filtros opcionais
        """
        query = """
            SELECT 
                l.id as lote_id,
                l.numero_lote,
                l.metragem,
                'disponivel' as status,
                q.id as quadra_id,
                q.numero_quadra,
                lot.id as loteamento_id,
                lot.nome as loteamento_nome
            FROM lotes l
            JOIN quadras q ON l.quadra_id = q.id
            JOIN loteamentos lot ON q.loteamento_id = lot.id
            WHERE 1=1
        """
        
        params = []
        
        # Aplicar filtros
        if filtros:
            if filtros.get('loteamento_id'):
                query += " AND lot.id = %s"
                params.append(filtros['loteamento_id'])
            
            if filtros.get('quadra_id'):
                query += " AND q.id = %s"
                params.append(filtros['quadra_id'])
            
            if filtros.get('metragem_min'):
                query += " AND l.metragem >= %s"
                params.append(filtros['metragem_min'])
            
            if filtros.get('metragem_max'):
                query += " AND l.metragem <= %s"
                params.append(filtros['metragem_max'])
        
        query += " ORDER BY lot.nome, q.numero_quadra, l.numero_lote"
        
        return self.execute_query(query, params if params else None)
    
    def get_todos_lotes_por_quadra(self, quadra_id):
        """
        Retorna todos os lotes de uma quadra (para o mapa visual)
        """
        query = """
            SELECT 
                l.id,
                l.numero_lote,
                l.metragem,
                'disponivel' as status,
                q.numero_quadra,
                lot.nome as loteamento_nome
            FROM lotes l
            JOIN quadras q ON l.quadra_id = q.id
            JOIN loteamentos lot ON q.loteamento_id = lot.id
            WHERE q.id = %s
            ORDER BY l.numero_lote
        """
        return self.execute_query(query, (quadra_id,))
    
    # ==================== ESTATÍSTICAS ====================
    
    def get_estatisticas(self):
        """
        Retorna estatísticas gerais de disponibilidade
        """
        stats = {
            'total_loteamentos': 0,
            'total_quadras': 0,
            'total_lotes': 0,
            'lotes_disponiveis': 0,
            'lotes_vendidos': 0,
            'lotes_reservados': 0,
            'metragem_disponivel': 0,
            'percentual_disponivel': 0
        }
        
        try:
            # Total de loteamentos
            query = "SELECT COUNT(*) as total FROM loteamentos"
            result = self.execute_query(query)
            stats['total_loteamentos'] = result[0]['total'] if result else 0
            
            # Total de quadras
            query = "SELECT COUNT(*) as total FROM quadras"
            result = self.execute_query(query)
            stats['total_quadras'] = result[0]['total'] if result else 0
            
            # Total de lotes e metragem
            query = """
                SELECT 
                    COUNT(*) as total,
                    COALESCE(SUM(metragem), 0) as metragem_total
                FROM lotes
            """
            result = self.execute_query(query)
            if result:
                stats['total_lotes'] = result[0]['total'] or 0
                stats['lotes_disponiveis'] = result[0]['total'] or 0
                stats['metragem_disponivel'] = float(result[0]['metragem_total'] or 0)
                stats['percentual_disponivel'] = 100.0 if stats['total_lotes'] > 0 else 0
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
        
        return stats
    
    def get_estatisticas_por_loteamento(self, loteamento_id):
        """
        Retorna estatísticas de um loteamento específico
        """
        query = """
            SELECT 
                COUNT(*) as total_lotes,
                SUM(CASE WHEN l.status = 'disponivel' THEN 1 ELSE 0 END) as disponiveis,
                SUM(CASE WHEN l.status = 'vendido' THEN 1 ELSE 0 END) as vendidos,
                SUM(CASE WHEN l.status = 'reservado' THEN 1 ELSE 0 END) as reservados,
                SUM(CASE WHEN l.status = 'disponivel' THEN l.metragem ELSE 0 END) as metragem_disp,
                COUNT(DISTINCT q.id) as total_quadras
            FROM lotes l
            JOIN quadras q ON l.quadra_id = q.id
            WHERE q.loteamento_id = %s
        """
        result = self.execute_query(query, (loteamento_id,))
        
        if result:
            return {
                'total_lotes': result[0]['total_lotes'] or 0,
                'disponiveis': result[0]['disponiveis'] or 0,
                'vendidos': result[0]['vendidos'] or 0,
                'reservados': result[0]['reservados'] or 0,
                'metragem_disponivel': float(result[0]['metragem_disp'] or 0),
                'total_quadras': result[0]['total_quadras'] or 0
            }
        return None


# Instância global
db = DatabaseManager()
