import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from database import criar_tabelas
from routes.autores import autores_bp
from routes.livros import livros_bp
from routes.auth import auth_bp

app = Flask(__name__)

# Somente para o exercício local. Em produção, use variável de ambiente.
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "chave-local-do-exercicio-com-32-caracteres")

jwt = JWTManager(app)

app.register_blueprint(autores_bp)
app.register_blueprint(livros_bp)
app.register_blueprint(auth_bp)


@app.after_request
def adicionar_versao(resposta):
    resposta.headers["X-API-Versao"] = "1.0"
    return resposta


# ---------- Error handlers (respostas JSON padronizadas) ----------
@app.errorhandler(400)
def erro_400(e):
    return jsonify({"erro": "Requisição inválida"}), 400


@app.errorhandler(404)
def erro_404(e):
    return jsonify({"erro": "Recurso não encontrado"}), 404


@app.errorhandler(405)
def erro_405(e):
    return jsonify({"erro": "Método não permitido"}), 405


@app.errorhandler(500)
def erro_500(e):
    return jsonify({"erro": "Erro interno do servidor"}), 500


@app.errorhandler(Exception)
def erro_generico(e):
    if isinstance(e, HTTPException):
        return jsonify({"erro": e.name}), e.code
    return jsonify({"erro": "Erro interno do servidor"}), 500


# ---------- Respostas JWT (token ausente, inválido ou expirado) ----------
@jwt.unauthorized_loader
def token_ausente(motivo):
    return jsonify({"erro": "Token de acesso ausente"}), 401


@jwt.invalid_token_loader
def token_invalido(motivo):
    return jsonify({"erro": "Token inválido"}), 401


@jwt.expired_token_loader
def token_expirado(cabecalho, dados):
    return jsonify({"erro": "Token expirado"}), 401


if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)