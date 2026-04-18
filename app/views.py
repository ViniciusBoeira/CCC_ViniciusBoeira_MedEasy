from flask import abort, request
from flask import render_template, flash, redirect, url_for, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_limiter import Limiter                   # [SEGURANÇA] Importa a classe Limiter que controla o número de requisições por IP
from flask_limiter.util import get_remote_address   # [SEGURANÇA] Importa a função que extrai o endereço IP do cliente de cada requisição
from app import app, db, lm
from app.forms import (
    LoginForm, CadastroPacienteForm, CadastroMedicoForm,
    AgendamentoForm, EditarConsultaForm, EmptyForm,
    EvolucaoForm, PrescriptionForm
)
from app.models import (
    User, Paciente, Medico, Consulta,
    Evolucao, Receita
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)


# Carrega o usuário da sessão para o Flask-Login
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


# Define o g.user antes de cada requisição
@app.before_request
def before_request():
    g.user = current_user


# Rota principal
@app.route('/')
def index():
    return render_template('index.html')


# Rota de Login
@app.route('/login/', methods=['GET', 'POST'])

@limiter.limit("5 per minute", methods=["POST"], error_message="Muitas tentativas de login. Aguarde 1 minuto e tente novamente.")
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('E-mail ou senha inválidos.')
            return redirect(url_for('login'))

        login_user(user)
        flash('Login realizado com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template('login.html', title='Login', form=form)


# Rota de Logout
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.')
    return redirect(url_for('index'))


# Rota de Dashboard
@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=g.user)


# Rota para escolher o tipo de cadastro
@app.route('/register/')
def register_choice():
    return render_template('register_choice.html')


# Rota de Cadastro de Paciente
@app.route('/register/paciente', methods=['GET', 'POST'])
def register_paciente():
    form = CadastroPacienteForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash('Este e-mail já está cadastrado. Faça login ou use outro e-mail.')
            return redirect(url_for('register_paciente'))

        if Paciente.query.filter_by(cpf=form.cpf.data).first():
            flash('Este CPF já está cadastrado.')
            return redirect(url_for('register_paciente'))

        paciente = Paciente(
            name=form.name.data,
            email=form.email.data,
            cpf=form.cpf.data,
            data_nascimento=form.data_nascimento.data
        )
       
        paciente.set_password(form.password.data)
        db.session.add(paciente)
        db.session.commit()
        flash('Cadastro de paciente realizado com sucesso!')
        return redirect(url_for('login'))

    return render_template('register_paciente.html', title='Cadastro de Paciente', form=form)


# Rota de Cadastro de Médico
@app.route('/register/medico', methods=['GET', 'POST'])
def register_medico():
    form = CadastroMedicoForm()
    if form.validate_on_submit():

     
        if User.query.filter_by(email=form.email.data).first():
            flash('Este e-mail já está cadastrado. Faça login ou use outro e-mail.')
            return redirect(url_for('register_medico'))

        if Medico.query.filter_by(crm=form.crm.data).first():
            flash('Este CRM já está cadastrado.')
            return redirect(url_for('register_medico'))

        medico = Medico(
            name=form.name.data,
            email=form.email.data,
            crm=form.crm.data,
            especialidade=form.especialidade.data
        )
     
        medico.set_password(form.password.data)
        db.session.add(medico)
        db.session.commit()
        flash('Cadastro de médico realizado com sucesso!')
        return redirect(url_for('login'))

    return render_template('register_medico.html', title='Cadastro de Médico', form=form)


@app.route('/agendar/', methods=['GET', 'POST'])
@login_required
def agendar_consulta():
    if current_user.user_type != 'paciente':
        flash('Apenas pacientes podem agendar consultas.')
        return redirect(url_for('dashboard'))

    form = AgendamentoForm()

    if form.validate_on_submit():
        medico_id = form.medico.data.id
        data_hora = form.data_hora.data

        consulta_existente = Consulta.query.filter(
            Consulta.medico_id == medico_id,
            Consulta.data_hora == data_hora,
            Consulta.status.in_(['Agendada', 'Confirmada'])
        ).first()

        if consulta_existente:
            flash(
                f'O Dr(a). {consulta_existente.medico.name} já possui uma consulta '
                f'agendada ou confirmada para este horário.',
                'danger'
            )
            return redirect(url_for('agendar_consulta'))

        nova_consulta = Consulta(
            data_hora=data_hora,
            paciente_id=current_user.id,
            medico_id=medico_id,
            status='Agendada'
        )
        db.session.add(nova_consulta)
        db.session.commit()
        flash('Consulta agendada com sucesso!')
        return redirect(url_for('minhas_consultas'))

    return render_template('agendar_consulta.html', title='Agendar Consulta', form=form)


@app.route('/consultas/')
@login_required
def minhas_consultas():
    form = EmptyForm()
    consultas = []
    if current_user.user_type == 'paciente':
        consultas = Consulta.query.filter_by(paciente_id=current_user.id).order_by(Consulta.data_hora.desc()).all()
    elif current_user.user_type == 'medico':
        consultas = Consulta.query.filter_by(medico_id=current_user.id).order_by(Consulta.data_hora.desc()).all()

    return render_template('consultas.html', title='Minhas Consultas', consultas=consultas, form=form)


