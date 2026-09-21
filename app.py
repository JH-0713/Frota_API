from datetime import timedelta, datetime
from flask import Flask, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models import Policial, db_session, Viatura, Checklist_Turno, Responsavel, Itens_Manutencao, Ordem_Itens, \
    Ordem_Servico
import os
from dotenv import load_dotenv
# gera token
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps

load_dotenv()

app = Flask(__name__)
# definir a senha, em produção colocar em local seguro
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
jwt = JWTManager(app)

# previne gargalo "too many connections"
"""
### @app.teardown_appcontext (O Zelador)
### Para que serve: 
Fechar conexões de banco de dados, limpar memória temporária, fechar arquivos abertos. 
Ele evita o temido Memory Leak (Vazamento de Memória).
### Curiosidade: 
Como estamos usando o Flask-SQLAlchemy, você nunca precisará escrever esse comando na mão para o banco de dados. 
A biblioteca já injeta um teardown_appcontext invisível no seu app que faz db.session.remove() automaticamente.
"""


@app.route('/get_policiais', methods=['GET'])
def get_policiais():
    db = db_session()
    try:
        sql_p = select(Policial)
        result_policia = db.execute(sql_p).scalars()
        lista_p = []
        for p in result_policia:
            lista_p.append(p.serialize())
        return jsonify(lista_p), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_viaturas', methods=['GET'])
def get_viaturas():
    try:
        sql_v = select(Viatura)
        result_viatura = db_session.execute(sql_v).scalars()
        lista_v = []
        for v in result_viatura:
            lista_v.append(v.serialize())
        return jsonify(lista_v), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_responsaveis', methods=['GET'])
def get_responsaveis():
    try:
        sql_r = select(Responsavel)
        result_responsavel = db_session.execute(sql_r).scalars()
        lista_r = []
        for r in result_responsavel:
            lista_r.append(r.serialize())
        return jsonify(lista_r), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_itens', methods=['GET'])
def get_itens():
    try:
        sql_i = select(Itens_Manutencao)
        result_itens = db_session.execute(sql_i).scalars()
        lista_i = []
        for i in result_itens:
            lista_i.append(i.serialize())
        return jsonify(lista_i), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_checklist', methods=['GET'])
def get_checklist():
    try:
        checklist_banco = select(Checklist_Turno)
        result_checklist = db_session.execute(checklist_banco).scalars()
        lista_c = []
        if not result_checklist:
            print(result_checklist)
            return jsonify({"msg": "Error"}), 400
        print('flamingo',result_checklist)
        for c in result_checklist:
            lista_c.append(c.serialize())
        return jsonify(lista_c), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {str(e)}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_ordem', methods=['GET'])
def get_ordem():
    try:
        sql_o = select(Ordem_Servico)
        result_ordem = db_session.execute(sql_o).scalars()
        lista_o = []
        for o in result_ordem:
            lista_o.append(o.serialize())
        return jsonify(lista_o), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/get_ordem_itens', methods=['GET'])
def get_ordem_itens():
    try:
        sql_oi = select(Ordem_Itens)
        result_ordem_itens = db_session.execute(sql_oi).scalars()
        lista_oi = []
        for oi in result_ordem_itens:
            lista_oi.append(oi.serialize())
        return jsonify(lista_oi), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()



