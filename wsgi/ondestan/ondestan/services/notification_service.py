# coding=UTF-8
from pyramid.i18n import (
    TranslationString as _
    )

from sqlalchemy import and_, desc

from ondestan.entities import Notification
from ondestan.security import get_user_login, check_permission
import ondestan.services
from ondestan.utils import get_custom_localizer, send_mail, send_sms
from datetime import datetime
import logging

logger = logging.getLogger('ondestan')
web_type = Notification._TYPES.index('web')
mail_type = Notification._TYPES.index('e-mail')
sms_type = Notification._TYPES.index('sms')

# We put these 18n strings here so they're detected when parsing files
_('no_orders_notification_web', domain='Ondestan')


def get_web_notifications(login, archived=None):
    if archived == None:
        return Notification().queryObject().filter(and_(
                        Notification.user.has(login=login),
                        Notification.type == web_type)).\
                        order_by(desc(Notification.date)).all()
    else:
        return Notification().queryObject().filter(and_(
                        Notification.user.has(login=login),
                        Notification.type == web_type,
                        Notification.archived == archived)).\
                        order_by(desc(Notification.date)).all()


def get_new_web_notifications_for_logged_user(request):
    login = get_user_login(request)
    notifications = get_web_notifications(login, False)
    for notification in notifications:
        notification.archived = True
        notification.update()
    if (not check_permission('admin', request)) and\
        len(ondestan.services.order_service.get_all_orders(login)) == 0:
        logger.debug("User " + login + " has no orders. Notification " +
            "about making a first one will be displayed.")
        notification = Notification()
        notification.level = 0
        notification.type = web_type
        notification.date = datetime.now()
        notification.archived = False
        notification.text = "_('no_orders_notification_web'," +\
            " mapping={'url': '" + request.route_url('orders') +\
            "'}, domain='Ondestan')"
        notifications.append(notification)
    return notifications


def get_all_notifications(request):
    is_admin = check_permission('admin', request)
    if is_admin:
        return Notification().queryObject().\
                        order_by(desc(Notification.date)).all()
    else:
        return Notification().queryObject().filter(
                        Notification.user.has(login=get_user_login(request))).\
                        order_by(desc(Notification.date)).all()


def process_web_notification(user, text, level):
    logger.debug("Processing web notification '" + text + "' for user "
                 + user.login)
    notification = Notification()
    if user != None:
        notification.user_id = user.id
        notification.text = text
        notification.level = level
        notification.type = web_type
        notification.date = datetime.now()
        notification.save()


def process_sms_notification(user, text):
    localizer = get_custom_localizer(user.locale)
    localized = localizer.translate(eval(text))
    logger.debug("Processing SMS notification '" + text + "' for user "
                 + user.login)
    if user.phone == None or user.phone == '':
        logger.warn("Can't send SMS notification to user "
                     + user.login)
    else:
        send_sms(localized, user.phone)

    notification = Notification()
    if user != None:
        notification.user_id = user.id
        notification.text = text
        notification.type = sms_type
        notification.date = datetime.now()
        notification.archived = True
        notification.save()


def process_email_notification(user, subject, html_body, text_body):
    localizer = get_custom_localizer(user.locale)
    localized_subject = localizer.translate(eval(subject))
    localized_html_body = localizer.translate(eval(html_body))
    localized_text_body = localizer.translate(eval(text_body))
    logger.debug("Processing mail notification with subject '" + subject +
                 "' for user " + user.login)
    send_mail(localized_html_body, localized_text_body, localized_subject,
              user.email)
    notification = Notification()
    if user != None:
        notification.user_id = user.id
        notification.text = subject
        notification.type = mail_type
        notification.date = datetime.now()
        notification.archived = True
        notification.save()


def process_notification(base_id, login, web=False, web_level=0, email=False,
                         sms=False, parameters={}):
    user = ondestan.services.user_service.get_user_by_login(login)

    if base_id == None or base_id == '' or user == None:
        return

    localizer = get_custom_localizer(user.locale)
    # We check the parameters for translatable strings
    for i in parameters:
        if str(parameters[i]).startswith("_("):
            parameters[i] = localizer.translate(eval(parameters[i]))

    if web:
        text = "_('" + base_id + "_notification_web', domain='Ondestan'," +\
                " mapping=" + str(parameters) + ")"
        process_web_notification(user, text, web_level)
    if sms:
        text = "_('" + base_id + "_notification_sms', domain='Ondestan'," +\
                       " mapping=" + str(parameters) + ")"
        process_sms_notification(login, text)
    if email:
        subject = "_('" + base_id + "_notification_mail_subject'," +\
                       "domain='Ondestan', mapping=" + str(parameters) + ")"
        html_body = "_('" + base_id + "_notification_mail_html_body'," +\
                       "domain='Ondestan', mapping=" + str(parameters) + ")"
        text_body = "_('" + base_id + "_notification_mail_text_body'," +\
                       "domain='Ondestan', mapping=" + str(parameters) + ")"
        process_email_notification(user, subject, html_body, text_body)
