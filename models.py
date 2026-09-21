from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship
from werkzeug.security import generate_password_hash, check_password_hash

"""
##Base de dados link local(model) SQLITE
"""
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/banco_frota',pool_size=10, max_overflow=20)

# Banco MySQL
Base = declarative_base()

db_session = scoped_session(sessionmaker(bind=engine))

class Policial(Base):
    __tablename__ = 'policial'
    id_policial = Column(Integer, primary_key=True)
    nome = Column(String(255),nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(Text, nullable=False)
    cargo_patente = Column(String(125), nullable=False)
    matricula = Column(Integer,nullable=False)

    def set_senha_hash(self, senha):
        self.senha = generate_password_hash(senha)

    def check_password_hash(self,senha):
        return check_password_hash(self.senha,senha)

    def serializar(self):
        dados = {
            "id_policial": self.id_policial,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "cargo_patente": self.cargo_patente,
            "matricula": self.matricula
        }
        return dados


class Viatura(Base):
    __tablename__ = 'viatura'
    id_viatura = Column(Integer, primary_key=True)
    modelo = Column(String(255), nullable=False)
    prefixo = Column(String(50), nullable=False)
    placa = Column(String(50), nullable=False)
    ano = Column(String(10), nullable=False)
    km_atual = Column(Float, nullable=False)
    status_atual = Column(Enum('disponivel','oficina','atencao'),default='disponivel', nullable=False)


    def serializar(self):
        dados = {
            "id_viatura": self.id_viatura,
            "modelo": self.modelo,
            "prefixo": self.prefixo,
            "placa": self.placa,
            "ano": self.ano,
            "km_atual": self.km_atual,
            "status_atual": self.status_atual
        }
        return dados

class Responsavel(Base):
    __tablename__ = 'responsavel'
    id_responsavel = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255),unique=True, nullable=False)
    senha = Column(Text, nullable=False)
    cargo_funcao = Column(String(150), nullable=False)

    def set_senha_hash(self, senha):
        self.senha = generate_password_hash(senha)

    def check_password_hash(self,senha):
        return check_password_hash(self.senha,senha)

    def serializar(self):
        dados = {
            "id_responsavel": self.id_responsavel,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "cargo_funcao": self.cargo_funcao
        }
        return dados

class Itens_Manutencao(Base):
    __tablename__ = 'itens_manutencao'
    id_item = Column(Integer, primary_key=True)
    nome_item = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria_falha = Column(Enum('motor','cambio','embreagem','freio','suspensao','direcao','bateria','injecao_eletronica','iluminacao','ar_condicionado','arrefecimento','alimentacao'), nullable=False)
    valor_unitario = Column(Float, nullable=False)

    def serialize(self):
        dados = {
            "id_item": self.id_item,
            "nome_item": self.nome_item,
            "descricao": self.descricao,
            "categoria_falha": self.categoria_falha,
            "valor_unitario": self.valor_unitario
        }
        return dados

class Checklist_Turno(Base):
    __tablename__ = 'checklist_turno'
    id_checklist = Column(Integer, primary_key=True)
    viatura_id = Column(Integer, ForeignKey('viatura.id_viatura'))
    policial_id = Column(Integer, ForeignKey('policial.id_policial'))
    data_hora = Column(DateTime, nullable=False, default=func.now())
    nivel_oleo = Column(Enum('alto','medio','baixo'), nullable=False)
    status_pneu = Column(Enum('ok','intermediario','ruim'), nullable=False)
    giroflex = Column(Enum('ok','falta'), nullable=False)
    sirene = Column(Enum('ok','falta'), nullable=False)
    radio = Column(Enum('ok','falta'), nullable=False)
    kit_emergencia = Column(Enum('ok','falta'), nullable=False)
    status_checklist = Column(Enum('dia','noite'), default='dia', nullable=False)
    km_abertura = Column(Float, nullable=False)
    relatorio_problema = Column(Text, nullable=False)

    def serializar(self):
        dados = {
            "id_checklist": self.id_checklist,
            "id_viatura": self.viatura_id,
            "policial_id": self.policial_id,
            "data_hora": self.data_hora,
            "nivel_oleo": self.nivel_oleo,
            "status_pneu": self.status_pneu,
            "giroflex": self.giroflex,
            "sirene": self.sirene,
            "radio": self.radio,
            "kit_emergencia": self.kit_emergencia,
            "status_checklist": self.status_checklist,
            "km_abertura": self.km_abertura,
            "relatorio_problema": self.relatorio_problema
        }
        return dados

class Ordem_Servico(Base):
    __tablename__ = 'ordem_servico'
    id_ordem = Column(Integer, primary_key=True)
    viatura_id = Column(Integer, ForeignKey('viatura.id_viatura'))
    responsavel_id = Column(Integer, ForeignKey('responsavel.id_responsavel'))
    data_abertura = Column(DateTime, nullable=False, default=func.now())
    data_fechamento = Column(DateTime)
    tipo_manutencao = Column(Enum('preventiva','correntiva'),nullable=False)
    status_os = Column(Enum('andamento','concluida'),nullable=False)
    custo_total = Column(Float, nullable=False)

    def serializar(self):
        dados = {
            "id_ordem": self.id_ordem,
            "viatura_id": self.viatura_id,
            "responsavel_id": self.responsavel_id,
            "data_abertura": self.data_abertura,
            "data_fechamento": self.data_fechamento,
            "tipo_manutencao": self.tipo_manutencao,
            "status_os": self.status_os,
            "custo_total": self.custo_total
        }
        return dados

class Ordem_Itens(Base):
    __tablename__ = 'ordem_itens'
    id_os_item = Column(Integer, primary_key=True)
    os_id = Column(Integer, ForeignKey('ordem_servico.id_ordem'))
    item_id = Column(Integer, ForeignKey('itens_manutencao.id_item'))

    def serializar(self):
        dados = {
            "id_os_item": self.id_os_item,
            "os_id": self.os_id,
            "item_id": self.item_id
        }
        return dados