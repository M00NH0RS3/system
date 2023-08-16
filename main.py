from flask import Flask, render_template, redirect, request, flash, send_from_directory, session
import json
import ast
import os
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origind="*")
app.config['SECRET_KEY'] = '2603'

logado = False
usuarioOnline = None


@app.route('/')
def home():

    global logado

    logado = False
    return render_template('login.html')


@app.route('/adm')
def adm():
    if logado == True:
        with open('usuarios.json') as usuariosTemp:
            usuarios = json.load(usuariosTemp)
        return render_template('administrador.html', usuarios=usuarios)
    if logado == False:
        flash('Necessário realizar o Login!')
        return redirect('/')


@app.route('/usuario')
def usuario():
    if logado == True:
        nome = session.get('nome')
        usuarioOnline = nome
        arquivo = []
        for documento in os.listdir('arquivos/'):
            arquivo.append(documento)

        return render_template('usuario.html', arquivos=arquivo, usuarioOnline=usuarioOnline)
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():

    global logado

    nome = request.form.get('nome')
    senha = request.form.get('senha')

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

        cont = 0

        for usuario in usuarios:
            cont += 1
            if nome == 'adm' and senha == '000':
                logado = True
                return redirect('/adm')

            if usuario['nome'] == nome and usuario['senha'] == senha:
                logado = True
                session['nome'] = nome
                return redirect('/usuario')

            if cont >= len(usuarios):
                flash('Usuário ou Senha Inválida!')
                return redirect('/')


@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    global logado

    nome = request.form.get('nome')
    senha = request.form.get('senha')

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

        nomes_cadastrados = [usuario['nome'] for usuario in usuarios]

        if nome in nomes_cadastrados:
            flash('Usuário já cadastrado!')
            return redirect('/adm')
        else:
            novo_usuario = {
                "nome": nome,
                "senha": senha
            }
            usuarios.append(novo_usuario)

            with open('usuarios.json', 'w') as gravarTemp:
                json.dump(usuarios, gravarTemp, indent=4)

            logado = True

            flash(f'{nome} cadastrado!')
            return redirect('/adm')


@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():

    global logado
    logado = True

    usuario = request.form.get('usuarioPexcluir')
    usuarioDict = ast.literal_eval(usuario)
    nome = usuarioDict['nome']

    with open('usuarios.json') as usuariosTemp:
        usuariosJson = json.load(usuariosTemp)
        for c in usuariosJson:
            if c == usuarioDict:
                usuariosJson.remove(usuarioDict)
                with open('usuarios.json', 'w') as usuarioAexcluir:
                    json.dump(usuariosJson, usuarioAexcluir, indent=4)

    flash(F'{nome} excluído!')
    return redirect('/adm')


@app.route('/upload', methods=['POST'])
def upload():
    global logado
    logado = True

    arquivo = request.files.get('documento')
    nome_arquivo = arquivo.filename.replace(' ', '_')
    arquivo.save(os.path.join('arquivos/', nome_arquivo))
    flash('Arquivo salvo!')
    return redirect('/adm')


@app.route('/download', methods=['POST'])
def download():
    nomeArquivo = request.form.get('arquivosParaDownload')

    return send_from_directory('arquivos', nomeArquivo, as_attachment=1)


@socketio.on('message')
def gerenciar_mensagem(mensagem):
    send(mensagem, broadcast=1)


@app.route('/chat', methods=['POST'])
def chat():
    global logado
    logado = True
    nome = session.get('nome')
    usuarioChat = nome

    return render_template('chat.html', usuarioChat=usuarioChat)

@app.route('/menu', methods=['POST'])
def menu():
    global logado
    logado = True

    return redirect('/usuario')

@app.route('/sair', methods=['POST'])
def sair():

    return redirect('/')

if __name__ in '__main__':
    app.run(debug=1)
