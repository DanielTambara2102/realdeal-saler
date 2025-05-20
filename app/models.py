from . import db
from datetime import date

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    data_compra = db.Column(db.Date, nullable=False)
    custo_manutencao = db.Column(db.Float, nullable=True)
    custo_frete = db.Column(db.Float, nullable=True)
    custos_extras = db.Column(db.Float, nullable=True)
    data_venda = db.Column(db.Date, nullable=True)
    preco_venda = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Disponivel')
    lucro = db.Column(db.Float, nullable=True)
    valor_venda_sugerido = db.Column(db.Float, nullable=True)


