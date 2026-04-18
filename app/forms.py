from flask_wtf import FlaskForm # [SEGURANÇA] Todo formulário que herda FlaskForm ganha automaticamente um campo oculto com token CSRF
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


# [SEGURANÇA] Função auxiliar que valida a força da senha.
# Exige mínimo de 8 caracteres e proíbe sequências numéricas consecutivas.
def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida a senha com as seguintes regras:
    - Mínimo de 8 caracteres
    - Não pode conter sequências numéricas (123, 456, 321, etc)
    """
    if len(senha) < 8:
        return False, 'A senha deve ter no mínimo 8 caracteres.'

    # [SEGURANÇA] Cria a lista ['012','123','234','345','456','567','678','789']
    # Cada item é formado por 3 dígitos consecutivos crescentes (i, i+1, i+2)
    sequencias_crescentes = [str(i) + str(i+1) + str(i+2) for i in range(0, 8)]

    # [SEGURANÇA] Cria a lista ['987','876','765','654','543','432','321','210']
    # Cada item é formado por 3 dígitos consecutivos decrescentes (i, i-1, i-2)
    sequencias_decrescentes = [str(i) + str(i-1) + str(i-2) for i in range(9, 1, -1)]

    for seq in sequencias_crescentes + sequencias_decrescentes:
        if seq in senha:
            return False, f'A senha não pode conter sequências numéricas como "{seq}".'

    # Se passou por todas as verificações sem rejeitar, a senha é válida
    return True, ''


# [SEGURANÇA] Função auxiliar que valida o CPF pelo algoritmo oficial
# dos dígitos verificadores da Receita Federal.
def validar_cpf(cpf: str) -> bool:
    """
    Valida o CPF pelos dígitos verificadores (algoritmo oficial).
    Rejeita CPFs com todos os dígitos iguais (ex: '11111111111').
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    if digito1 != int(cpf[9]):
        return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    if digito2 != int(cpf[10]):
        return False

    return True


class CadastroPacienteForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        EqualTo('password2', message='As senhas devem ser iguais.')
    ])
    password2 = PasswordField('Confirme a Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    # [SEGURANÇA] O WTForms chama este método automaticamente ao validar o formulário.
    # Ele pega a senha digitada (field.data), passa para validar_senha() e,
    # se inválida, lança ValidationError com a mensagem de erro para o usuário.
    def validate_password(self, field):
        valida, mensagem = validar_senha(field.data)
        if not valida:
            raise ValidationError(mensagem)

    # [SEGURANÇA] O WTForms chama este método automaticamente ao validar o formulário.
    # Remove pontos e traços do CPF digitado, passa para validar_cpf() e,
    # se inválido, lança ValidationError. Se válido, sobrescreve field.data
    # com o CPF limpo (só números) para salvar no banco sem formatação.
    def validate_cpf(self, field):
        cpf_limpo = ''.join(filter(str.isdigit, field.data))
        if not validar_cpf(cpf_limpo):
            raise ValidationError('CPF inválido. Verifique os dígitos informados.')
        field.data = cpf_limpo


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

    # [SEGURANÇA] Mesma validação de senha do paciente aplicada ao médico.
    # Pega a senha digitada, passa para validar_senha() e lança erro se inválida.
    def validate_password(self, field):
        valida, mensagem = validar_senha(field.data)
        if not valida:
            raise ValidationError(mensagem)


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

    def validate_data_hora(self, field):
        """Validador de Horário (8:00-11:00 e 13:00-17:30)."""
        data_hora = field.data
        hora = data_hora.time()

        inicio_manha = datetime.time(8, 0)
        fim_manha = datetime.time(11, 0)
        inicio_tarde = datetime.time(13, 0)
        fim_tarde = datetime.time(17, 30)

        manha_valida = inicio_manha <= hora <= fim_manha
        tarde_valida = inicio_tarde <= hora <= fim_tarde

        if not manha_valida and not tarde_valida:
            raise ValidationError(
                'A consulta deve ser agendada entre 08:00 e 11:00 ou entre 13:00 e 17:30.'
            )


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
        choices=[
            ('Agendada', 'Agendada'),
            ('Confirmada', 'Confirmada'),
            ('Finalizada', 'Finalizada'),
            ('Cancelada', 'Cancelada')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Salvar Alterações')

    def validate_data_hora(self, field):
        """Validador de Horário (8:00-11:00 e 13:00-17:30)."""
        data_hora = field.data
        hora = data_hora.time()

        inicio_manha = datetime.time(8, 0)
        fim_manha = datetime.time(11, 0)
        inicio_tarde = datetime.time(13, 0)
        fim_tarde = datetime.time(17, 30)

        manha_valida = inicio_manha <= hora <= fim_manha
        tarde_valida = inicio_tarde <= hora <= fim_tarde

        if not manha_valida and not tarde_valida:
            raise ValidationError(
                'A consulta deve ser agendada entre 08:00 e 11:00 ou entre 13:00 e 17:30.'
            )


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