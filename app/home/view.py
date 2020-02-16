from flask_classy import FlaskView, route
from flask import render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import current_user
from flask_mail import Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

import pyfastocloud_models.constants as constants
from pyfastocloud_models.utils.utils import is_valid_email, get_country_code_by_remote_addr
from app import app, mail, login_manager
from app.home.entry import ProviderAdminUser
from app.home.forms import ContactForm
from app.common.provider.forms import SignupForm, SigninForm
from bson.objectid import ObjectId

def _get_provider_by_email(email: str):
    try:
        provider = ProviderAdminUser.objects.get({'email': email})
    except ProviderAdminUser.DoesNotExist:
        return None
    else:
        return provider


def _get_provider_by_id(id: str):
    try:
        provider = ProviderAdminUser.objects.get({'_id': ObjectId(id)})
    except ProviderAdminUser.DoesNotExist:
        return None
    else:
        return provider


def flash_success(text: str):
    flash(text, 'success')


def flash_error(text: str):
    flash(text, 'danger')


def send_email(email: str, subject: str, message: str):
    config = app.config['PUBLIC_CONFIG']
    msg = Message(subject, recipients=[config['support']['contact_email']])
    msg.body = 'From: {0} <{0}> {1}'.format(email, message)
    mail.send(msg)


def post_login(form: SigninForm):
    if not form.validate_on_submit():
        flash_error(form.errors)
        return render_template('home/login.html', form=form)

    email = form.email.data.lower()
    check_user = _get_provider_by_email(email)
    if not check_user:
        flash_error('User not found.')
        return render_template('home/login.html', form=form)

    if check_user.status == ProviderAdminUser.Status.NO_ACTIVE:
        flash_error('User not active.')
        return render_template('home/login.html', form=form)

    if not ProviderAdminUser.check_password_hash(check_user.password, form.password.data):
        flash_error('Invalid password.')
        return render_template('home/login.html', form=form)

    check_user.login()
    return redirect(url_for('ProviderView:dashboard'))


class HomeView(FlaskView):
    CONFIRM_LINK_TTL = 3600
    SALT_LINK = 'email-confirm'

    route_base = "/"

    def __init__(self):
        self._confirm_link_generator = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    def index(self):
        languages = constants.AVAILABLE_LOCALES_PAIRS
        return render_template('index.html', languages=languages)

    @route('/robots.txt')
    @route('/sitemap.xml')
    def static_from_root(self):
        return send_from_directory(app.static_folder, request.path[1:])

    @route('/contact', methods=['GET', 'POST'])
    def contact(self):
        form = ContactForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('All fields are required.')
                return render_template('contact.html', form=form)

            send_email(form.email.data, form.subject.data, form.message.data)
            return render_template('contact.html', success=True)

        elif request.method == 'GET':
            return render_template('contact.html', form=form)

    @route('/language/<language>')
    def set_language(self, language=constants.DEFAULT_LOCALE):
        founded = next((x for x in constants.AVAILABLE_LOCALES if x == language), None)
        if founded:
            session['language'] = founded

        return redirect(url_for('HomeView:index'))

    def confirm_email(self, token):
        try:
            email = self._confirm_link_generator.loads(token, salt=HomeView.SALT_LINK,
                                                       max_age=HomeView.CONFIRM_LINK_TTL)
            confirm_user = _get_provider_by_email(email)
            if confirm_user:
                confirm_user.status = ProviderAdminUser.Status.ACTIVE
                confirm_user.save()
                confirm_user.login()
                return redirect(url_for('HomeView:signin'))
            else:
                return '<h1>We can\'t find user.</h1>'
        except SignatureExpired:
            return '<h1>The token is expired!</h1>'

    @route('/signin', methods=['POST', 'GET'])
    def signin(self):
        if current_user.is_authenticated:
            return redirect(url_for('ProviderView:dashboard'))

        form = SigninForm()
        if request.method == 'POST':
            return post_login(form)

        return render_template('home/login.html', form=form)

    def private_policy(self):
        config = app.config['PUBLIC_CONFIG']
        return render_template('home/private_policy.html', contact_email=config['support']['contact_email'],
                               title=config['site']['title'])

    def term_of_use(self):
        config = app.config['PUBLIC_CONFIG']
        return render_template('home/term_of_use.html', contact_email=config['support']['contact_email'],
                               title=config['site']['title'])

    @route('/signup', methods=['GET', 'POST'])
    def signup(self):
        form = SignupForm(country=get_country_code_by_remote_addr(request.remote_addr))
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash_error(form.errors)
                return render_template('home/register.html', form=form)

            email = form.email.data.lower()
            if not is_valid_email(email, False):
                flash_error('Invalid email.')
                return render_template('home/register.html', form=form)

            existing_user = _get_provider_by_email(email)
            if existing_user:
                return redirect(url_for('HomeView:signin'))

            new_user = ProviderAdminUser.make_provider(email=email, password=form.password.data,
                                                       country=form.country.data,
                                                       language=form.language.data)
            new_user.save()

            token = self._confirm_link_generator.dumps(email, salt=HomeView.SALT_LINK)
            confirm_url = url_for('HomeView:confirm_email', token=token, _external=True)
            config = app.config['PUBLIC_CONFIG']
            html = render_template('home/email/activate.html', confirm_url=confirm_url,
                                   contact_email=config['support']['contact_email'], title=config['site']['title'],
                                   company=config['company']['title'])
            msg = Message(subject='Confirm Email', recipients=[email], html=html)
            mail.send(msg)
            flash_success('Please check email: {0}.'.format(email))
            return redirect(url_for('HomeView:signin'))

        return render_template('home/register.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return _get_provider_by_id(user_id)


def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)
