# coding=UTF-8
from hashlib import sha512

from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

from ondestan.entities import User
from ondestan.utils.comms import send_mail
from ondestan.utils.various import rand_string
import logging

logger = logging.getLogger('ondestan')


def group_finder(login, request):
    user = User().queryObject().filter(
        User.login == login, User.activated == True
    ).scalar()
    if ((user != None) and (user.role != None)):
        return ['role:' + user.role.name]
    return []


def activate_user(request):
    loginhash = request.matchdict['loginhash']
    users = User().queryObject().all()
    for user in users:
        if sha512(user.login).hexdigest() == loginhash:
            logger.info('User ' + user.login + ' has been activated')
            user.activated = True
            user.save()
            break


def reset_password(request):
    loginhash = request.matchdict['loginhash']
    users = User().queryObject().all()
    for user in users:
        if sha512(user.login).hexdigest() == loginhash:
            new_password = rand_string(10)
            logger.info('Password of user ' + user.login +
                        ' has been reset to ' + new_password)
            user.password = sha512(new_password).hexdigest()
            user.save()

            localizer = get_localizer(request)

            # Create the body of the message (a plain-text and an HTML version)
            url = request.route_url('login')
            text_ts = _('plain_password_reset_mail', mapping={
                        'name': user.name, 'password': new_password,
                        'url': url}, domain='Ondestan')
            html_ts = _('html_password_reset_mail', mapping={'name': user.name,
                        'password': new_password, 'url': url},
                        domain='Ondestan')
            subject_ts = _('subject_password_reset_mail', domain='Ondestan')

            text = localizer.translate(text_ts)
            html = localizer.translate(html_ts)
            subject = localizer.translate(subject_ts)

            send_mail(html, text, subject, user.email)
            break


def remind_user(request):
    email = request.params['email']
    user = User().queryObject().filter(
        User.email == email).scalar()
    if (user != None):

        localizer = get_localizer(request)

        # Create the body of the message (a plain-text and an HTML version).
        url = request.route_url('password_reset',
                                loginhash=sha512(user.login).hexdigest())
        text_ts = _('plain_reminder_mail', mapping={'name': user.name,
                        'url': url, 'login': user.login}, domain='Ondestan')
        html_ts = _('html_reminder_mail', mapping={'name': user.name,
                        'url': url, 'login': user.login}, domain='Ondestan')
        subject_ts = _('subject_reminder_mail', domain='Ondestan')

        text = localizer.translate(text_ts)
        html = localizer.translate(html_ts)
        subject = localizer.translate(subject_ts)

        send_mail(html, text, subject, email)


def check_login_request(request):
    return check_user_pass(request.params['login'], request.params['password'])


def check_user_pass(login, password):
    user = User().queryObject().filter(
        User.login == login, User.activated == True
    ).scalar()
    if (user != None):
        return user.password == sha512(password).hexdigest()
    return False


def get_user_by_login(login):
    return User().queryObject().filter(User.login == login).scalar()


def get_user_by_email(email):
    return User().queryObject().filter(User.email == email).scalar()


def create_user(request):
    localizer = get_localizer(request)

    login = request.params['login']
    name = request.params['name']
    email = request.params['email']
    user = User().queryObject().filter(User.login == login).scalar()
    if (user != None):
        msg = _('login_already_use', domain='Ondestan')
        return localizer.translate(msg)
    user = User().queryObject().filter(User.email == email).scalar()
    if (user != None):
        msg = _('email_already_use', domain='Ondestan')
        return localizer.translate(msg)
    user = User()
    user.login = login
    user.name = name
    user.email = email
    user.phone = request.params['phone']
    user.activated = False
    user.password = sha512(request.params['password']).hexdigest()
    user.role_id = 2
    user.save()

    # Create the body of the message (a plain-text and an HTML version).
    url = request.route_url('activate_user',
                            loginhash=sha512(login).hexdigest())
    text_ts = _('plain_signup_mail', mapping={'name': name, 'url': url},
                                domain='Ondestan')
    html_ts = _('html_signup_mail', mapping={'name': name, 'url': url},
                                domain='Ondestan')
    subject_ts = _('subject_signup_mail', domain='Ondestan')

    text = localizer.translate(text_ts)
    html = localizer.translate(html_ts)
    subject = localizer.translate(subject_ts)

    send_mail(html, text, subject, email)

    return ''
