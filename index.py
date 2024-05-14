from flask import Flask, render_template, request, redirect, url_for
import qrcode
import json
import os

app = Flask(__name__)

# Define o caminho para o arquivo JSON do banco de dados
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'db', 'database.json')

# Verifica se o diretório db existe, se não, cria-o
if not os.path.exists(os.path.dirname(DATABASE_PATH)):
    os.makedirs(os.path.dirname(DATABASE_PATH))

# Verifica se o arquivo JSON do banco de dados existe, se não, cria-o com uma lista vazia
if not os.path.exists(DATABASE_PATH):
    with open(DATABASE_PATH, 'w') as f:
        json.dump([], f)

def load_database():
    # Carrega o banco de dados a partir do arquivo JSON
    try:
        with open(DATABASE_PATH, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return []

def save_to_database(data):
    # Salva os dados no banco de dados (JSON)
    with open(DATABASE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_qrcode', methods=['POST'])
def gerar_qrcode():
    # Carrega os dados existentes no banco de dados
    database = load_database()

    # Verifica se existem dados no banco de dados
    if database:
        # Se existirem, obtem o último ID e incrementa
        id_autoincrement = database[-1]['id'] + 1
    else:
        # Se não existirem, define o ID inicial como 1
        id_autoincrement = 1

    # Recebe os dados do formulário
    peca = request.form['peca']
    tamanho = request.form['tamanho']
    modelo = request.form['modelo']
    fabricacao = request.form['fabricacao']
    n_pedido = request.form['n_pedido']
    lote = request.form['lote']
    cod = request.form['cod']

    # Constrói o conteúdo da página dinâmica com base nos dados do formulário
    conteudo_pagina = f"<h1>Página Gerada</h1><p>ID: {id_autoincrement}</p><p>Modelo: {modelo}</p><p>Tamanho: {tamanho}</p><p>Fabricação: {fabricacao}</p><p>Número do Pedido: {n_pedido}</p><p>Lote: {lote}</p><p>Código: {cod}</p>"

    # Adiciona os dados ao banco de dados
    database.append({
        'id':  id_autoincrement,
        'modelo': modelo,
        'tamanho': tamanho,
        'fabricacao': fabricacao,
        'n_pedido': n_pedido,
        'lote': lote,
        'cod': cod
    })
    save_to_database(database)

    # Gera o link para a página dinâmica com os dados preenchidos
    link_infopage = url_for('infopage', id=id_autoincrement, peca=peca, tamanho=tamanho, modelo=modelo, fabricacao=fabricacao, n_pedido=n_pedido, lote=lote, cod=cod, _external=True)

    # Cria o QR code com base no link da página dinâmica
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(link_infopage)
    qr.make(fit=True)

    # Cria uma imagem do QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Salva a imagem com o nome do ID da peça
    img_path = f"static/qrcode/qrcode_{id_autoincrement}.png"
    img.save(img_path)

    # Redireciona para a página inicial com o modal de sucesso e o caminho do QR code
    return render_template('index.html', success=True, qrcode_path=img_path)


@app.route('/infopage')
def infopage():
    # Recebe os dados passados pela URL
    id = request.args.get('id')
    modelo = request.args.get('modelo')
    tamanho = request.args.get('tamanho')
    fabricacao = request.args.get('fabricacao')
    n_pedido = request.args.get('n_pedido')
    lote = request.args.get('lote')
    cod = request.args.get('cod')
    peca = request.args.get('peca')

    return render_template('infopage.html', id=id, peca=peca, tamanho=tamanho, modelo=modelo, fabricacao=fabricacao, n_pedido=n_pedido, lote=lote, cod=cod)

if __name__ == '__main__':
    app.run(debug=True, host='172.16.56.145', port=80)
