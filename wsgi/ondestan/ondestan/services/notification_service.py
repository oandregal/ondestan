# coding=UTF-8
from pyramid.i18n import (
    TranslationString as _
    )

from sqlalchemy import and_

from ondestan.entities import Notification
from ondestan.security import get_user_login, check_permission
import ondestan.services
from ondestan.utils import get_custom_localizer, send_mail, send_sms
from datetime import datetime
import logging

logger = logging.getLogger('ondestan')

# We put these 18n strings here so they're detected when parsing files
_('no_orders_notification_web', domain='Ondestan')


def get_notifications(login, archived=None):
    if archived == None:
        return Notification().queryObject().filter(
                        Notification.user.has(login=login)).\
                        order_by(Notification.date).all()
    else:
        return Notification().queryObject().filter(and_(
                        Notification.user.has(login=login),
                        Notification.archived == archived)).\
                        order_by(Notification.date).all()


def get_new_notifications_for_logged_user(request):
    login = get_user_login(request)
    notifications = get_notifications(login, False)
    for notification in notifications:
        notification.archived = True
        notification.update()
    if (not check_permission('admin', request)) and\
        len(ondestan.services.order_service.get_all_orders(login)) == 0:
        logger.debug("User " + login + " has no orders. Notification " +
            "about making a first one will be displayed.")
        notification = Notification()
        notification.level = 0
        notification.date = datetime.now()
        notification.archived = False
        notification.text = "_('no_orders_notification_web'," +\
            " mapping={'url': '" + request.route_url('orders') +\
            "'}, domain='Ondestan')"
        notifications.append(notification)
    return notifications


def process_web_notification(user, text, level):
    logger.debug("Processing web notification '" + text + "' for user "
                 + user.login)
    notification = Notification()
    if user != None:
        notification.user_id = user.id
        notification.text = text
        notification.level = level
        notification.save()


def process_sms_notification(user, text):
    logger.debug("Processing SMS notification '" + text + "' for user "
                 + user.login)
    if user.phone == None or user.phone == '':
        logger.warn("Can't send SMS notification to user "
                     + user.login)
        return
    send_sms(text, user.phone)


def process_email_notification(user, subject, html_body, text_body):
    logger.debug("Processing mail notification with subject '" + subject +
                 "' for user " + user.login)
    send_mail(html_body, text_body, subject, user.email)


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
        message_ts = _(base_id + '_notification_sms', domain='Ondestan',
                       mapping=parameters)
        text = localizer.translate(message_ts)
        process_sms_notification(login, text)
    if email:
        message_ts = _(base_id + '_notification_mail_subject',
                       domain='Ondestan', mapping=parameters)
        subject = localizer.translate(message_ts)
        message_ts = _(base_id + '_notification_mail_html_body',
                       domain='Ondestan', mapping=parameters)
        html_body = localizer.translate(message_ts)
        message_ts = _(base_id + '_notification_mail_text_body',
                       domain='Ondestan', mapping=parameters)
        text_body = localizer.translate(message_ts)
        process_email_notification(user, subject, html_body, text_body)
