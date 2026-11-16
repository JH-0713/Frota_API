from flask import Flask, jsonify, request
from sqlalchemy import select
from models import Policial, db_session, Viatura, Checklist_Turno, Itens_Manutencao, Ordem_Itens, \
    Ordem_Servico, Carro_Modelo, Cargo_Oficial, Categoria
import os
from dotenv import load_dotenv
# gera token
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import random


load_dotenv()

app = Flask(__name__)
# definir a senha, em produção colocar em local seguro
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
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

def gerar_codigo(tipo='nenhum', contagem=0):
    lista_codigo = []
    lista = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    for i in range(contagem):
        lista_codigo.append(random.choice(lista))
    variavel = "".join(lista_codigo)
    if tipo.upper() == 'NENHUM':
        return 'error'
    elif tipo.upper() == 'PM':
        return "PM-" + variavel
    elif tipo.upper() == 'VTR':
        return "VTR-" + variavel


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



@app.route('/get_policiais', methods=['GET'])
def get_policiais():
    """
      **API para Consulta de Policiais**

      ### Endpoint:
      GET /get_policiais

      ### Parametros de Entrada:
      Não possui parâmetros de entrada.

      ### Respostas (JSON):
      * **200 OK:** Lista de policiais retornada com sucesso.
        ```json
        [
            {
                "id_policial": 1,
                "nome": "string",
                "email": "string",
                "senha": "string",
                "cargo_patente": "string",
                "matricula": "string"
            }
        ]
        ```
    """
    db = db_session()
    try:
        sql_p = (
            select(Policial, Cargo_Oficial)
            .join(Cargo_Oficial, Cargo_Oficial.id_cargo == Policial.cargo_patente)
        )
        result_policia = db.execute(sql_p).all()
        if not result_policia and result_policia != []:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_p = []
        for p, c in result_policia:
            lista_p.append({
                "policial": p.serialize(),
                "cargo": c.serialize()
            })
        return jsonify(lista_p), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_viaturas', methods=['GET'])
def get_viaturas():
    """
          **API para Consulta de Viaturas**

          ### Endpoint:
          GET /get_viaturas

          ### Parametros de Entrada:
          Não possui parâmetros de entrada.

          ### Respostas (JSON):
          * **200 OK:** Lista de viaturas retornada com sucesso.
            ```json
            [
                {
                    "id_viatura": 1,
                    "modelo": "string",
                    "ano": "string",
                    "placa": "string",
                    "prefixo": "string",
                    "km_atual": "float",
                    "status_atual": "string"
                }
            ]
            ```
        """
    db = db_session()
    try:
        sql_v = (
            select(Viatura, Carro_Modelo)
            .join(Carro_Modelo, Carro_Modelo.id_carro == Viatura.modelo_id)
        )
        result_viatura = db.execute(sql_v).all()
        print('asd', result_viatura)
        if not result_viatura and result_viatura != []:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_v = []
        for v, c in result_viatura:
            lista_v.append({
                "viatura": v.serialize(),
                "carro_modelo": c.serialize()
            })
        return jsonify(lista_v), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_itens', methods=['GET'])
def get_itens():
    """
          **API para Consulta de Itens de Manutenção**

          ### Endpoint:
          GET /get_itens

          ### Parametros de Entrada:
          Não possui parâmetros de entrada.

          ### Respostas (JSON):
          * **200 OK:** Lista de itens retornada com sucesso.
            ```json
            [
                {
                    "id_item": 1,
                    "nome_item": "string",
                    "descricao": "string",
                    "categoria_falha": "string",
                    "valor_unitario": "float"
                }
            ]
            ```
        """
    db = db_session()
    try:
        sql_i = (
            select(Itens_Manutencao, Categoria)
            .join(Categoria, Categoria.id_categoria == Itens_Manutencao.categoria_id)
        )
        result_itens = db.execute(sql_i).all()
        if not result_itens:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_i = []
        for i, c in result_itens:
            lista_i.append({
                "item": i.serialize(),
                "categoria": c.serialize()
            })
        return jsonify(lista_i), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_checklist', methods=['GET'])
