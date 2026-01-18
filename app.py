#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Portal Web Corretores - Grupo Bandeirantes Imobiliária
Aplicação Flask principal
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from database import db
import json

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'


# ==================== MODELO DE USUÁRIO ====================

class User(UserMixin):
    """
    Classe de usuário para Flask-Login
    """
    def __init__(self, id, username, nome, email, tipo='corretor'):
        self.id = id
        self.username = username
        self.nome = nome
        self.email = email
        self.tipo = tipo


@login_manager.user_loader
def load_user(user_id):
    """
    Carrega usuário pelo ID
    """
    corretor = db.get_corretor_by_id(int(user_id))
    if corretor:
        return User(
            id=corretor['id'],
            username=corretor['username'],
            nome=corretor['nome'],
            email=corretor.get('email', ''),
            tipo=corretor.get('tipo', 'corretor')
        )
    return None


# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/')
def index():
    """
    Página inicial - redireciona para login ou dashboard
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        # Buscar corretor no banco
        corretor = db.get_corretor_by_username(username)
        print(f"DEBUG: Buscando usuario '{username}'")
        print(f"DEBUG: Corretor encontrado: {corretor}")
        
        if corretor:
            print(f"DEBUG: Verificando senha...")
            senha_ok = check_password_hash(corretor['senha'], password)
            print(f"DEBUG: Senha correta: {senha_ok}")
        
        if corretor and check_password_hash(corretor['senha'], password):
            user = User(
                id=corretor['id'],
                username=corretor['username'],
                nome=corretor['nome'],
                email=corretor.get('email', ''),
                tipo=corretor.get('tipo', 'corretor')
            )
            login_user(user, remember=True)
            
            next_page = request.args.get('next')
            redirect_url = next_page or url_for('dashboard')
            
            # Mostrar animação de entrada
            return render_template('login_success.html',
                                 user_name=corretor['nome'],
                                 redirect_url=redirect_url)
        else:
            flash('Usuário ou senha inválidos.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    Logout do usuário
    """
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


# ==================== ROTAS PRINCIPAIS ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal
    """
    # Obter estatísticas
    stats = db.get_estatisticas()
    loteamentos = db.get_loteamentos()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         loteamentos=loteamentos,
                         user=current_user)


@app.route('/disponibilidade')
@login_required
def disponibilidade():
    """
    Página de disponibilidade de lotes
    """
    # Obter filtros da URL
    filtros = {
        'loteamento_id': request.args.get('loteamento_id', type=int),
        'quadra_id': request.args.get('quadra_id', type=int),
        'metragem_min': request.args.get('metragem_min', type=float),
        'metragem_max': request.args.get('metragem_max', type=float)
    }
    
    # Remover filtros vazios
    filtros = {k: v for k, v in filtros.items() if v is not None}
    
    # Obter dados
    lotes = db.get_disponibilidade_completa(filtros if filtros else None)
    loteamentos = db.get_loteamentos()
    stats = db.get_estatisticas()
    
    # Obter quadras se loteamento selecionado
    quadras = []
    if filtros.get('loteamento_id'):
        quadras = db.get_quadras_by_loteamento(filtros['loteamento_id'])
    
    return render_template('disponibilidade.html',
                         lotes=lotes,
                         loteamentos=loteamentos,
                         quadras=quadras,
                         filtros=filtros,
                         stats=stats,
                         user=current_user)


@app.route('/mapa')
@login_required
def mapa():
    """
    Mapa visual das quadras
    """
    loteamento_id = request.args.get('loteamento_id', type=int)
    quadra_id = request.args.get('quadra_id', type=int)
    
    loteamentos = db.get_loteamentos()
    quadras = []
    lotes = []
    loteamento_selecionado = None
    quadra_selecionada = None
    
    if loteamento_id:
        loteamento_selecionado = db.get_loteamento_by_id(loteamento_id)
        quadras = db.get_quadras_by_loteamento(loteamento_id)
        
        if quadra_id:
            lotes = db.get_todos_lotes_por_quadra(quadra_id)
            for q in quadras:
                if q['id'] == quadra_id:
                    quadra_selecionada = q
                    break
    
    return render_template('mapa.html',
                         loteamentos=loteamentos,
                         quadras=quadras,
                         lotes=lotes,
                         loteamento_selecionado=loteamento_selecionado,
                         quadra_selecionada=quadra_selecionada,
                         user=current_user)


# ==================== API ENDPOINTS ====================

@app.route('/api/loteamentos')
@login_required
def api_loteamentos():
    """
    API: Retorna lista de loteamentos
    """
    loteamentos = db.get_loteamentos()
    return jsonify(loteamentos)


@app.route('/api/quadras/<int:loteamento_id>')
@login_required
def api_quadras(loteamento_id):
    """
    API: Retorna quadras de um loteamento
    """
    quadras = db.get_quadras_by_loteamento(loteamento_id)
    return jsonify(quadras)


@app.route('/api/lotes/<int:quadra_id>')
@login_required
def api_lotes(quadra_id):
    """
    API: Retorna lotes de uma quadra
    """
    lotes = db.get_todos_lotes_por_quadra(quadra_id)
    return jsonify(lotes)


@app.route('/api/disponibilidade')
@login_required
def api_disponibilidade():
    """
    API: Retorna lotes disponíveis com filtros
    """
    filtros = {
        'loteamento_id': request.args.get('loteamento_id', type=int),
        'quadra_id': request.args.get('quadra_id', type=int),
        'metragem_min': request.args.get('metragem_min', type=float),
        'metragem_max': request.args.get('metragem_max', type=float)
    }
    
    filtros = {k: v for k, v in filtros.items() if v is not None}
    lotes = db.get_disponibilidade_completa(filtros if filtros else None)
    
    return jsonify(lotes)


@app.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """
    API: Retorna estatísticas gerais
    """
    stats = db.get_estatisticas()
    return jsonify(stats)


@app.route('/api/estatisticas/<int:loteamento_id>')
@login_required
def api_estatisticas_loteamento(loteamento_id):
    """
    API: Retorna estatísticas de um loteamento
    """
    stats = db.get_estatisticas_por_loteamento(loteamento_id)
    return jsonify(stats)


# ==================== FILTROS JINJA2 ====================

@app.template_filter('format_currency')
def format_currency(value):
    """
    Formata valor como moeda brasileira
    """
    if value is None:
        return 'R$ 0,00'
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


@app.template_filter('format_area')
def format_area(value):
    """
    Formata valor como área em m²
    """
    if value is None:
        return '0,00 m²'
    return f"{value:,.2f} m²".replace(',', 'X').replace('.', ',').replace('X', '.')


@app.template_filter('format_number')
def format_number(value):
    """
    Formata número com separador de milhar
    """
    if value is None:
        return '0'
    return f"{value:,}".replace(',', '.')


# ==================== CONTEXTO GLOBAL ====================

@app.context_processor
def inject_globals():
    """
    Injeta variáveis globais nos templates
    """
    return {
        'app_name': Config.APP_NAME,
        'app_version': Config.APP_VERSION,
        'company_name': Config.COMPANY_NAME
    }


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    # Conectar ao banco de dados
    if db.connect():
        print("Conexão com banco de dados estabelecida!")
    else:
        print("AVISO: Não foi possível conectar ao banco de dados.")
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
