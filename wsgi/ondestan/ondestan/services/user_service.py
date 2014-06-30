# coding=UTF-8
from datetime import datetime
from hashlib import sha512

from pyramid.i18n import (
    get_localizer,
    get_locale_name,
    TranslationString as _
    )
from sqlalchemy import not_, and_

from ondestan.entities import User, Role, Notification
import ondestan.services
from ondestan.utils import rand_string
from ondestan.security import get_user_email
import logging

logger = logging.getLogger('ondestan')

# We put these 18n strings here so they're detected when parsing files
_('signup_notification_mail_subject', domain='Ondestan')
_('signup_notification_mail_html_body', domain='Ondestan')
_('signup_notification_mail_text_body', domain='Ondestan')

_('password_reset_notification_web', domain='Ondestan')
_('password_reset_notification_mail_subject', domain='Ondestan')
_('password_reset_notification_mail_html_body', domain='Ondestan')
_('password_reset_notification_mail_text_body', domain='Ondestan')

_('user_profile_updated', domain='Ondestan')
_('user_password_updated', domain='Ondestan')
_('wrong_password', domain='Ondestan')


def group_finder(email, request):
    user = User().queryObject().filter(
        User.email == email, User.activated == True
    ).scalar()
    if ((user != None) and (user.role != None)):
        return ['role:' + user.role.name]
    return []


def activate_user(request):
    loginhash = request.matchdict['loginhash']
    users = User().queryObject().all()
    for user in users:
        if sha512(user.email).hexdigest() == loginhash:
            logger.info('User ' + user.email + ' has been activated')
            user.activated = True
            user.save()
            break


def reset_password(request):
    email = request.params['email']
    if email != None:
        user = get_user_by_email(email)
        if user != None:
            # new_password = rand_string(10)
            new_password = user.email
            logger.info('Password of user ' + user.email +
                        ' has been reset to ' + new_password)
            user.password = sha512(new_password).hexdigest()
            user.save()

            parameters = {'name': user.name, 'password': new_password,
                          'url': request.route_url('login'),
                          'url_profile': request.route_url('update_profile')}
            ondestan.services.notification_service.process_notification(
                'password_reset', user.email, True, 3, True, False, parameters)


def check_login_request(request):
    email = request.params['email']
    if (check_user_pass(email, request.params['password'])):
        user = get_user_by_email(email)
        user.last_login = datetime.utcnow()
        user.locale = get_locale_name(request)
        user.update()
        logger.debug('Updating last_login and locale for user ' + email)
        return True
    else:
        return False


def get_admin_users():
    return User().queryObject().filter(and_(User.role.has(
            name=Role._ADMIN_ROLE), User.activated == True)).all()


def get_non_admin_users():
    return User().queryObject().filter(and_(not_(User.role.has(
            name=Role._ADMIN_ROLE)), User.activated == True)).all()


def check_user_pass(email, password):
    user = User().queryObject().filter(
        User.email == email, User.activated == True
    ).scalar()
    if (user != None):
        return user.password == sha512(password).hexdigest()
    return False


def get_user_by_email(email):
    return User().queryObject().filter(User.email == email).scalar()


def create_user(request):
    localizer = get_localizer(request)

    name = request.params['name']
    email = request.params['email']
    user = User().queryObject().filter(User.email == email).scalar()
    if (user != None):
        msg = _('email_already_use', domain='Ondestan')
        return localizer.translate(msg)

    user = User()
    user.name = name
    user.email = email
    user.locale = get_locale_name(request)
    user.phone = request.params['phone']
    user.activated = False
    user.password = sha512(request.params['password']).hexdigest()
    user.role_id = 2
    user.save()

    url = request.route_url('activate_user',
                            loginhash=sha512(email).hexdigest())
    parameters = {'name': name, 'url': url}
    ondestan.services.notification_service.process_notification('signup',
        user.email, False, 0, True, False, parameters)

    return ''


def update_user(request):
    user_id = int(request.params['id'])
    user = User().queryObject().filter(User.id == user_id).scalar()
    if (user.email != get_user_email(request)):
        return
    name = request.params['name']
    email = request.params['email']
    user = User().queryObject().filter(User.email == email).scalar()
    if ((user != None) and (user.id != user_id)):
        notification = Notification()
        notification.text = "_('email_already_use', domain='Ondestan')"
        notification.level = 3
        return notification

    user = User().queryObject().filter(User.id == user_id).scalar()
    user.name = name
    user.email = email
    user.phone = request.params['phone']
    user.update()
    logger.debug('Profile updated for user ' + user.email)

    notification = Notification()
    notification.text = "_('user_profile_updated', domain='Ondestan')"
    notification.level = 0
    return notification


def update_password(request):
    user_id = int(request.params['id'])
    user = User().queryObject().filter(User.id == user_id).scalar()
    if (user.email != get_user_email(request)):
        return
    old_password = request.params['old_password']

    if user.password != sha512(old_password).hexdigest():
        notification = Notification()
        notification.text = "_('wrong_password', domain='Ondestan')"
        notification.level = 3
        return notification
    user.password = sha512(request.params['password']).hexdigest()
    user.update()
    logger.debug('Password updated for user ' + user.email)

    notification = Notification()
    notification.text = "_('user_password_updated', domain='Ondestan')"
    notification.level = 0
    return notification
