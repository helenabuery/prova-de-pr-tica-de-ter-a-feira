import sqlite3

from flask import Blueprint, request, jsonify

from database import conectar_banco

autores_bp = Blueprint("autores", __name__)


def _validar(dados):
    nome = str(dados.get("nome") or "").strip()
    nacionalidade = dados.get("nacionalidade")
    if not nome:
        return None, None
    return nome, (str(nacionalidade).strip() if nacionalidade else None)


@autores_bp.route("/autores", methods=["GET"])
def listar_autores():
    conn = conectar_banco()
    try:
        linhas = conn.execute("SELECT * FROM autores").fetchall()
        return jsonify([dict(l) for l in linhas]), 200
    except sqlite3.Error:
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@autores_bp.route("/autores/<int:id>", methods=["GET"])
def buscar_autor(id):
    conn = conectar_banco()
    try:
        linha = conn.execute("SELECT * FROM autores WHERE id = ?", (id,)).fetchone()
        if linha is None:
            return jsonify({"erro": "Autor não encontrado"}), 404
        return jsonify(dict(linha)), 200
    except sqlite3.Error:
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@autores_bp.route("/autores", methods=["POST"])
def criar_autor():
    nome, nacionalidade = _validar(request.get_json(silent=True) or {})
    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    conn = conectar_banco()
    try:
        cur = conn.execute(
            "INSERT INTO autores (nome, nacionalidade) VALUES (?, ?)", (nome, nacionalidade)
        )
        conn.commit()
        return jsonify({"id": cur.lastrowid, "nome": nome, "nacionalidade": nacionalidade}), 201
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@autores_bp.route("/autores/<int:id>", methods=["PUT"])
def atualizar_autor(id):
    nome, nacionalidade = _validar(request.get_json(silent=True) or {})
    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    conn = conectar_banco()
    try:
        cur = conn.execute(
            "UPDATE autores SET nome = ?, nacionalidade = ? WHERE id = ?",
            (nome, nacionalidade, id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"erro": "Autor não encontrado"}), 404
        return jsonify({"id": id, "nome": nome, "nacionalidade": nacionalidade}), 200
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@autores_bp.route("/autores/<int:id>", methods=["DELETE"])
def excluir_autor(id):
    conn = conectar_banco()
    try:
        cur = conn.execute("DELETE FROM autores WHERE id = ?", (id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"erro": "Autor não encontrado"}), 404
        return jsonify({"mensagem": "Autor excluído"}), 200
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"erro": "Autor possui livros vinculados"}), 409
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()