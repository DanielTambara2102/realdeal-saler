from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Produto
from datetime import datetime
from collections import defaultdict

main = Blueprint('main', __name__)

# Usuário de exemplo (substituir por autenticação real futuramente)
USUARIOS = [
    {'usuario': 'admin', 'senha': '1234'},
    {'usuario': 'daniel.tambara', 'senha': '1234'},
    {'usuario': 'eduarda.robinson', 'senha': '1234'},
    {'usuario': 'luiza.bastos', 'senha': '1234'}
]


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica se existe um usuário com esse login e senha
        for user in USUARIOS:
            if user['usuario'] == username and user['senha'] == password:
                session.permanent = False
                session['usuario_logado'] = username
                return redirect(url_for('main.estoque'))

        flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')



@main.route('/')
@main.route('/index')
def index():
    return redirect(url_for('main.estoque'))


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('main.login'))


@main.route('/estoque', methods=['GET'])
def estoque():
    if 'usuario_logado' not in session:
        return redirect(url_for('main.login'))

    status_filtro = request.args.get('status', 'Todos')

    if status_filtro == 'Todos':
        produtos = Produto.query.filter(Produto.status.in_(['Disponivel', 'Em Manutenção'])).all()
    else:
        produtos = Produto.query.filter_by(status=status_filtro).all()

    return render_template('estoque.html', produtos=produtos, usuario=session['usuario_logado'], status_filtro=status_filtro)

@main.route('/processar_selecao', methods=['POST'])
def processar_selecao():
    if 'usuario_logado' not in session:
        return redirect(url_for('main.login'))

    produto_id = request.form.get('produto_selecionado')
    novo_status = request.form.get('novo_status')

    if not produto_id:
        flash('Nenhum produto selecionado.', 'warning')
        return redirect(url_for('main.estoque'))

    if not novo_status:
        flash('Nenhum status selecionado.', 'warning')
        return redirect(url_for('main.estoque'))

    produto = Produto.query.get(produto_id)
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('main.estoque'))

    # Atualiza o status
    produto.status = novo_status

    from . import db

    try:
        # Se o status for 'Disponivel', atualiza custo de manutenção e preço sugerido
        if novo_status == 'Disponivel':
            custo_manutencao = request.form.get('custo_manutencao')
            valor_venda_sugerido = request.form.get('valor_venda_sugerido')

            if custo_manutencao:
                produto.custo_manutencao = float(custo_manutencao)
            if valor_venda_sugerido:
                produto.valor_venda_sugerido = float(valor_venda_sugerido)

        # Se houver campo de custo de manutenção para outros status, atualiza também
        else:
            custo_manutencao = request.form.get('custo_manutencao')            
            if custo_manutencao:
                produto.custo_manutencao = float(custo_manutencao)

        # Se o status for vendido, processa os campos de venda
        if novo_status == 'Vendido':
            custo_frete = request.form.get('custo_frete')
            custos_extras = request.form.get('custos_extras')
            preco_venda = request.form.get('preco_venda')
            data_venda = request.form.get('data_venda')

            if custo_frete:
                produto.custo_frete = float(custo_frete)
            else:
                produto.custo_frete = 0.0

            if custos_extras:
                produto.custos_extras = float(custos_extras)
            else:
                produto.custos_extras = 0.0

            if preco_venda:
                produto.preco_venda = float(preco_venda)
            else:
                produto.preco_venda = 0.0

            if data_venda:
                produto.data_venda = datetime.strptime(data_venda, '%Y-%m-%d').date()

            # Calcula o lucro
            preco = produto.preco or 0.0
            custo_manutencao = produto.custo_manutencao or 0.0
            lucro = produto.preco_venda - preco - produto.custo_frete - produto.custos_extras - custo_manutencao
            produto.lucro = lucro
            
        db.session.commit()

    except ValueError:
        flash('Um ou mais valores numéricos são inválidos.', 'warning')
        return redirect(url_for('main.estoque'))

    flash(f'Status do produto #{produto.id} atualizado para "{novo_status}".', 'success')
    return redirect(url_for('main.estoque'))



from collections import defaultdict
from datetime import datetime

@main.route('/financeiro')
def financeiro():
    produtos = Produto.query.all()

    capital_investido = 70000.00
    estoque_produtos = [p for p in produtos if p.status in ['Disponivel', 'Em Manutenção']]
    valor_estoque = sum(p.preco for p in estoque_produtos)
    custo_manutencao_estoque = sum((p.custo_manutencao or 0) for p in estoque_produtos)

    lucro_total = sum(
        (p.lucro or 0)
        for p in produtos
        if p.status != 'Disponivel' and p.lucro is not None
    )

    saldo_disponivel = capital_investido - (valor_estoque + custo_manutencao_estoque) + lucro_total
    lucro_percentual = (lucro_total / capital_investido * 100) if capital_investido > 0 else 0

    # 🧠 Lógica para montar os dados do gráfico
    compras_por_mes = defaultdict(int)
    vendas_por_mes = defaultdict(int)

    for p in produtos:
        if p.data_compra:
            mes = p.data_compra.strftime('%Y-%m')
            compras_por_mes[mes] += 1
        if p.data_venda:
            mes = p.data_venda.strftime('%Y-%m')
            vendas_por_mes[mes] += 1

    todos_meses = sorted(set(compras_por_mes) | set(vendas_por_mes))
    labels = [datetime.strptime(m, "%Y-%m").strftime("%b/%Y") for m in todos_meses]
    compras_list = [compras_por_mes[m] for m in todos_meses]
    vendas_list = [vendas_por_mes[m] for m in todos_meses]

    return render_template(
        'financeiro.html',
        capital_investido=capital_investido,
        valor_estoque=valor_estoque,
        custo_manutencao_estoque=custo_manutencao_estoque,
        lucro_total=lucro_total,
        lucro_percentual=lucro_percentual,
        saldo_disponivel=saldo_disponivel,
        labels=labels,
        compras_list=compras_list,
        vendas_list=vendas_list
    )


@main.route('/comprar', methods=['GET', 'POST'])
def comprar():
    if 'usuario_logado' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        try:
            marca = request.form['marca'].strip().upper()
            nome = request.form['nome'].strip().upper()
            preco = float(request.form['preco'])
            valor_venda_sugerido = float(request.form['valor_venda_sugerido'])
            data_compra = datetime.strptime(request.form['data_compra'], '%Y-%m-%d').date()

            if preco <= 0:
                flash('O preço deve ser maior que zero.', 'danger')
                return redirect(url_for('main.comprar'))

            novo_produto = Produto(
                marca=marca,
                nome=nome,
                preco=preco,
                valor_venda_sugerido=valor_venda_sugerido,
                data_compra=data_compra,
            )

            from . import db
            db.session.add(novo_produto)
            db.session.commit()

            flash('Produto comprado com sucesso!', 'success')
            return redirect(url_for('main.comprar'))

        except Exception as e:
            flash(f'Erro ao processar os dados: {str(e)}', 'danger')

    return render_template('comprar.html')


@main.route('/vendidos', methods=['GET'])
def vendidos():
    if 'usuario_logado' not in session:
        return redirect(url_for('main.login'))

    produtos = Produto.query.filter_by(status='Vendido').all()
    return render_template('vendidos.html', produtos=produtos, usuario=session['usuario_logado'])
