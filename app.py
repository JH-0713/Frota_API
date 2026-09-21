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
        print('result_flamingo',result_itens)
        for i in result_itens:
            print(i.serialize())
            lista_i.append(i.serialize())
        return jsonify(lista_i), 200
    except Exception as e:
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
            return jsonify({'msg': "Usuário já existe"}), 400

        new_p = Policial(nome=nome, email=email, cargo_patente=cargo_patente, matricula=matricula)
        new_p.set_senha_hash(senha)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_policial
        }

        return jsonify(info), 201
    except Exception as e:
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
            return jsonify({'msg': "Usuário já existe"}), 400

        new_v = Viatura(placa=placa, ano=ano, km_atual=km_atual, prefixo=prefixo, modelo=modelo,
                        status_atual=status_atual)
        db_session.add(new_v)
        db_session.commit()

        info = {
            "msg": "Usuário criado com sucesso",
            "user_id": new_v.id_viatura
        }

        return jsonify(info), 201
    except Exception as e:
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
            return jsonify({'msg': "Usuário já existe"}), 400

        new_p = Responsavel(nome=nome, email=email, cargo_funcao=cargo_funcao)
        new_p.set_senha_hash(senha)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_responsavel
        }

        return jsonify(info), 201
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()



@app.route('/post_itens_manutencao', methods=['POST'])
def post_itens_manutencao():
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
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_item
        }

        return jsonify(info), 201
    except Exception as e:
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
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_checklist
        }

        return jsonify(info), 201
    except Exception as e:
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

    if not viatura_id or not responsavel_id or not  tipo_manutencao or not status_os or not custo_total:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Ordem_Servico(viatura_id=viatura_id, responsavel_id=responsavel_id, tipo_manutencao=tipo_manutencao, status_os=status_os, custo_total=custo_total)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_ordem
        }

        return jsonify(info), 201
    except Exception as e:
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
            "msg": "Usuário criado com sucesso",
            "user_id": new_p.id_lista
        }

        return jsonify(info), 201
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.remove()


