from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
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

# Helper para os formulários de consulta
def get_medicos():
    return Medico.query.all()

class AgendamentoForm(FlaskForm):
    medico = QuerySelectField(
        'Médico', 
        query_factory=get_medicos, 
        get_label='name', 
        allow_blank=False,
        validators=[DataRequired()]
    )
    data_hora = DateTimeLocalField(
        'Data e Hora da Consulta',
        format='%Y-%m-%dT%H:%M', 
        validators=[DataRequired()]
    )
    submit = SubmitField('Agendar Consulta')

class EditarConsultaForm(FlaskForm):
    medico = QuerySelectField(
        'Médico',
        query_factory=get_medicos,
        get_label='name',
        allow_blank=False,
        validators=[DataRequired()]
    )
    data_hora = DateTimeLocalField(
        'Data e Hora da Consulta',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    status = SelectField(
        'Status',
        # Adicionamos 'Finalizada' às opções
        choices=[('Agendada', 'Agendada'), ('Confirmada', 'Confirmada'), ('Finalizada', 'Finalizada'), ('Cancelada', 'Cancelada')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Salvar Alterações')
    
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit') 

class EvolucaoForm(FlaskForm):
    conteudo = TextAreaField('Conteúdo da Evolução', validators=[DataRequired()])
    submit_evolucao = SubmitField('Salvar Evolução')

class PrescriptionForm(FlaskForm):
    """
    Formulário para médicos adicionarem uma prescrição (receita) a uma consulta.
    """
    descricao = TextAreaField('Descrição da Receita', validators=[DataRequired()])
    submit_receita = SubmitField('Salvar Receita')
