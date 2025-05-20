from app import create_app, db
from app.models import Produto

app = create_app()
with app.app_context():
    db.create_all()
    print("Banco e tabelas criados com sucesso.")