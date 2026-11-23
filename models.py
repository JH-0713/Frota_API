from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, relationship
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/banco_frota', pool_size=10, max_overflow=20)

Base = declarative_base()
db_session = scoped_session(sessionmaker(bind=engine))

class Cargo_Oficial(Base):
    __tablename__ = 'cargo_oficial'
    id_cargo = Column(Integer, primary_key=True)
    nome_cargo = Column(String(255), nullable=False)
    categoria = Column(String(255), nullable=False)
    permicao = Column(String(255), nullable=False)

    policiais = relationship("Policial", back_populates="cargo")

    def serialize(self):
        dados = {
            "id_cargo": self.id_cargo,
            "nome_cargo": self.nome_cargo,
            "categoria": self.categoria,
            "permicao": self.permicao,
        }

        return dados

class Policial(Base):
    __tablename__ = 'policial'
    id_policial = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    senha = Column(Text, nullable=False)
    cargo_patente = Column(Integer, ForeignKey('cargo_oficial.id_cargo'))
    matricula = Column(String(50), nullable=False)

    cargo = relationship("Cargo_Oficial", back_populates="policiais")
    checklists = relationship("Checklist_Turno", back_populates="policial")
    ordens_servico = relationship("Ordem_Servico", back_populates="policial")

    def set_senha_hash(self, senha):
        self.senha = generate_password_hash(senha)

    def check_password_hash(self, senha):
        return check_password_hash(self.senha, senha)

    def serialize(self):
        dados = {
            'id_policial': self.id_policial,
            'nome': self.nome,
            'email': self.email,
            'senha': self.senha,
            'cargo_patente': self.cargo.nome_cargo,
            'matricula': self.matricula,
        }
        return dados

class Carro_Modelo(Base):
    __tablename__ = "carro_modelo"
    id_carro = Column(Integer, primary_key=True)
    modelo = Column(String(255), nullable=False)
    marca = Column(String(255), nullable=False)

    viaturas = relationship("Viatura", back_populates="modelo_fk")

    def serialize(self):
        return {
            "id_carro": self.id_carro,
            "modelo": self.modelo,
            "marca": self.marca
        }

class Viatura(Base):
    __tablename__ = 'viatura'
    id_viatura = Column(Integer, primary_key=True)
    placa = Column(String(255), nullable=False)
    ano = Column(String(255), nullable=False)
    km_atual = Column(Float, nullable=False)
    prefixo = Column(String(125), nullable=False)
    modelo_id = Column(Integer, ForeignKey('carro_modelo.id_carro'))
    status_atual = Column(Enum('disponivel','oficina','atencao'),default="disponivel", nullable=False)

    modelo_fk = relationship("Carro_Modelo", back_populates="viaturas")
    checklists = relationship("Checklist_Turno", back_populates="viatura")
    ordens_servico = relationship("Ordem_Servico", back_populates="viatura")

    def serialize(self):
        dados = {
            "id_viatura": self.id_viatura,
            "placa": self.placa,
            "ano": self.ano,
            "km_atual": self.km_atual,
            "prefixo": self.prefixo,
            "modelo": self.modelo_fk.modelo,
            "status_atual": self.status_atual,
        }
        return dados

class Categoria(Base):
    __tablename__ = 'categoria'
    id_categoria = Column(Integer,primary_key=True)
    nome_categoria = Column(String(255), nullable=False)

    itens = relationship("Itens_Manutencao", back_populates="categoria")

    def serialize(self):
        return {
            "id_categoria": self.id_categoria,
            "nome_categoria": self.nome_categoria
        }

class Itens_Manutencao(Base):
    __tablename__ = 'itens_manutencao'
    id_item = Column(Integer, primary_key=True)
    nome_item = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria_id = Column(Integer,ForeignKey('categoria.id_categoria'))
    valor_unitario = Column(Float, nullable=False)

    categoria = relationship("Categoria", back_populates="itens")
    ordem_itens = relationship("Ordem_Itens", back_populates="item")

    def serialize(self):
        dados = {
            "id_item": self.id_item,
            "nome_item": self.nome_item,
            "descricao": self.descricao,
            "categoria": self.categoria.nome_categoria,
            "valor_unitario": self.valor_unitario,

        }
        return dados

class Checklist_Turno(Base):
    __tablename__ = 'checklist_turno'
    id_checklist = Column(Integer, primary_key=True)
    viatura_id = Column(Integer, ForeignKey('viatura.id_viatura'))
    policial_id = Column(Integer, ForeignKey('policial.id_policial'))
    data_hora = Column(DateTime,default=func.now(), nullable=False)
    nivel_oleo = Column(Enum('alto','medio','baixo'), nullable=False)
    status_pneu = Column(Enum('ok','intermediario','ruim'), nullable=False)
    giroflex = Column(Enum('ok','falta'), nullable=False)
    sirene = Column(Enum('ok','falta'), nullable=False)
    radio = Column(Enum('ok','falta'), nullable=False)
    kit_emergencia = Column(Enum('ok','falta'), nullable=False)
    km_abertura = Column(Float, nullable=False)
    relatorio_problema = Column(Text, nullable=False)

    viatura = relationship("Viatura", back_populates="checklists")
    policial = relationship("Policial", back_populates="checklists")


    def serialize(self):
        dados = {
            "id_checklist": self.id_checklist,
            "viatura": self.viatura.serialize(),
            "policial": self.policial.serialize(),
            "data_hora": self.data_hora,
            "nivel_oleo": self.nivel_oleo,
            "status_pneu": self.status_pneu,
            "giroflex": self.giroflex,
            "sirene": self.sirene,
            "radio": self.radio,
            "kit_emergencia": self.kit_emergencia,
            "km_abertura": self.km_abertura,
            "relatorio_problema": self.relatorio_problema,

        }
        return dados


class Ordem_Servico(Base):
    __tablename__ = 'ordem_servico'
    id_ordem = Column(Integer, primary_key=True)
    viatura_id = Column(Integer, ForeignKey('viatura.id_viatura'))
    policial_id = Column(Integer, ForeignKey('policial.id_policial'))
    data_abertura = Column(DateTime, nullable=False, default=func.now())
    data_fechamento = Column(DateTime)
    tipo_manutencao = Column(Enum('preventiva','corretiva'), nullable=False)
    status_os = Column(Enum('andamento','concluida'), nullable=False)
    custo_total = Column(Float, nullable=False)

    viatura = relationship("Viatura", back_populates="ordens_servico")
    policial = relationship("Policial", back_populates="ordens_servico")
    ordem_itens = relationship("Ordem_Itens", back_populates="ordem")

    def serialize(self):
        dados = {
            "id_ordem": self.id_ordem,
            "viatura": self.viatura.serialize(),
            "policial": self.policial.serialize(),
            "data_abertura": self.data_abertura,
            "data_fechamento": self.data_fechamento,
            "tipo_manutencao": self.tipo_manutencao,
            "status_os": self.status_os,
            "custo_total": self.custo_total,

        }
        return dados


class Ordem_Itens(Base):
    __tablename__ = 'ordem_itens'
    id_lista = Column(Integer, primary_key=True)
    os_id = Column(Integer, ForeignKey('ordem_servico.id_ordem'))
    item_id = Column(Integer, ForeignKey('itens_manutencao.id_item'))

    ordem = relationship("Ordem_Servico", back_populates="ordem_itens")
    item = relationship("Itens_Manutencao", back_populates="ordem_itens")

    def serialize(self):
        dados = {
            "id_lista": self.id_lista,
            "ordem": self.ordem.serialize(),
            "item": self.item.serialize(),

        }
        return dados