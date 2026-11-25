import sqlite3

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

from database import conectar_banco

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json(silent=True) or {}
    nome = str(dados.get("nome") or "").strip()
    email = str(dados.get("email") or "").strip().lower()
    senha = str(dados.get("senha") or "")
    perfil = dados.get("perfil", "usuario")

    if not nome or not email or not senha or perfil not in ("usuario", "admin"):
        return jsonify({"erro": "Campos obrigatórios ausentes ou inválidos"}), 400

    conn = conectar_banco()
    try:
        cur = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, perfil) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), perfil),
        )
        conn.commit()
        return jsonify({"id": cur.lastrowid, "nome": nome, "email": email, "perfil": perfil}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"erro": "E-mail já cadastrado"}), 409
    except sqlite3.Error:
        conn.rollback()
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}
    email = str(dados.get("email") or "").strip().lower()
    senha = str(dados.get("senha") or "")

    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    conn = conectar_banco()
    try:
        usuario = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    except sqlite3.Error:
        return jsonify({"erro": "Erro ao processar a requisição"}), 500
    finally:
        conn.close()

    if usuario is None or not check_password_hash(usuario["senha"], senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    token = create_access_token(
        identity=str(usuario["id"]),  # o subject do JWT deve ser string
        additional_claims={"perfil": usuario["perfil"]},
    )
    return jsonify({"access_token": token}), 200


@auth_bp.route("/meu-acesso", methods=["GET"])
@jwt_required()
def meu_acesso():
    return jsonify({"id": int(get_jwt_identity()), "perfil": get_jwt().get("perfil")}), 200