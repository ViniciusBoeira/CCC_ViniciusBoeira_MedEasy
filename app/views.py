from flask import abort, request
from flask import render_template, flash, redirect, url_for, g
from flask_login import login_user, logout_user, current_user, login_required
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

# Rota de Dashboard (exemplo pós-login)
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
    # Apenas pacientes podem agendar
    if current_user.user_type != 'paciente':
        flash('Apenas pacientes podem agendar consultas.')
        return redirect(url_for('dashboard'))

    form = AgendamentoForm()
    
    if form.validate_on_submit():
        nova_consulta = Consulta(
            data_hora=form.data_hora.data,
            paciente_id=current_user.id,
            medico_id=form.medico.data.id, 
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
    # Busca as consultas com base no tipo de usuário
    if current_user.user_type == 'paciente':
        consultas = Consulta.query.filter_by(paciente_id=current_user.id).order_by(Consulta.data_hora.desc()).all()
    elif current_user.user_type == 'medico':
        consultas = Consulta.query.filter_by(medico_id=current_user.id).order_by(Consulta.data_hora.desc()).all()
    
    # Passa o formulário para o template
    return render_template('consultas.html', title='Minhas Consultas', consultas=consultas, form=form)

@app.route('/consulta/<int:consulta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)

    # Regra de permissão: Apenas o médico da consulta ou o paciente podem editar.
    if current_user.id not in [consulta.paciente_id, consulta.medico_id]:
        abort(403) 

    form = EditarConsultaForm(obj=consulta) 

    if form.validate_on_submit():
        # Atualiza os dados do objeto 'consulta' com os dados do formulário
        consulta.medico_id = form.medico.data.id
        consulta.data_hora = form.data_hora.data
        consulta.status = form.status.data
        db.session.commit()
        flash('Consulta atualizada com sucesso!')
        return redirect(url_for('minhas_consultas'))
    
    # Se for um GET request, apenas popula os campos que não foram automaticamente
    form.medico.data = consulta.medico
    form.data_hora.data = consulta.data_hora

    return render_template('editar_consulta.html', title='Editar Consulta', form=form, consulta=consulta)


@app.route('/consulta/<int:consulta_id>/confirmar', methods=['POST'])
@login_required
def confirmar_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    # Apenas o médico da consulta pode confirmar
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
    # Médico ou paciente podem cancelar
    if current_user.id not in [consulta.paciente_id, consulta.medico_id]:
        abort(403)

    consulta.status = 'Cancelada'
    db.session.commit()
    flash('Consulta cancelada.')
    return redirect(url_for('minhas_consultas'))

@app.route('/consulta/<int:consulta_id>/evolucoes', methods=['GET', 'POST'])
@login_required
def gerenciar_evolucoes(consulta_id):
    # Apenas médicos podem acessar esta página
    if current_user.user_type != 'medico':
        abort(403)
        
    consulta = Consulta.query.get_or_404(consulta_id)
    
    # Regra de permissão: Apenas o médico da consulta pode gerenciar.
    if current_user.id != consulta.medico_id:
        flash('Você não tem permissão para acessar o prontuário desta consulta.')
        return redirect(url_for('minhas_consultas'))

    # Instancia os dois formulários
    evolucao_form = EvolucaoForm()
    prescription_form = PrescriptionForm() # Novo

    # Verifica se o formulário de EVOLUÇÃO foi enviado (checando o botão específico)
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

    # Verifica se o formulário de PRESCRIÇÃO foi enviado (checando o botão específico)
    if prescription_form.submit_receita.data and prescription_form.validate_on_submit():
        nova_receita = Receita(
            descricao=prescription_form.descricao.data,
            consulta_id=consulta.id
            # O timestamp é adicionado automaticamente pelo modelo
        )
        db.session.add(nova_receita)
        db.session.commit()
        flash('Receita salva com sucesso!')
        return redirect(url_for('gerenciar_evolucoes', consulta_id=consulta.id))


    # Buscamos os dados existentes para exibir na página (em caso de GET ou falha na validação)
    evolucoes = consulta.evolucoes.order_by(Evolucao.data_criacao.asc()).all()
    receitas = consulta.receitas.order_by(Receita.timestamp.desc()).all() # Novo

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
    # Apenas pacientes podem aceder ao seu histórico desta forma
    if current_user.user_type != 'paciente':
        abort(403) # Proibido para não-pacientes

    consulta = Consulta.query.get_or_404(consulta_id)

    # Regra de segurança: Garante que o paciente só pode ver as suas próprias consultas
    if current_user.id != consulta.paciente_id:
        abort(403) # Proibido se tentar aceder à consulta de outro paciente

    # Carrega as evoluções para exibir no template
    evolucoes = consulta.evolucoes.order_by(Evolucao.data_criacao.asc()).all()
    # Carrega as receitas para exibir no template (Novo)
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
    
    # Regra de segurança: Apenas o médico da consulta pode finalizá-la.
    if current_user.id != consulta.medico_id:
        abort(403)
    
    # Regra de negócio: Só se pode finalizar uma consulta que está 'Confirmada'.
    if consulta.status != 'Confirmada':
        flash('Apenas consultas confirmadas podem ser finalizadas.')
        return redirect(url_for('minhas_consultas'))

    consulta.status = 'Finalizada'
    db.session.commit()
    flash('Consulta marcada como finalizada com sucesso!')
    return redirect(url_for('minhas_consultas'))