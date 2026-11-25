import sqlite3

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from database import conectar_banco

livros_bp = Blueprint("livros", __name__)


def _validar(dados):
    """Retorna (titulo, ano, autor_id) ou None se os dados forem inválidos."""
    titulo = str(dados.get("titulo") or "").strip()
    autor_id = dados.get("autor_id")
    ano = dados.get("ano")
    if not titulo or not isinstance(autor_id, int) or isinstance(autor_id, bool):
        return None
    if ano is not None and (not isinstance(ano, int) or isinstance(ano, bool)):
        return None
    return titulo, ano, autor_id


def _autor_existe(conn, autor_id):
    return conn.execute("SELECT id FROM autores WHERE id = ?", (autor_id,)).fetchone() is not None


@livros_bp.route("/livros", methods=["GET"])
def listar_livros():
    conn = conectar_banco()
    try:
        linhas = conn.execute("SELECT * FROM livros").fetchall()
        return jsonify([dict(l) for l in linhas]), 200
    except sqlite3.Error:
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@livros_bp.route("/livros/<int:id>", methods=["GET"])
def buscar_livro(id):
    conn = conectar_banco()
    try:
        linha = conn.execute("SELECT * FROM livros WHERE id = ?", (id,)).fetchone()
        if linha is None:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify(dict(linha)), 200
    except sqlite3.Error:
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@livros_bp.route("/livros", methods=["POST"])
@jwt_required()
def criar_livro():
    valores = _validar(request.get_json(silent=True) or {})
    if valores is None:
        return jsonify({"erro": "Título e autor_id válidos são obrigatórios"}), 400
    titulo, ano, autor_id = valores

    conn = conectar_banco()
    try:
        if not _autor_existe(conn, autor_id):
            return jsonify({"erro": "autor_id inexistente"}), 400
        cur = conn.execute(
            "INSERT INTO livros (titulo, ano, autor_id) VALUES (?, ?, ?)",
            (titulo, ano, autor_id),
        )
        conn.commit()
        return jsonify({"id": cur.lastrowid, "titulo": titulo, "ano": ano, "autor_id": autor_id}), 201
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@livros_bp.route("/livros/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_livro(id):
    valores = _validar(request.get_json(silent=True) or {})
    if valores is None:
        return jsonify({"erro": "Título e autor_id válidos são obrigatórios"}), 400
    titulo, ano, autor_id = valores

    conn = conectar_banco()
    try:
        if not _autor_existe(conn, autor_id):
            return jsonify({"erro": "autor_id inexistente"}), 400
        cur = conn.execute(
            "UPDATE livros SET titulo = ?, ano = ?, autor_id = ? WHERE id = ?",
            (titulo, ano, autor_id, id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify({"id": id, "titulo": titulo, "ano": ano, "autor_id": autor_id}), 200
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@livros_bp.route("/livros/<int:id>", methods=["DELETE"])
@jwt_required()
def excluir_livro(id):
    conn = conectar_banco()
    try:
        cur = conn.execute("DELETE FROM livros WHERE id = ?", (id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify({"mensagem": "Livro excluído"}), 200
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()