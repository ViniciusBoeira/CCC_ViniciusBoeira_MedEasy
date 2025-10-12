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
