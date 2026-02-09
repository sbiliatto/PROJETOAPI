from flask import Flask, jsonify, request
from main import app, con

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

@app.route('/criar_livro', methods=['POST'])
def criar_livro():
    try:
        dados = request.get_json()

        titulo = dados.get('titulo')
        autor = dados.get('autor')
        ano_publicacao = dados.get('ano_publicacao')

        cur = con.cursor()

        cur.execute('select 1 from livro where titulo = ?', (titulo,))
        if cur.fetchone():
            return jsonify({"error":"Livro já cadastrado"}), 400

        cur.execute("""insert into livro(titulo, autor, ano_publicacao)
                       values(?,?,?)""", (titulo, autor, ano_publicacao))

        con.commit()
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



