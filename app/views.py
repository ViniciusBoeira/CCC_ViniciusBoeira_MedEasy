from flask import render_template, flash, redirect, url_for, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.forms import LoginForm, CadastroPacienteForm, CadastroMedicoForm
from app.models import User, Paciente, Medico

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