def get_checklist():
    """
          **API para Consulta de Checklists**

          ### Endpoint:
          GET /get_checklist

          ### Parametros de Entrada:
          Não possui parâmetros de entrada.

          ### Respostas (JSON):
          * **200 OK:** Lista de checklists retornada com sucesso.
            ```json
            [
                {
                    "id_checklist": 1,
                    "data_hora": "1",
                    "nivel_oleo": "string",
                    "status_pneu": "string",
                    "relatorio_problema": "string",
                    "km_abertura": "float",
                    "policial_id": "integre",
                    "viatura_id": "integre"
                }
            ]
            ```
        """
    db = db_session()
    try:
        checklist_banco = select(Checklist_Turno)
        result_checklist = db.execute(checklist_banco).scalars()
        if not result_checklist:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_c = []
        for c in result_checklist:
            lista_c.append(c.serialize())
        return jsonify(lista_c), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {str(e)}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_ordem', methods=['GET'])
def get_ordem():
    """
              **API para Consulta de Ordem de Serviço**

              ### Endpoint:
              GET /get_ordem

              ### Parametros de Entrada:
              Não possui parâmetros de entrada.

              ### Respostas (JSON):
              * **200 OK:** Lista de ordem retornada com sucesso.
                ```json
                [
                    {
                        "id_ordem": 1,
                        "data_abertura": "string",
                        "data_fechamento": "string",
                        "status_os": "string",
                        "tipo_manutencao": "string",
                        "custo_total": "float",
                        "viatura_id": "integre",
                        "responsavel_id": "integre"
                    }
                ]
                ```
            """
    db = db_session()
    try:
        sql_o = select(Ordem_Servico)
        result_ordem = db.execute(sql_o).scalars()
        if not result_ordem:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_o = []
        for o in result_ordem:
            lista_o.append(o.serialize())
        return jsonify(lista_o), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_ordem_itens', methods=['GET'])
def get_ordem_itens():
    """
      **API para Consulta de Ordem_Itens**

      ### Endpoint:
      GET /get_ordem_itens

      ### Parametros de Entrada:
      Não possui parâmetros de entrada.

      ### Respostas (JSON):
      * **200 OK:** Lista de ordem_itens retornada com sucesso.
        ```json
        [
            {
                "id_lista": 1,
                "item_id": "integre",
                "item_id": "integre"
            }
        ]
        ```
    """
    db = db_session()
    try:
        sql_oi = select(Ordem_Itens)
        result_ordem_itens = db.execute(sql_oi).scalars()
        if not result_ordem_itens:
            return jsonify({'msg': "Credenciais invalidas"}), 400
        lista_oi = []
        for oi in result_ordem_itens:
            lista_oi.append(oi.serialize())
        return jsonify(lista_oi), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_carros', methods=['GET'])
def get_carros():
    """
      **API para Consulta de Carros**

      ### Endpoint:
      GET /get_carros

      ### Parametros de Entrada:
      Não possui parâmetros de entrada.

      ### Respostas (JSON):
      * **200 OK:** Lista de carro_modelo retornada com sucesso.
        ```json
        [
            {
                "id_carro": 1,
                "marca": "string",
                "modelo": "string"
            },
        ]
        ```
    """
    db = db_session()
    try:
        sql_cr = select(Carro_Modelo)
        result = db.execute(sql_cr).scalars()

        if not result:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        lista_carro = []

        for i in result:
            lista_carro.append(i.serialize())

        return jsonify(lista_carro), 200
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/get_cargos', methods=['GET'])
def get_cargos():
    """
      **API para Consulta de Carros**

      ### Endpoint:
      GET /get_carros

      ### Parametros de Entrada:
      Não possui parâmetros de entrada.

      ### Respostas (JSON):
      * **200 OK:** Lista de carro_modelo retornada com sucesso.
        ```json
        [
            {
                "id_carro": 1,
                "marca": "string",
                "modelo": "string"
            },
        ]
        ```
    """
    db = db_session()
    try:
        sql_cg = select(Cargo_Oficial)
        result_cargo = db.execute(sql_cg).scalars()

        if not result_cargo:
            return jsonify({'msg': "Valores não encontrados"}), 400

        lista_cg = []
        for cg in result_cargo:
            lista_cg.append(cg.serialize())

        return jsonify(lista_cg), 200
    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500
    finally:
        db_session.close()


