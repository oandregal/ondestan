# coding=UTF-8
from pyramid.i18n import (
    TranslationString as _
    )

from sqlalchemy import and_

from ondestan.entities import Notification
from ondestan.services import user_service, order_service
from ondestan.security import get_user_login, check_permission
from datetime import datetime
import logging

logger = logging.getLogger('ondestan')

# We put this 18n string here so it's detected when parsing files
_('no_orders_notification', domain='Ondestan')


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
    if (not check_permission('admin', request)) and len(order_service.get_all_orders(login)) == 0:
        logger.debug("User " + login + " has no orders. Notification " +
            "about making a first one will be displayed.")
        notification = Notification()
        notification.level = 0
        notification.date = datetime.now()
        notification.archived = False
        notification.text = "_('no_orders_notification', mapping={'url': '" +\
            request.route_url('orders') + "'}, domain='Ondestan')"
        notifications.append(notification)
    return notifications


def store_notification(login, text, level):
    notification = Notification()
    user = user_service.get_user_by_login(login)
    if user != None:
        notification.user_id = user.id
        notification.text = text
        notification.level = level
        notification.date = datetime.now()
        notification.save()
