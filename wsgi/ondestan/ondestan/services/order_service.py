# coding=UTF-8
from sqlalchemy import func, tuple_, and_, desc

from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

from datetime import datetime
import logging

from ondestan.entities import Order, User, Order_state
from ondestan.security import get_user_email, check_permission
from ondestan.utils import (
        Db,
        HtmlContainer
        )
import ondestan.services

logger = logging.getLogger('ondestan')

# We put these 18n strings here so they're detected when parsing files
_('order_update_state_0_notification_web', domain='Ondestan')
_('order_update_state_0_notification_mail_subject', domain='Ondestan')
_('order_update_state_0_notification_mail_html_body', domain='Ondestan')
_('order_update_state_0_notification_mail_text_body', domain='Ondestan')

_('order_update_state_1_notification_web', domain='Ondestan')
_('order_update_state_1_notification_mail_subject', domain='Ondestan')
_('order_update_state_1_notification_mail_html_body', domain='Ondestan')
_('order_update_state_1_notification_mail_text_body', domain='Ondestan')

_('order_update_state_2_notification_web', domain='Ondestan')
_('order_update_state_2_notification_mail_subject', domain='Ondestan')
_('order_update_state_2_notification_mail_html_body', domain='Ondestan')
_('order_update_state_2_notification_mail_text_body', domain='Ondestan')

_('order_update_state_3_notification_web', domain='Ondestan')
_('order_update_state_3_notification_mail_subject', domain='Ondestan')
_('order_update_state_3_notification_mail_html_body', domain='Ondestan')
_('order_update_state_3_notification_mail_text_body', domain='Ondestan')

_('order_update_state_4_notification_web', domain='Ondestan')
_('order_update_state_4_notification_mail_subject', domain='Ondestan')
_('order_update_state_4_notification_mail_html_body', domain='Ondestan')
_('order_update_state_4_notification_mail_text_body', domain='Ondestan')

_('new_order_user_notification_mail_subject', domain='Ondestan')
_('new_order_user_notification_mail_html_body', domain='Ondestan')
_('new_order_user_notification_mail_text_body', domain='Ondestan')

_('new_order_admin_notification_web', domain='Ondestan')
_('new_order_admin_notification_mail_subject', domain='Ondestan')
_('new_order_admin_notification_mail_html_body', domain='Ondestan')
_('new_order_admin_notification_mail_text_body', domain='Ondestan')


def get_orders(request):
    is_admin = check_permission('admin', request)
    if is_admin:
        new_orders = get_all_pending_orders()
    else:
        new_orders = get_all_pending_orders(
            get_user_email(request))
    return new_orders


def get_orders_popover(request, new_orders):
    popover_content = ''
    n_orders = {}
    for order in new_orders:
        state = order.states[0].state
        if not state in n_orders:
            n_orders[state] = 1
        else:
            n_orders[state] += 1
    localizer = get_localizer(request)
    for state in n_orders:
        popover_content += '<li>' + str(n_orders[state]) + ' en ' + \
        localizer.translate(_('order_state_' + str(state), domain='Ondestan'))\
        + '</li>'
    return HtmlContainer(popover_content)


def create_order(request):
    email = get_user_email(request)
    units = int(request.params['units'])
    address = request.params['address']
    user = User().queryObject().filter(User.email == email).scalar()
    if (user != None):
        order = Order()
        order.units = units
        order.address = address
        order.user_id = user.id
        order.save()

        order_state = Order_state()
        order_state.order_id = order.id
        order_state.state = Order_state._STATES[0]
        order_state.date = datetime.utcnow()
        order_state.save()

        notify_new_order(order_state, request)

    return ''


def update_order_state(order_id, state, request):
    order_state = Order_state()
    order_state.order_id = order_id
    order_state.state = state
    order_state.date = datetime.utcnow()
    order_state.save()

    notify_order_update(order_state, request)

    return ''


def notify_order_update(order_state, request):
    parameters = {'name': order_state.order.user.name,
                 'login': order_state.order.user.email,
                 'units': order_state.order.units,
                 'address': order_state.order.address,
                 'map_url': request.route_url('map'),
                 'url': request.route_url('orders')
                 }
    ondestan.services.notification_service.process_notification(
        'order_update_state_' + str(order_state.state),
        order_state.order.user.email, True, 1, True, False, parameters)


def notify_new_order(order_state, request):
    parameters = {'name': order_state.order.user.name,
                 'login': order_state.order.user.email,
                 'units': order_state.order.units,
                 'address': order_state.order.address,
                 'url': request.route_url('orders'),
                 'state': "_('order_state_0', domain='Ondestán')"}
    ondestan.services.notification_service.process_notification(
        'new_order_user', order_state.order.user.email, False, 0, True, False,
        parameters)

    admins = ondestan.services.user_service.get_admin_users()
    for admin in admins:
        ondestan.services.notification_service.process_notification(
            'new_order_admin', admin.email, True, 1, True, False, parameters)


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


def get_all_pending_orders(email=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if email != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(email=email), Order_state.state < Order_state._STATES
        [len(Order_state._STATES) - 2])).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)),
        Order_state.state < Order_state._STATES[len(Order_state._STATES)\
        - 2]).order_by(Order_state.state, desc(Order_state.date)).all()


def get_all_processed_orders(email=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if email != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(email=email), Order_state.state >= Order_state._STATES
        [len(Order_state._STATES) - 2])).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)),
        Order_state.state >= Order_state._STATES[len(Order_state._STATES)\
        - 2]).order_by(Order_state.state, desc(Order_state.date)).all()


def get_all_orders(email=None):
    session = Db.instance().session
    # Create subquery for retrieving the last state of each order
    subquery = session.query(
        Order_state.order_id, func.max(Order_state.date)
    ).group_by(Order_state.order_id).subquery()
    if email != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(email=email))).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)).\
        order_by(Order_state.state, desc(Order_state.date)).all()
