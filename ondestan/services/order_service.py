# coding=UTF-8
from ondestan.entities import Order, User
from ondestan.security import get_user_login
import logging

logger = logging.getLogger('ondestan')


def create_order(request):
    # localizer = get_localizer(request)

    login = get_user_login(request)
    units = int(request.params['units'])
    address = request.params['address']
    user = User().queryObject().filter(User.login == login).scalar()
    if (user != None):
        order = Order()
        order.state = Order._STATES[0]
        order.units = units
        order.address = address
        order.user_id = user.id
        order.save()

    return ''


def update_order_state(request):

    order_id = int(request.params['id'])
    state = int(request.params['state'])

    order = get_order_by_id(order_id)
    order.state = state

    order.update()


def get_order_by_id(order_id):
    return Order().queryObject().filter(Order.id == order_id).scalar()


def get_all_new_orders():
    return Order().queryObject().filter(Order.state == Order._STATES[0]).all()


def get_all_orders(login=None):
    if login != None:
        return Order().queryObject().filter(
            Order.user.has(login=login)).order_by(Order.state).all()
    else:
        return Order().queryObject().order_by(Order.state).all()
