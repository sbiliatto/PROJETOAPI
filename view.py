from flask import Flask, jsonify, request, send_file, Response
from main import app, con
from funcao import validar_senha
from funcao import enviando_email
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
import os
import pygal
import threading


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/listar_livro', methods=['GET'])
def listar_livro():
    try:
        cur = con.cursor()
        cur.execute("select id_livros, TITULO, AUTOR, ANO_PUBLICACAO from livro")
        livros = cur.fetchall()

        livros_lista = []
        for livro in livros:
            livros_lista.append({
                'id_livros': livro[0]
                ,'titulo': livro[1]
                , 'autor': livro[2]
                , 'ano_publicacao': livro[3]
            })

        return jsonify(mensagem="Lista de livros", livros=livros_lista)
    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar livro"}), 500
    finally:
        cur.close()


@app.route('/relatorio', methods=['GET'])
def relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livros, titulo, autor, ano_publicacao FROM livro")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(
            200,
            10,
            f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}",
            ln=True
        )

    contador_livros = len(livros)
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(
        200,
        10,
        f"Total de livros cadastrados: {contador_livros}",
        ln=True,
        align='C'
    )

    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)

    return send_file(
        pdf_path,
        as_attachment=True,
        mimetype='application/pdf'
    )


@app.route('/criar_livro', methods=['POST'])
def criar_livro():
    try:

        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        ano_publicacao = request.form.get('ano_publicacao')
        imagem = request.files.get('imagem')
        cur = con.cursor()

        cur.execute('select 1 from livro where titulo = ?', (titulo,))
        if cur.fetchone():
            return jsonify({"error":"Livro já cadastrado"}), 400

        cur.execute("""insert into livro(titulo, autor, ano_publicacao)
                       values(?,?,?) returning id_livros""", (titulo, autor, ano_publicacao))

        codigo_livro = cur.fetchone()[0]
        con.commit()

        caminho_imagem = None

        if imagem:
            nome_imagem =f"{codigo_livro}.jpg"
            caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
            os.makedirs(caminho_imagem_destino, exist_ok=True)
            caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
            imagem.save(caminho_imagem)

        return jsonify({
            "message": "Livro cadastrado com sucesso",
            'livro': {
            "titulo": titulo,
            "autor": autor,
            "ano_publicacao": ano_publicacao
        }
        }), 201

    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar livro"}), 500
    finally:
        cur.close()

@app.route('/grafico')
def grafico():
    cur = con.cursor()
    cur.execute("""select ano_publicacao, count(*) 
                     from livro
                    group by ano_publicacao
                    order by ano_publicacao
    """)
    resultado = cur.fetchall()
    cur.close()

    grafico = pygal.Bar()
    grafico.title = 'Quantidade de livros por ano de publicação'

    for linha in resultado:
        grafico.add(str(linha[0]), linha[1])
    return Response(grafico.render(), mimetype='image/svg+xml')

@app.route('/enviar_email', methods=['POST'])
def enviar_email():
    dados = request.get_json()
    assunto = dados.get["assunto"]
    mensagem = dados.get["mensagem"]
    destinatario = dados.get["destinatario"]

    thread = threading.Thread(target=enviando_email,
                              args=(destinatario, assunto, mensagem))

    thread.start()

    return jsonify({"mensagem": "Email enviado com sucesso!"}), 200


@app.route('/editar_livro/<int:id>', methods=['PUT'])
def editar_livro(id):

    cur = con.cursor()
    cur.execute('select id_livros, titulo, autor, ano_publicacao from livro where id_livros = ?', (id,))
    tem_livro = cur.fetchone()
    if not tem_livro:
        cur.close()
        return jsonify({"error": "Livro não encontrado"}), 404
    dados = request.get_json()
    titulo = dados.get('titulo')
    autor = dados.get('autor')
    ano_publicacao = dados.get('ano_publicacao')

    cur.execute(""" update livro set titulo = ?, autor = ?, ano_publicacao = ? 
                    where id_livros = ? """, (titulo, autor, ano_publicacao, id))
    con.commit()
    cur.close()

    return jsonify({"message": "Livro atualizado com sucesso",
                    "livro": {
                        "id_livros": id,
                        "titulo": titulo,
                        "autor": autor,
                        "ano_publicacao": ano_publicacao
                    }
                    })


@app.route('/deletar_livro/<int:id>', methods=['DELETE'])
def deletar_livro(id):
        cur = con.cursor()
        cur.execute('select 1 from livro where id_livros = ?', (id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Livro não encontrado"}), 404

        cur.execute('delete from livro where id_livros = ?', (id,))
        con.commit()
        cur.close()

        return jsonify({"message": "Livro deletado com sucesso",
                        'id_livros':id })

@app.route('/listar_usuario', methods=['GET'])
def listar_usuario():
    try:
        cur = con.cursor()
        cur.execute("select id_usuario, nome from usuario")
        usuarios = cur.fetchall()

        usuario_lista = []
        for usuario in usuarios:
            usuario_lista.append({
                'id_usuario': usuario[0]
                ,'nome': usuario[1]
            })
            print('aqui')

        return jsonify(mensagem="Lista de usuarios", usuario=usuario_lista)
    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar usuário"}), 500

    finally:
        cur.close()

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        senha = dados.get('senha')
        cur = con.cursor()
        validado = validar_senha(senha)

        cur.execute('select 1 from usuario where nome = ?', (nome,))
        if cur.fetchone():
            return jsonify({"error": "Usuário já cadastrado"}), 400

        if not validado:
            return jsonify({"error": "A senha nao esta nos nossos rigorossos padroes de segurança"}), 400

        senha_hash = generate_password_hash(senha).decode('utf-8')
        cur.execute("""insert into usuario(nome, senha)
                              values(?,?)""", (nome, senha_hash))
        con.commit()
        return jsonify({
            "message": "Usuário cadastrado com sucesso",
            'usuario': {
                "nome": nome,
            }
        }), 201

    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar usuário"}), 500
    finally:
        cur.close()

@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):

    cur = con.cursor()
    cur.execute('select id_usuario, nome from usuario where id_usuario = ?', (id,))
    tem_usuario = cur.fetchone()
    if not tem_usuario:
        cur.close()
        return jsonify({"error": "Usuario não encontrado"}), 404
    dados = request.get_json()
    nome = dados.get('nome')
    senha = dados.get('senha')

    cur.execute(""" update usuario set nome = ?, senha = ?
                    where id_usuario = ? """, (nome, senha, id))
    con.commit()
    cur.close()

    return jsonify({"message": "Usuário atualizado com sucesso",
                    "usuario": {
                        "id_usuario": id,
                        "nome": nome,
                        "senha":senha,
                    }
                    })


@app.route('/login', methods=['POST'])
def login():
    cur = None
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        senha = dados.get('senha')

        cur = con.cursor()
        cur.execute("select senha from usuario where nome = ?", (nome,))
        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Usuário ou senha inválidos"}), 401

        if not validar_senha(senha):
            return jsonify({"error": "Usuário ou senha inválidos"}), 401

        return jsonify({"message": "Login realizado com sucesso"}), 200

    except Exception:
        return jsonify({"message": "Erro no login"}), 500


@app.route('/deletar_usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
        cur = con.cursor()
        cur.execute('select 1 from usuario where id_usuario = ?', (id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Usuario não encontrado"}), 404

        cur.execute('delete from usuario where id_usuario = ?', (id,))
        con.commit()
        cur.close()

        return jsonify({"message": "Usuário deletado com sucesso",
                        'id_usuario':id })


