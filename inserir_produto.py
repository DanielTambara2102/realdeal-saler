from app import create_app, db
from app.models import Produto
from datetime import datetime

# Cria a aplicação com o factory
app = create_app()

# Usa o contexto da aplicação para acessar o banco
with app.app_context():
    novo_produto = Produto(
        marca='Nike',
        nome='testeIII',
        preco=2000,
        data_compra=datetime.strptime('2025-05-17', '%Y-%m-%d'),
        servicos_extras=100,
        #data_venda=datetime.strptime('2025-05-18', '%Y-%m-%d'),
        #preco_venda=6000,
        status = 'Em Manutenção'
    )

    db.session.add(novo_produto)
    db.session.commit()

    print('✅ Produto inserido com sucesso!')
