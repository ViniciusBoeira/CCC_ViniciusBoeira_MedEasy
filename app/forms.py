from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError 
from wtforms.fields import DateTimeLocalField
from wtforms_sqlalchemy.fields import QuerySelectField
from .models import Medico
import datetime 

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
    
    # Validador de Horário (8:00-11:00 e 13:00-17:30)
    def validate_data_hora(self, field):
        data_hora = field.data
        hora = data_hora.time()
        
        inicio_manha = datetime.time(8, 0)
        fim_manha = datetime.time(11, 0)
        inicio_tarde = datetime.time(13, 0)
        fim_tarde = datetime.time(17, 30)

        manha_valida = inicio_manha <= hora <= fim_manha
        tarde_valida = inicio_tarde <= hora <= fim_tarde

        if not manha_valida and not tarde_valida:
            raise ValidationError('A consulta deve ser agendada entre 08:00 e 11:00 ou entre 13:00 e 17:30.')


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
        choices=[('Agendada', 'Agendada'), ('Confirmada', 'Confirmada'), ('Finalizada', 'Finalizada'), ('Cancelada', 'Cancelada')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Salvar Alterações')

    # Validador de Horário (8:00-11:00 e 13:00-17:30)
    def validate_data_hora(self, field):
        data_hora = field.data
        hora = data_hora.time()
        
        inicio_manha = datetime.time(8, 0)
        fim_manha = datetime.time(11, 0)
        inicio_tarde = datetime.time(13, 0)
        fim_tarde = datetime.time(17, 30)

        manha_valida = inicio_manha <= hora <= fim_manha
        tarde_valida = inicio_tarde <= hora <= fim_tarde

        if not manha_valida and not tarde_valida:
            raise ValidationError('A consulta deve ser agendada entre 08:00 e 11:00 ou entre 13:00 e 17:30.')

    
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