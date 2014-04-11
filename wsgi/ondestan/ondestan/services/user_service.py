# coding=UTF-8
from datetime import datetime
from hashlib import sha512

from pyramid.i18n import (
    get_localizer,
    get_locale_name,
    TranslationString as _
    )

from ondestan.entities import User
import ondestan.services
from ondestan.utils import rand_string
import logging

logger = logging.getLogger('ondestan')

# We put these 18n strings here so they're detected when parsing files
_('signup_notification_mail_subject', domain='Ondestan')
_('signup_notification_mail_html_body', domain='Ondestan')
_('signup_notification_mail_text_body', domain='Ondestan')

_('login_reminder_notification_mail_subject', domain='Ondestan')
_('login_reminder_notification_mail_html_body', domain='Ondestan')
_('login_reminder_notification_mail_text_body', domain='Ondestan')

_('password_reset_notification_web', domain='Ondestan')
_('password_reset_notification_mail_subject', domain='Ondestan')
_('password_reset_notification_mail_html_body', domain='Ondestan')
_('password_reset_notification_mail_text_body', domain='Ondestan')


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

            parameters = {'name': user.name, 'password': new_password,
                          'url': request.route_url('login'),
                          'url_profile': request.route_url('update_profile')}
            ondestan.services.notification_service.process_notification(
                'password_reset', user.login, True, 3, True, False, parameters)
            break


def remind_user(request):
    email = request.params['email']
    user = User().queryObject().filter(
        User.email == email).scalar()
    if (user != None):
        url = request.route_url('password_reset',
                                loginhash=sha512(user.login).hexdigest())
        parameters = {'name': user.name, 'url': url, 'login': user.login}
        ondestan.services.notification_service.process_notification(
            'login_reminder', user.login, False, 0, True, False, parameters)


def check_login_request(request):
    login = request.params['login']
    if (check_user_pass(login, request.params['password'])):
        user = get_user_by_login(login)
        user.last_login = datetime.now()
        user.locale = get_locale_name(request)
        user.update()
        logger.debug('Updating last_login and locale for user ' + login)
        return True
    else:
        return False


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
    user.locale = get_locale_name(request)
    user.phone = request.params['phone']
    user.activated = False
    user.password = sha512(request.params['password']).hexdigest()
    user.role_id = 2
    user.save()

    url = request.route_url('activate_user',
                            loginhash=sha512(login).hexdigest())
    parameters = {'name': name, 'url': url}
    ondestan.services.notification_service.process_notification('signup',
        user.login, False, 0, True, False, parameters)

    return ''


def update_user(request):
    localizer = get_localizer(request)

    user_id = int(request.params['id'])
    login = request.params['login']
    name = request.params['name']
    email = request.params['email']
    user = User().queryObject().filter(User.login == login).scalar()
    if ((user != None) and (user.id != user_id)):
        msg = _('login_already_use', domain='Ondestan')
        return localizer.translate(msg)
    user = User().queryObject().filter(User.email == email).scalar()
    if ((user != None) and (user.id != user_id)):
        msg = _('email_already_use', domain='Ondestan')
        return localizer.translate(msg)

    user = User().queryObject().filter(User.id == user_id).scalar()
    user.login = login
    user.name = name
    user.email = email
    user.phone = request.params['phone']
    user.password = sha512(request.params['password']).hexdigest()
    user.update()

    msg = _('user_profile_updated', domain='Ondestan')
    return localizer.translate(msg)
