from app import create_app, db
from app.models import Produto

app = create_app()

with app.app_context():
    id_para_excluir = 4  # substitua pelo id do produto que quer excluir

    produto = Produto.query.get(id_para_excluir)
    if produto:
        db.session.delete(produto)
        db.session.commit()
        print(f'✅ Produto com id {id_para_excluir} excluído com sucesso!')
    else:
        print(f'❌ Produto com id {id_para_excluir} não encontrado.')