@app.route('/post_policial', methods=['POST'])
def post_policial():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cargo_patente = dados.get('cargo_patente')
    matricula = dados.get('matricula')

    if not nome or not email or not senha or not cargo_patente or not matricula:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Policial).where(Policial.email == email)
        result_policia = db_session.execute(sql_p).scalar()

        if result_policia:
            return jsonify({'msg': "Policial já existe"}), 400

        new_p = Policial(nome=nome, email=email, cargo_patente=cargo_patente, matricula=matricula)
        new_p.set_senha_hash(senha)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Policial cadastrado com sucesso",
            "user_id": new_p.id_policial
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_viatura', methods=['POST'])
def post_viatura():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    placa = dados.get('placa')
    ano = dados.get('ano')
    km_atual = dados.get('km_atual')
    prefixo = dados.get('prefixo')
    modelo = dados.get('modelo')
    status_atual = dados.get('status_atual')

    if not placa or not ano or not km_atual or not prefixo or not modelo:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Viatura).where(Viatura.placa == placa)
        result_viatura = db_session.execute(sql_p).scalar()

        if result_viatura:
            return jsonify({'msg': "Viatura já existe"}), 400

        new_v = Viatura(placa=placa, ano=ano, km_atual=km_atual, prefixo=prefixo, modelo=modelo,
                        status_atual=status_atual)
        db_session.add(new_v)
        db_session.commit()

        info = {
            "msg": "Viatura cadastrada com sucesso",
            "user_id": new_v.id_viatura
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_responsavel', methods=['POST'])
def post_responsavel():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cargo_funcao = dados.get('cargo_funcao')

    if not nome or not email or not senha or not cargo_funcao:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Responsavel).where(Responsavel.email == email)
        result_responsavel = db_session.execute(sql_p).scalar()

        if result_responsavel:
            return jsonify({'msg': "Responsavel já existe"}), 400

        new_p = Responsavel(nome=nome, email=email, cargo_funcao=cargo_funcao)
        new_p.set_senha_hash(senha)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Responsavel cadastrado com sucesso",
            "user_id": new_p.id_responsavel
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_item', methods=['POST'])
def post_item():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    nome_item = dados.get('nome_item')
    descricao = dados.get('descricao')
    categoria_falha = dados.get('categoria_falha')
    valor_unitario = dados.get('valor_unitario')

    if not nome_item or not descricao or not categoria_falha or not valor_unitario:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Itens_Manutencao(nome_item=nome_item, descricao=descricao, categoria_falha=categoria_falha, valor_unitario=valor_unitario )
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Item cadastrado com sucesso",
            "user_id": new_p.id_item
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_checklist', methods=['POST'])
def post_checklist():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    viatura_id = dados.get('viatura_id')
    policial_id = dados.get('policial_id')
    nivel_oleo = dados.get('nivel_oleo')
    status_pneu = dados.get('status_pneu')
    km_abertura = dados.get('km_abertura')
    relatorio_problema = dados.get('relatorio_problema')

    if not nivel_oleo or not viatura_id or not policial_id or not status_pneu or not km_abertura or not relatorio_problema:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Checklist_Turno(viatura_id=viatura_id, policial_id=policial_id, nivel_oleo=nivel_oleo, status_pneu=status_pneu, km_abertura=km_abertura, relatorio_problema=relatorio_problema)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Checklist cadastrada com sucesso",
            "user_id": new_p.id_checklist
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_ordem_servico', methods=['POST'])
def post_ordem_servico():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    viatura_id = dados.get('viatura_id')
    responsavel_id = dados.get('responsavel_id')
    tipo_manutencao = dados.get('tipo_manutencao')
    status_os = dados.get('status_os')
    custo_total = dados.get('custo_total')

    if not viatura_id or not responsavel_id or not tipo_manutencao or not status_os or not custo_total:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Ordem_Servico(viatura_id=viatura_id, responsavel_id=responsavel_id, tipo_manutencao=tipo_manutencao, status_os=status_os, custo_total=custo_total)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Ordem cadastrada com sucesso",
            "user_id": new_p.id_ordem
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()

@app.route('/post_ordem_itens', methods=['POST'])
def post_ordem_itens():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    os_id = dados.get('os_id')
    item_id = dados.get('item_id')

    if not os_id or not item_id:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Ordem_Itens(os_id=os_id, item_id=item_id)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Lista de Itens criada com sucesso",
            "user_id": new_p.id_os_item
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()


if __name__ == '__main__':
    app.run(debug=True,port=5005,host='0.0.0.0')