from flask import Flask, jsonify, bcript, request
from main import app, con

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        dados = request.get_json()

        nome = dados.get('nome')
        senha = dados.get('senha')

        cur = con.cursor()

        cur.execute('select 1 from usuario where nome = ?', (nome,))
        if cur.fetchone():
            return jsonify({"error":"Usuário já cadastrado"}), 400

        cur.execute("""insert into usuario(nome, senha)
                       values(?,?)""", (nome, senha))

        con.commit()
        return jsonify({
            "message": "Usuário cadastrado com sucesso",
            'usuario': {
            "nome": nome,
            "senha": senha,
        }
        }), 201

    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar usuário"}), 500
    finally:
        cur.close()

@app.route('/validar_senha', methods=['POST'])
def validar_senha(senha: str):
    if not senha:
        return False, "Senha é obrigatória.",

    maiuscula = minuscula = numero = caracterpcd = False
    for s in senha:
        if s.isupper():
            maiuscula = True
        if s.islower():
            minuscula = True
        if s.isdigit():
            numero = True
        if not s.isalnum():
            caracterpcd = True

    if len(senha) < 8 or len(senha) > 12:
        return False, "A senha deve ter entre 8 e 12 caracteres.",

    if not (maiuscula and minuscula and numero and caracterpcd):
        return False, "Senha fraca: precisa maiúscula, minúscula, número e caractere especial.",
