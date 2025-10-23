import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
    # Discriminator para saber se o usuário é Médico ou Paciente
    user_type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Métodos exigidos pelo Flask-Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.name}>'


class Medico(User):
    __tablename__ = 'medicos'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    crm = db.Column(db.String(50), unique=True, nullable=False)
    especialidade = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity': 'medico',
    }

    def __repr__(self):
        return f'<Medico {self.name}, CRM: {self.crm}>'


class Paciente(User):
    __tablename__ = 'pacientes'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    data_nascimento = db.Column(db.DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'paciente',
    }

    def __repr__(self):
        return f'<Paciente {self.name}, CPF: {self.cpf}>'
    
class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = db.Column(db.String(50), default='Agendada', nullable=False)
    
    # Chaves estrangeiras
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)

    # Relacionamentos (para facilitar o acesso aos objetos)
    paciente = db.relationship('Paciente', backref=db.backref('consultas', lazy=True))
    medico = db.relationship('Medico', backref=db.backref('consultas', lazy=True))
    
    receitas = db.relationship('Receita', backref='consulta', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Consulta {self.id} - {self.paciente.name} com {self.medico.name} em {self.data_hora}>' 
    
class Evolucao(db.Model):
    __tablename__ = 'evolucoes'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Chave estrangeira para a consulta
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    # Chave estrangeira para o médico que escreveu
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)

    # Relacionamentos
    consulta = db.relationship('Consulta', backref=db.backref('evolucoes', lazy='dynamic', cascade="all, delete-orphan"))
    medico = db.relationship('Medico', backref=db.backref('evolucoes', lazy=True))

    def __repr__(self):
        return f'<Evolucao {self.id} da Consulta {self.consulta_id}>'

class Receita(db.Model):
    __tablename__ = 'receitas'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    
    # Chave estrangeira para a consulta
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    
    def __repr__(self):
        return f'<Receita {self.id} da Consulta {self.consulta_id}>'
