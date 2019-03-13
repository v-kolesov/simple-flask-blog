import functools
from sqlalchemy import desc
from flask import Blueprint
from flask.helpers import get_env
from flask import (url_for, redirect, render_template,
                   abort, flash, session, request)
from flask_wtf import FlaskForm, RecaptchaField
from wtforms_alchemy import model_form_factory
from flask.globals import current_app
from models import Page, db
from wtforms import StringField, TextAreaField, validators as v, PasswordField
from flask_mail import Mail, Message


bp = Blueprint('blog', 'blog')

mail = Mail()

ModelForm = model_form_factory(FlaskForm)


class ContactForm(FlaskForm):
    email = StringField('Your email', [v.Email(), v.DataRequired()])
    name = StringField('Your name', [v.DataRequired()])
    message = TextAreaField('Your message', [v.DataRequired()])
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    username = StringField(
        'Username', [v.Email(), v.DataRequired(), v.EqualTo])
    password = PasswordField('Password', [v.DataRequired()])
    recaptcha = RecaptchaField()


class PageForm(ModelForm):
    class Meta:
        model = Page


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if (
            session.get('auth_correct', False)
            or get_env() == 'testing'
        ):
            return fn(*args, **kwargs)
        return redirect(url_for('blog.admin', next=request.path))
    return inner


@bp.route('/admin/pages/<id>', methods=['POST', 'GET'])
@login_required
def admin_pages(id=None):
    obj = (Page.query.get(id) if id else None) or Page()
    form = PageForm(obj=obj)

    if form.validate_on_submit():
        form.populate_obj(obj)
        db.session.add(obj)
        db.session.commit()
        flash('Saved', 'success')
        return redirect(url_for('blog.admin_pages', id=obj.id))

    cntx = dict(
        page=obj,
        form=form,
        id=id,
        nav_suppressed=True,
    )
    return render_template('admin/page_edit.html', **cntx)


@bp.route('/admin/pages/')
@login_required
def admin_pages_list(id=None):
    cntx = dict(
        pages=Page.query.order_by(desc(Page.created_at)).all(),
        nav_suppressed=True,
    )
    return render_template('admin/page_list.html', **cntx)


@bp.route('/create')
@login_required
def create():
    if current_app.config['BLOG_ALLOW_RECREATE_DATABASE']:
        db.drop_all()
        db.create_all()
        homepage = Page(
            is_published=True,
            slug='/',
            title=current_app.config['BLOG_HOME_TITLE'],
            intro=current_app.config['BLOG_HOME_INTRO'],
            text='None'
        )
        db.session.add(homepage)
        db.session.commit()
        return 'created'
    abort('404')


@bp.route('/admin/login', methods=['POST', 'GET'])
def login():
    next_url = request.args.get('next', url_for('blog.admin_pages_list'))
    form = LoginForm()
    if session.get('auth_correct'):
        return redirect(next_url)

    if form.validate_on_submit():
        if (
            current_app.config['BLOG_EMAIL'] == form.username.data and
            current_app.config['BLOG_USERPWD'] == form.password.data
        ):
            session['auth_correct'] = True
            return redirect(next_url)

    cntx = {
        'form': form,
        'page': {
            'title': 'Login Page'
        }}
    return render_template('front/login.html', **cntx)


@bp.route('/admin/logout')
@login_required
def admin_logout():
    del session['auth_correct']
    return redirect(request.args.get('next', '/'))


@bp.route('/')
@bp.route('/p/<int:num>')
def home(num=0):
    offset = int(current_app.config['BLOG_PAGINATE_PAGE_COUNT'])
    cntx = {
        'page': Page.published().first(),
        'pagination': (
            Page.published()
            .filter(Page.slug != '/')
            .order_by(desc(Page.created_at))
            .paginate(num, offset, False)
        ),
    }
    return render_template('front/index.html', **cntx)


@bp.route('/<path:slug>.html')
def page(slug='/'):
    page = (
        Page.published().filter(Page.slug == slug).first()
        or abort(404)
    )
    cntx = dict(page=page)
    if page:
        return render_template('front/page.html', **cntx)



@bp.route('/contact', methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    success_send = False
    if form.validate_on_submit():
        host = request.headers.get('Host', '<no host>')
        msg = Message(f'Incoming message from [{host}]',
                      sender=form.email.data,
                      recipients=[current_app.config['BLOG_EMAIL']],
                      body=form.message.data
                      )
        print(msg)
        mail.send(msg)

        success_send = True

    cntx = {
        'form': form,
        'success_send': success_send,
        'page': {
            'title': 'Contact Me',
            'intro': 'Have questions? I have answers.'
        }
    }
    return render_template('front/contact.html', **cntx)
