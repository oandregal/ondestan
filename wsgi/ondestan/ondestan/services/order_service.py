# coding=UTF-8
from sqlalchemy import func, tuple_, and_, desc

from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

import datetime
import logging

from ondestan.entities import Order, User, Order_state
from ondestan.security import get_user_login
from ondestan.utils import Db, Config
from ondestan.utils.comms import send_mail

logger = logging.getLogger('ondestan')


def create_order(request):
    # localizer = get_localizer(request)

    login = get_user_login(request)
    units = int(request.params['units'])
    address = request.params['address']
    user = User().queryObject().filter(User.login == login).scalar()
    if (user != None):
        order = Order()
        order.units = units
        order.address = address
        order.user_id = user.id
        order.save()

        update_order_state(order.id, Order_state._STATES[0], request)

    return ''


def update_order_state(order_id, state, request):

    order_state = Order_state()
    order_state.order_id = order_id
    order_state.state = state
    order_state.date = datetime.datetime.now()
    order_state.save()

    notify_order_update(order_state, request)

    return ''


def notify_order_update(order_state, request):
    if order_state.state == 0:
        notify_new_order_to_admin_by_email(order_state, request)
    else:
        notify_order_update_to_user_by_email(order_state, request)


def notify_order_update_to_user_by_email(order_state, request):
    localizer = get_localizer(request)

    # Create the body of the message (a plain-text and an HTML version).
    text_ts = _('plain_order_update_user_mail',
        mapping={'name': order_state.order.user.name,
                 'login': order_state.order.user.login,
                 'units': order_state.order.units,
                 'address': order_state.order.address,
                 'url': request.route_url('orders'),
                 'state': localizer.translate(_('order_state_' + str(order_state.state),
                            domain='Ondestan'))},
        domain='Ondestan')
    html_ts = _('html_order_update_user_mail',
        mapping={'name': order_state.order.user.name,
                 'login': order_state.order.user.login,
                 'units': order_state.order.units,
                 'address': order_state.order.address,
                 'url': request.route_url('orders'),
                 'state': localizer.translate(_('order_state_' + str(order_state.state),
                            domain='Ondestan'))},
        domain='Ondestan')
    subject_ts = _('subject_order_update_user_mail', domain='Ondestan')

    text = localizer.translate(text_ts)
    html = localizer.translate(html_ts)
    subject = localizer.translate(subject_ts)

    send_mail(html, text, subject, order_state.order.user.email)


def notify_new_order_to_admin_by_email(order_state, request):
    admin_email = Config.get_string_value('config.admin_email')
    if admin_email != None and admin_email != '':
        localizer = get_localizer(request)

        # Create the body of the message (a plain-text and an HTML version).
        text_ts = _('plain_new_order_admin_mail',
            mapping={'name': order_state.order.user.name,
                     'login': order_state.order.user.login,
                     'units': order_state.order.units,
                     'address': order_state.order.address,
                     'url': request.route_url('orders'),
                     'state': _('order_state_0',
                                domain='Ondestán')},
            domain='Ondestan')
        html_ts = _('html_new_order_admin_mail',
            mapping={'name': order_state.order.user.name,
                     'login': order_state.order.user.login,
                     'units': order_state.order.units,
                     'address': order_state.order.address,
                     'url': request.route_url('orders'),
                     'state': _('order_state_0',
                                domain='Ondestán')},
            domain='Ondestan')
        subject_ts = _('subject_new_order_admin_mail', domain='Ondestan')

        text = localizer.translate(text_ts)
        html = localizer.translate(html_ts)
        subject = localizer.translate(subject_ts)

        send_mail(html, text, subject, admin_email)


def get_order_by_id(order_id):
    return Order().queryObject().filter(Order.id == order_id).scalar()


def get_all_new_orders():
    session = Db.instance().session
    # First we create a subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    # Filter orders by checking which ones have a last state with state 0
    return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order_state.state == Order_state._STATES[0])).order_by(
        desc(Order_state.date)).all()


def get_all_pending_orders(login=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if login != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(login=login), Order_state.state != Order_state._STATES
        [len(Order_state._STATES) - 1])).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)),
        Order_state.state != Order_state._STATES[len(Order_state._STATES)\
        - 1]).order_by(Order_state.state, desc(Order_state.date)).all()


def get_all_unprocessed_orders(login=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if login != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(login=login), Order_state.state != Order_state._STATES
        [len(Order_state._STATES) - 1])).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)),
        Order_state.state != Order_state._STATES[len(Order_state._STATES)\
        - 1]).order_by(Order_state.state, desc(Order_state.date)).all()


def get_all_processed_orders(login=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if login != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(login=login), Order_state.state == Order_state._STATES
        [len(Order_state._STATES) - 1])).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)),
        Order_state.state == Order_state._STATES[len(Order_state._STATES)\
        - 1]).order_by(Order_state.state, desc(Order_state.date)).all()


def get_all_orders(login=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if login != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(login=login))).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)).\
        order_by(Order_state.state, desc(Order_state.date)).all()