@app.route('/put_policial/<var_id>', methods=['PUT'])
def put_policial(var_id):
    editar = select(Policial).where(Policial.id_policial == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Policial não encontrado"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        cargo_patente = dados.get('cargo_patente')
        matricula = dados.get('matricula')


        if not nome or not email or not senha or not matricula or not cargo_patente:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.nome = nome
            result.email = email
            result.senha = senha
            result.cargo_patente = cargo_patente
            result.matricula = matricula
            db_session.commit()
            return jsonify({"msg": "Policial atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()


@app.route('/put_viatura/<var_id>', methods=['PUT'])
def put_viatura(var_id):
    editar = select(Viatura).where(Viatura.id_viatura == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Viatura não encontrado"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        placa = dados.get('placa')
        ano = dados.get('ano')
        km_atual = dados.get('km_atual')
        prefixo = dados.get('prefixo')
        modelo = dados.get('modelo')
        status_atual = dados.get('status_atual')

        if not placa or not ano or not km_atual or not prefixo or not modelo or not status_atual:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.placa = placa
            result.ano = ano
            result.km_atual = km_atual
            result.prefixo = prefixo
            result.modelo = modelo
            result.status_atual = status_atual
            db_session.commit()
            return jsonify({"msg": "Viatura atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/put_responsavel/<var_id>', methods=['PUT'])
def put_responsavel(var_id):
    editar = select(Responsavel).where(Responsavel.id_responsavel == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Responsavel não encontrado"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        cargo_funcao = dados.get('cargo_funcao')

        if not nome or not email or not senha or not cargo_funcao:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.nome = nome
            result.email = email
            result.senha = senha
            result.cargo_funcao = cargo_funcao
            db_session.commit()
            return jsonify({"msg": "Responsavel atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/put_itens_manutencao/<var_id>', methods=['PUT'])
def put_itens_manutencao(var_id):
    editar = select(Itens_Manutencao).where(Itens_Manutencao.id_item == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Itens de manutenção não encontrados"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        nome_item = dados.get('nome_item')
        descricao = dados.get('descricao')
        categoria_falha = dados.get('categoria_falha')
        valor_unitario = dados.get('valor_unitario')

        if not nome_item or not descricao or not categoria_falha or not valor_unitario:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.nome_item = nome_item
            result.descricao = descricao
            result.categoria_falha = categoria_falha
            result.valor_unitario = valor_unitario
            db_session.commit()
            return jsonify({"msg": "Item de manutenção atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/put_checklist_turno/<var_id>', methods=['PUT'])
def put_checklist_turno(var_id):
    editar = select(Checklist_Turno).where(Checklist_Turno.id_checklist == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Checklist não encontrados"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        viatura_id = dados.get('viatura_id')
        policial_id = dados.get('policial_id')
        nivel_oleo = dados.get('nivel_oleo')
        status_pneu = dados.get('status_pneu')
        km_abertura = dados.get('km_abertura')
        relatorio_problema = dados.get('relatorio_problema')

        if not viatura_id or not policial_id or not nivel_oleo or not status_pneu or not km_abertura or not relatorio_problema:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.viatura_id = viatura_id
            result.policial_id = policial_id
            result.nivel_oleo = nivel_oleo
            result.status_pneu = status_pneu
            result.km_abertura = km_abertura
            result.relatorio_problema = relatorio_problema

            db_session.commit()
            return jsonify({"msg": "Checklist atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/put_ordem_servico/<var_id>', methods=['PUT'])
def put_ordem_servico(var_id):
    editar = select(Ordem_Servico).where(Ordem_Servico.id_ordem == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Ordem de serviço não encontrados"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        viatura_id = dados.get('viatura_id')
        responsavel_id = dados.get('responsavel_id')
        tipo_manutencao = dados.get('tipo_manutencao')
        status_os = dados.get('status_os')
        custo_total = dados.get('custo_total')
        print('asd',tipo_manutencao)
        if not viatura_id or not responsavel_id or not tipo_manutencao or not status_os or not custo_total:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.viatura_id = viatura_id
            result.responsavel_id = responsavel_id
            result.tipo_manutencao = tipo_manutencao
            result.status_os = status_os
            result.custo_total = custo_total
            db_session.commit()
            return jsonify({"msg": "Ordem de serivço atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/put_ordem_itens/<var_id>', methods=['PUT'])
def put_ordem_itens(var_id):
    editar = select(Ordem_Itens).where(Ordem_Itens.id_lista == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Ordem de itens não encontrados"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        os_id = dados.get('os_id')
        item_id = dados.get('item_id')

        if not os_id or not item_id:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.os_id = os_id
            result.item_id = item_id
            db_session.commit()
            return jsonify({"msg": "Ordem de itens atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500
        finally:
            db_session.close()



@app.route('/delete_policial/<var_id>', methods=['DELETE'])
def delete_policial(var_id):
    sql_p = select(Policial).where(Policial.id_policial == int(var_id))
    result = db_session.execute(sql_p).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Policial não encontrado"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Policial deletado com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()


@app.route('/delete_viatura/<var_id>', methods=['DELETE'])
def delete_viatura(var_id):
    delete = select(Viatura).where(Viatura.id_viatura == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Viatura não encontrada"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Viatura deletada com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()





@app.route('/delete_responsavel/<var_id>', methods=['DELETE'])
def delete_responsavel(var_id):
    delete = select(Responsavel).where(Responsavel.id_responsavel == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Responsavel não encontrado"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Responsavel deletado com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



@app.route('/delete_itens_manutencao/<var_id>', methods=['DELETE'])
def delete_itens_manutencao(var_id):
    delete = select(Itens_Manutencao).where(Itens_Manutencao.id_item == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Itens_Manutencao não encontrado"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Itens_Manutencao deletado com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



@app.route('/delete_checklist_turno/<var_id>', methods=['DELETE'])
def delete_checklist_turno(var_id):
    delete = select(Checklist_Turno).where(Checklist_Turno.id_checklist == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Checklist não encontrado"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Checklist deletado com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()


@app.route('/delete_ordem_servico/<var_id>', methods=['DELETE'])
def delete_ordem_servico(var_id):
    delete = select(Ordem_Servico).where(Ordem_Servico.id_ordem == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Ordem de serviço não encontrada"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Ordem de serviço deletada com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()


@app.route('/delete_ordem_itens<var_id>', methods=['DELETE'])
def delete_ordem_itens(var_id):
    delete = select(Ordem_Itens).where(Ordem_Itens.id_lista == int(var_id))
    result = db_session.execute(delete).scalar_one_or_none()
    if not result:
        return jsonify({"msg": "Ordens de itens não encontrado"}), 400

    try:
        db_session.delete(result)
        db_session.commit()
        return jsonify({"msg": "Ordens de itens deletado com sucesso!"}), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



@app.route('/pesquisar_policial', methods=['POST'])
def pesquisar_policial():
    dados = request.get_json()
    matricula = dados.get('matricula')
    if not matricula:
        return jsonify({"msg": "Nenhum policial encontrado"}), 400
    try:
        busca = select(Policial).where(Policial.matricula == matricula)
        rastreio = db_session.execute(busca).scalars().all()
        lista = []
        for r in rastreio:
            lista.append(r.serialize())
        return jsonify(lista), 200
    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()


@app.route('/pesquisar_viatura', methods=['POST'])
def pesquisar_viatura():
    dados = request.get_json()
    prefixo = dados.get('prefixo')
    if not prefixo:
        return jsonify({"msg": "Nenhuma viatura encontrado"}), 400

    try:
        busca = select(Viatura).where(Viatura.prefixo == prefixo)
        rastreio = db_session.execute(busca).scalars().all()
        lista = []
        for r in rastreio:
            lista.append(r.serialize())

        db_session.commit()
        return jsonify(lista), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



@app.route('/pesquisar_responsavel', methods=['POST'])
def pesquisar_responsavel():
    dados = request.get_json()
    email = dados.get('email')
    if not email:
        return jsonify({"msg": "Nenhum rsponsavel encontrado"}), 400

    try:
        busca = select(Responsavel).where(Responsavel.email == email)
        rastreio = db_session.execute(busca).scalars().all()
        lista = []
        for r in rastreio:
            lista.append(r.serialize())

        db_session.commit()
        return jsonify(lista), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



@app.route('/pesquisar_itens_manutencao', methods=['POST'])
def pesquisar_itens_manutencao():
    dados = request.get_json()
    nome_item = dados.get('nome_item')
    print('nome_item', nome_item)
    if not nome_item:
        return jsonify({"msg": "Nenhum item encontrado"}), 400

    try:
        busca = select(Itens_Manutencao).where(Itens_Manutencao.nome_item == nome_item)
        rastreio = db_session.execute(busca).scalars().all()
        lista = []
        for r in rastreio:
            print(r.nome_item, r.id_item)
            print(r.serialize())
            lista.append(r.serialize())

        db_session.commit()
        return jsonify(lista), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()



if __name__ == '__main__':
    app.run(debug=True,port=5005,host='0.0.0.0')