@app.route('/consulta/<int:consulta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)

    if current_user.id not in [consulta.paciente_id, consulta.medico_id]:
        abort(403)

    form = EditarConsultaForm(obj=consulta)

    if current_user.user_type == 'paciente':
        form.status.choices = [
            ('Agendada', 'Agendada'),
            ('Cancelada', 'Cancelada')
        ]

    if form.validate_on_submit():
        novo_medico_id = form.medico.data.id
        nova_data_hora = form.data_hora.data
        novo_status = form.status.data

        if current_user.user_type == 'paciente' and novo_status in ['Confirmada', 'Finalizada']:
            flash('Você não tem permissão para alterar o status para Confirmada ou Finalizada.', 'danger')
            return redirect(url_for('editar_consulta', consulta_id=consulta.id))

        if novo_status in ['Agendada', 'Confirmada']:
            consulta_existente = Consulta.query.filter(
                Consulta.medico_id == novo_medico_id,
                Consulta.data_hora == nova_data_hora,
                Consulta.id != consulta.id,
                Consulta.status.in_(['Agendada', 'Confirmada'])
            ).first()

            if consulta_existente:
                flash(
                    f'O Dr(a). {consulta_existente.medico.name} já possui outra consulta '
                    f'agendada ou confirmada para este horário.',
                    'danger'
                )
                return redirect(url_for('editar_consulta', consulta_id=consulta.id))

        consulta.medico_id = novo_medico_id
        consulta.data_hora = nova_data_hora
        consulta.status = novo_status
        db.session.commit()
        flash('Consulta atualizada com sucesso!')
        return redirect(url_for('minhas_consultas'))

    form.medico.data = consulta.medico
    form.data_hora.data = consulta.data_hora

    return render_template('editar_consulta.html', title='Editar Consulta', form=form, consulta=consulta)


@app.route('/consulta/<int:consulta_id>/confirmar', methods=['POST'])
@login_required
def confirmar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    if current_user.id != consulta.medico_id:
        abort(403)

    consulta.status = 'Confirmada'
    db.session.commit()
    flash('Consulta confirmada com sucesso!')
    return redirect(url_for('minhas_consultas'))


@app.route('/consulta/<int:consulta_id>/cancelar', methods=['POST'])
@login_required
def cancelar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    if current_user.id not in [consulta.paciente_id, consulta.medico_id]:
        abort(403)

    consulta.status = 'Cancelada'
    db.session.commit()
    flash('Consulta cancelada.')
    return redirect(url_for('minhas_consultas'))


@app.route('/consulta/<int:consulta_id>/evolucoes', methods=['GET', 'POST'])
@login_required
def gerenciar_evolucoes(consulta_id):
    if current_user.user_type != 'medico':
        abort(403)

    consulta = Consulta.query.get_or_404(consulta_id)

    if current_user.id != consulta.medico_id:
        flash('Você não tem permissão para acessar o prontuário desta consulta.')
        return redirect(url_for('minhas_consultas'))

    evolucao_form = EvolucaoForm()
    prescription_form = PrescriptionForm()

    if evolucao_form.submit_evolucao.data and evolucao_form.validate_on_submit():
        nova_evolucao = Evolucao(
            conteudo=evolucao_form.conteudo.data,
            consulta_id=consulta.id,
            medico_id=current_user.id
        )
        db.session.add(nova_evolucao)
        db.session.commit()
        flash('Evolução salva com sucesso!')
        return redirect(url_for('gerenciar_evolucoes', consulta_id=consulta.id))

    if prescription_form.submit_receita.data and prescription_form.validate_on_submit():
        nova_receita = Receita(
            descricao=prescription_form.descricao.data,
            consulta_id=consulta.id
        )
        db.session.add(nova_receita)
        db.session.commit()
        flash('Receita salva com sucesso!')
        return redirect(url_for('gerenciar_evolucoes', consulta_id=consulta.id))

    evolucoes = consulta.evolucoes.order_by(Evolucao.data_criacao.asc()).all()
    receitas = consulta.receitas.order_by(Receita.timestamp.desc()).all()

    return render_template(
        'evolucoes.html',
        title='Prontuário da Consulta',
        evolucao_form=evolucao_form,
        prescription_form=prescription_form,
        consulta=consulta,
        evolucoes=evolucoes,
        receitas=receitas
    )


@app.route('/consulta/<int:consulta_id>/historico/')
@login_required
def historico_consulta(consulta_id):
    if current_user.user_type != 'paciente':
        abort(403)

    consulta = Consulta.query.get_or_404(consulta_id)

    if current_user.id != consulta.paciente_id:
        abort(403)

    evolucoes = consulta.evolucoes.order_by(Evolucao.data_criacao.asc()).all()
    receitas = consulta.receitas.order_by(Receita.timestamp.desc()).all()

    return render_template(
        'historico_consulta.html',
        title='Histórico da Consulta',
        consulta=consulta,
        evolucoes=evolucoes,
        receitas=receitas
    )


@app.route('/consulta/<int:consulta_id>/finalizar', methods=['POST'])
@login_required
def finalizar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)

    if current_user.id != consulta.medico_id:
        abort(403)

    if consulta.status != 'Confirmada':
        flash('Apenas consultas confirmadas podem ser finalizadas.')
        return redirect(url_for('minhas_consultas'))

    consulta.status = 'Finalizada'
    db.session.commit()
    flash('Consulta marcada como finalizada com sucesso!')
    return redirect(url_for('minhas_consultas'))