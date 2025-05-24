import os  # ✅ agora sim!
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv  # opcional, mas recomendado

# Carrega variáveis do .env se existir
load_dotenv()

# Inicializações globais
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Segurança e controle de sessão
    app.secret_key = "minha_chave_secreta"
    app.config['SESSION_PERMANENT'] = False

    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///meubanco.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialização dos componentes
    db.init_app(app)
    migrate.init_app(app, db)

    # Registro de filtros Jinja2 personalizados
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        if value is None:
            return ''
        return value.strftime(format)

    # Registro de Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
