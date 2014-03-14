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
        order.units = units
        order.address = address
        order.user_id = user.id
        order.save()

    return ''