@app.route('/get_categorias', methods=['GET'])
def get_categorias():
    """
          **API para Consulta de Carros**

          ### Endpoint:
          GET /get_carros

          ### Parametros de Entrada:
          Não possui parâmetros de entrada.

          ### Respostas (JSON):
          * **200 OK:** Lista de carro_modelo retornada com sucesso.
            ```json
            [
                {
                    "id_carro": 1,
                    "marca": "string",
                    "modelo": "string"
                },
            ]
            ```
        """
    db = db_session()
    try:
        sql_cg = select(Categoria)
        result_categ = db.execute(sql_cg).scalars()

        if not result_categ:
            return jsonify({'msg': "Valores não encontrados"}), 400

        lista_cg = []
        for cg in result_categ:
            lista_cg.append(cg.serialize())

        return jsonify(lista_cg), 200
    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/info_viatura/<var_id>', methods=['GET'])
def info_viatura(var_id):
    db = db_session()
    try:
        print(var_id)
        sql_vi = (
            select(Viatura, Carro_Modelo)
            .join(Carro_Modelo, Carro_Modelo.id_carro == Viatura.modelo_id)
            .where(Viatura.id_viatura == var_id)
        )
        result_via = db.execute(sql_vi).all()

        if not result_via:
            return jsonify({'msg': "Valores não encontrados"}), 400

        lista_vi = []
        for vi,mv in result_via:
            lista_vi.append({
                "viatura":vi.serialize(),
                "carro_modelo":mv.serialize()
            })

        return jsonify(lista_vi), 200
    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/log_policial/<var_id>',methods=['GET'])
