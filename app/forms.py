from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.fields import DateTimeLocalField
from wtforms_sqlalchemy.fields import QuerySelectField
from .models import Medico

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class CadastroPacienteForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=11)])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        EqualTo('password2', message='As senhas devem ser iguais.')
    ])
    password2 = PasswordField('Confirme a Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')


class CadastroMedicoForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    crm = StringField('CRM', validators=[DataRequired()])
    especialidade = StringField('Especialidade', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        EqualTo('password2', message='As senhas devem ser iguais.')
    ])
    password2 = PasswordField('Confirme a Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

# Função para obter a lista de médicos para o formulário
def get_medicos():
    return Medico.query.all()

class AgendamentoForm(FlaskForm):
    # Este campo especial irá carregar os médicos diretamente do banco
    medico = QuerySelectField(
        'Médico',
        query_factory=get_medicos,
        get_label='name', # O que será exibido na lista
        allow_blank=False,
        validators=[DataRequired()]
    )
    data_hora = DateTimeLocalField(
        'Data e Hora da Consulta',
        format='%Y-%m-%dT%H:%M', # Formato esperado pelo campo HTML5
        validators=[DataRequired()]
    )
    submit = SubmitField('Agendar Consulta')