def obter_policial(var_id):
    policial = db_session.get(Policial, int(var_id))

    if policial:
        return jsonify(policial.serialize()), 200
    return jsonify({"msg": "Policial não encontrada"}), 404

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"msg": "Dados não encontrados"}), 400

    email = dados.get('email')
    senha = dados.get('senha')
    print('user',email, senha)

    if not email or not senha:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Policial).where(Policial.email == email)
        result_policia = db_session.execute(sql_p).scalars().first()

        if result_policia and result_policia.check_password_hash(senha):
            return jsonify({
                'msg': "Policial Encontrado",
                "user": result_policia.serialize()
            }), 201

        return jsonify({"msg": "Policial não Encontrado"}), 400
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_policial', methods=['POST'])
def post_policial():
    """
        **API para Cadastro de Policial**

        ### Endpoint:
        POST /post_policial

        ### Parâmetros de Entrada (JSON):
        ```json
        {
            "nome": "string (obrigatorio) - Nome do policial",
            "email": "string (obrigatorio) - Endereço de e-mail do policial",
            "senha": "string (obrigatorio) - Senha para acesso ao sistema",
            "cargo_patente": "string (obrigatorio) - Cargo de acesso do policial"
        }
        ```

        ### Respostas (JSON):
        * **200 Created:** Policial registrada com sucesso.
          ```json
          {
              "msg": "Policial criado com sucesso",
              "id": policial.id_policial
          }
          ```
        * **400 Bad Request:** Ausencia de campos obrigatorios ou policial ja cadastrada.
          ```json
          {
              "msg": "Valor não Encontrado"
          }
          ```
        * **500 Internal Server Error:** Falha operacional no banco de dados.
          ```json
          {
              "msg": "[Descricao do Erro]"
          }
          ```
        """
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cargo_patente = dados.get('cargo_patente')
    matricula = gerar_codigo('pm', 5)

    if not nome or not email or not senha or not cargo_patente or not matricula:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Policial).where(Policial.email == email)
        result_policia = db_session.execute(sql_p).scalar()

        if result_policia:
            return jsonify({'msg': "Este policial já existe"}), 400

        new_p = Policial(nome=nome, email=email, cargo_patente=int(cargo_patente), matricula=matricula)
        new_p.set_senha_hash(senha)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Policial criado com sucesso",
            "id": new_p.id_policial
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_viatura', methods=['POST'])
def post_viatura():
    """
        **API para Cadastro de Viatura**

        ### Endpoint:
        POST /post_viatura

        ### Parâmetros de Entrada (JSON):
        ```json
        {
            "placa": "string (obrigatorio) - Identificacao oficial do viatura",
            "ano": "string (obrigatorio) - Ano de fabricacao",
            "km_atual": "float (obrigatorio) - Numero da quilometragem da viatura",
            "modelo": "string (obrigatorio) - Modelo da viatura",
            "status_atual": "string (obrigatorio) - Status atual da viatura"
        }
        ```

        ### Respostas (JSON):
        * **200 Created:** Viatura registrada com sucesso.
          ```json
          {
              "msg": "Viatura criada com sucesso",
              "id": viatura.id_viatura
          }
          ```
        * **400 Bad Request:** Ausencia de campos obrigatorios ou policial ja cadastrada.
          ```json
          {
              "msg": "Valor não Encontrado"
          }
          ```
        * **500 Internal Server Error:** Falha operacional no banco de dados.
          ```json
          {
              "msg": "[Descricao do Erro]"
          }
          ```
    """
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    placa = dados.get('placa')
    ano = dados.get('ano')
    km_atual = dados.get('km_atual')
    prefixo = gerar_codigo('vtr', 4)
    modelo = dados.get('modelo')

    if not placa or not ano or not km_atual or not prefixo or not modelo:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        sql_p = select(Viatura).where(Viatura.placa == placa)
        result_viatura = db_session.execute(sql_p).scalar()

        if result_viatura:
            return jsonify({'msg': "Esta viatura já existe"}), 400

        new_v = Viatura(placa=placa, ano=ano, km_atual=km_atual, prefixo=prefixo, modelo_id=int(modelo))
        db_session.add(new_v)
        db_session.commit()

        info = {
            "msg": "Viatura criada com sucesso",
            "id": new_v.id_viatura
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_item', methods=['POST'])
def post_item():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    nome_item = dados.get('nome_item')
    descricao = dados.get('descricao')
    categoria_id = dados.get('categoria_id')
    valor_unitario = dados.get('valor_unitario')

    if not nome_item or not descricao or not categoria_id or not valor_unitario:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Itens_Manutencao(nome_item=nome_item, descricao=descricao, categoria_id=int(categoria_id),
                                 valor_unitario=valor_unitario)
        db_session.add(new_p)
        db_session.commit()
        info = {
            "msg": "Item de manutenção criado com sucesso",
            "ID": new_p.id_item
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_checklist', methods=['POST'])
def post_checklist():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    viatura_id = dados.get('viatura_id')
    policial_id = dados.get('policial_id')
    nivel_oleo = dados.get('nivel_oleo')
    status_pneu = dados.get('status_pneu')
    giroflex = dados.get('giroflex')
    sirene = dados.get('sirene')
    radio = dados.get('radio')
    kit_emergencia = dados.get('kit_emergencia')
    km_abertura = dados.get('km_abertura')
    relatorio_problema = dados.get('relatorio_problema')

    if not nivel_oleo or not viatura_id or not policial_id or not status_pneu or not km_abertura or not relatorio_problema or not giroflex or not sirene or not radio or not kit_emergencia:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Checklist_Turno(viatura_id=viatura_id, policial_id=policial_id, nivel_oleo=nivel_oleo,
                                status_pneu=status_pneu,giroflex=giroflex,sirene=sirene,radio=radio,kit_emergencia=kit_emergencia, km_abertura=km_abertura, relatorio_problema=relatorio_problema)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Checklist criado com sucesso",
            "ID": new_p.id_checklist
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_ordem_servico', methods=['POST'])
def post_ordem_servico():
    dados = request.get_json()
    if not dados:
        return jsonify({'msg': "Dados não encontrados"}), 400
    viatura_id = dados.get('viatura_id')
    policial_id = dados.get('policial_id')
    tipo_manutencao = dados.get('tipo_manutencao')
    status_os = dados.get('status_os')
    custo_total = dados.get('custo_total')

    if not viatura_id or not policial_id or not tipo_manutencao or not status_os or not custo_total:
        return jsonify({'msg': "Credenciais invalidas"}), 400

    try:
        new_p = Ordem_Servico(viatura_id=viatura_id, policial_id=policial_id, tipo_manutencao=tipo_manutencao,
                              status_os=status_os, custo_total=custo_total)
        db_session.add(new_p)
        db_session.commit()

        info = {
            "msg": "Ordem de serviço criado com sucesso",
            "ID": new_p.id_ordem
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


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
            "msg": "Ordem de itens criado com sucesso",
            "ID": new_p.id_lista
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_cargo', methods=['POST'])
def post_cargo():
    dados = request.get_json()
    if not dados:
        return jsonify({"msg": "Credenciais invalidas"}), 400
    nome_cargo = dados.get('nome_cargo')
    categoria = dados.get('categoria')

    if not nome_cargo or not categoria:
        return jsonify({"msg": "Credenciais invalidas"}), 400

    try:
        new_c = Cargo_Oficial(nome_cargo=nome_cargo, categoria=categoria)
        db_session.add(new_c)
        db_session.commit()

        info = {
            "msg": "Ordem de itens criado com sucesso",
            "ID": new_c.id_cargo
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_modelo', methods=['POST'])
def post_modelo():
    dados = request.get_json()
    if not dados:
        return jsonify({"msg": "Credenciais invalidas"}), 400
    modelo = dados.get('modelo')
    marca = dados.get('marca')

    if not modelo or not marca:
        return jsonify({"msg": "Credenciais invalidas"}), 400

    try:
        new_m = Carro_Modelo(modelo=modelo, marca=marca)
        db_session.add(new_m)
        db_session.commit()

        info = {
            "msg": "Ordem de itens criado com sucesso",
            "ID": new_m.id_carro
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/post_categoria', methods=['POST'])
def post_categoria():
    dados = request.get_json()
    if not dados:
        return jsonify({"msg": "Credenciais invalidas"}), 400
    nome_categ = dados.get('nome_categ')

    if not nome_categ:
        return jsonify({"msg": "Credenciais invalidas"}), 400

    try:
        new_c = Categoria(nome_categoria=nome_categ)
        db_session.add(new_c)
        db_session.commit()

        info = {
            "msg": "Ordem de itens criado com sucesso",
            "ID": new_c.id_categoria
        }

        return jsonify(info), 201
    except Exception as e:
        db_session.rollback()
        print(f'Error: {e}')
        return jsonify({'msg': str(e)}), 500


@app.route('/put_policial/<var_id>', methods=['PUT'])
def put_policial(var_id):
    """
    **API para Atualização de Dados do Policial**

    ### Endpoint:
    PUT /put_policial/{var_id}

    ### Parâmetros de Path:
    * `var_id`: inteiro (obrigatório) - Identificador único do policial que será atualizado.

    ### Parâmetros de Entrada (JSON):
    ```json
    {
        "nome": "string (opcional) - Nome atualizado do policial",
        "email": "string (opcional) - Novo endereço de e-mail do policial",
        "senha": "string (opcional) - Nova senha para acesso ao sistema",
        "cargo_patente": "string (opcional) - Novo cargo de acesso do policial"
    }
    ```

    ### Respostas (JSON):
    * **200 OK:** Dados do policial atualizados com sucesso.
      ```json
      {
          "msg": "Policial atualizado com sucesso",
          "id": policial.id_policial
      }
      ```
    * **400 Bad Request:** Formato de dados inválido ou e-mail já em uso por outro usuário.
      ```json
      {
          "msg": "Valor não Encontrado"
      }
      ```
    * **404 Not Found:** Policial com o ID fornecido não foi encontrado no sistema.
      ```json
      {
          "msg": "Policial não encontrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "[Descricao do Erro]"
      }
      ```
    """
    editar = select(Policial).where(Policial.id_policial == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Policial não encontrado"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        cargo_patente = dados.get('cargo_patente')

        if not nome or not email or not cargo_patente:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.nome = nome
            result.email = email
            result.cargo_patente = int(cargo_patente)
            db_session.commit()
            return jsonify({"msg": "Policial atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500


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
        modelo = dados.get('modelo')

        if not placa or not ano or not km_atual or not modelo:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.placa = placa
            result.ano = ano
            result.km_atual = km_atual
            result.modelo_id = modelo
            db_session.commit()
            return jsonify({"msg": "Viatura atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500


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


@app.route('/put_ordem_servico/<var_id>', methods=['PUT'])
def put_ordem_servico(var_id):
    editar = select(Ordem_Servico).where(Ordem_Servico.id_ordem == int(var_id))
    result = db_session.execute(editar).scalar_one_or_none()

    if not result:
        return jsonify({"msg": "Ordem de serviço não encontrados"}), 400

    if request.method == 'PUT':
        dados = request.get_json()
        viatura_id = dados.get('viatura_id')
        policial_id = dados.get('policial_id')
        tipo_manutencao = dados.get('tipo_manutencao')
        status_os = dados.get('status_os')
        custo_total = dados.get('custo_total')
        if not viatura_id or not policial_id or not tipo_manutencao or not status_os or not custo_total:
            return jsonify({'msg': "Credenciais invalidas"}), 400

        try:
            result.viatura_id = viatura_id
            result.policial_id = policial_id
            result.tipo_manutencao = tipo_manutencao
            result.status_os = status_os
            result.custo_total = custo_total
            db_session.commit()
            return jsonify({"msg": "Ordem de serivço atualizado com sucesso!"}), 200

        except Exception as e:
            db_session.rollback()
            print(f'Error: {e}')
            return jsonify({'msg': str(e)}), 500


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


@app.route('/delete_policial/<var_id>', methods=['DELETE'])
def delete_policial(var_id):
    """
    **API para Remoção de Policial**

    ### Endpoint:
    DELETE /delete_policial/{id}

    ### Parâmetros de Path:
    * `id`: inteiro (obrigatório) - Identificador único do policial que será removido.

    ### Respostas (JSON):
    * **200 OK:** Policial removido com sucesso.
      ```json
      {
          "msg": "Policial removido com sucesso",
          "id": policial.id_policial
      }
      ```
    * **400 Bad Request:** Requisição inválida ou erro na sintaxe dos parâmetros.
      ```json
      {
          "msg": "Valor não Encontrado"
      }
      ```
    * **404 Not Found:** Policial com o ID fornecido não foi encontrado no sistema.
      ```json
      {
          "msg": "Policial não encontrado"
      }
      ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
      ```json
      {
          "msg": "[Descricao do Erro]"
      }
      ```
    """
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


@app.route('/delete_item/<var_id>', methods=['DELETE'])
def delete_item(var_id):
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


@app.route('/pesquisar_policial', methods=['POST'])
def pesquisar_policial():
    dados = request.get_json()
    nome = dados.get('nome')
    if not nome:
        return jsonify({"msg": "Nenhum policial encontrado"}), 400
    try:
        busca = (
            select(Policial, Cargo_Oficial)
            .join(Cargo_Oficial, Cargo_Oficial.id_cargo == Policial.cargo_patente)
            .where(Policial.nome.ilike(f'%{nome}%'))
        )
        rastreio = db_session.execute(busca).all()
        lista_p = []
        for p, c in rastreio:
            lista_p.append({
                "policial": p.serialize(),
                "cargo": c.serialize()
            })
        return jsonify(lista_p), 200
    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500


@app.route('/pesquisar_viatura', methods=['POST'])
def pesquisar_viatura():
    dados = request.get_json()
    prefixo = dados.get('prefixo')
    if not prefixo:
        return jsonify({"msg": "Prefixo não encontrado"}), 400
    db = db_session()
    try:
        busca = (
            select(Viatura, Carro_Modelo)
            .join(Carro_Modelo, Carro_Modelo.id_carro == Viatura.modelo_id)
            .where(Viatura.prefixo == f"VTR-{prefixo}")
        )
        rastreio = db.execute(busca).all()
        if not rastreio:
            return jsonify("Nenhuma viatura encontrada"), 400

        lista = []
        for r, c in rastreio:
            lista.append({
                "viatura": r.serialize(),
                "carro_modelo": c.serialize()
            })

        db.commit()
        return jsonify(lista), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500


@app.route('/pesquisar_itens', methods=['POST'])
def pesquisar_itens():
    dados = request.get_json()
    item_nome = dados.get('nome_item')

    if not item_nome:
        return jsonify({"msg": "Nenhum item encontrado"}), 400

    try:
        busca = (
            select(Itens_Manutencao,Categoria)
            .join(Categoria, Categoria.id_categoria == Itens_Manutencao.categoria_id)
            .where(Itens_Manutencao.nome_item.ilike(f'%{item_nome}%'))
        )

        rastreio = db_session.execute(busca).all()
        lista = []
        for i,c in rastreio:
            lista.append({
                "item":i.serialize(),
                "categoria": c.serialize()
            })

        db_session.commit()
        return jsonify(lista), 200

    except Exception as e:
        print(f'Error: {e}')
        db_session.rollback()
        return jsonify({'msg': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5005, host='0.0.0.0')
