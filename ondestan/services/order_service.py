# coding=UTF-8
from sqlalchemy import func, tuple_, and_, desc

from ondestan.entities import Order, User, Order_state
from ondestan.security import get_user_login
from ondestan.utils import Db
import logging, datetime

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

        update_order_state(order.id, Order_state._STATES[0])

    return ''


def update_order_state(order_id, state):

    order_state = Order_state()
    order_state.order_id = order_id
    order_state.state = state
    order_state.date = datetime.datetime.now()
    order_state.save()

    return ''


def get_order_by_id(order_id):
    return Order().queryObject().filter(Order.id == order_id).scalar()


def get_all_new_orders():
    session = Db.instance().session
    # First we create a subquery for retrieving the last state of each order
    subquery = session.query(Order_state.order_id, func.max(Order_state.date)).\
         group_by(Order_state.order_id).subquery()
    # Then we filter the orders by checking which ones have a last state with state 0
    return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order_state.state == 0)).order_by(desc(Order_state.date)).all()


def get_all_orders(login=None):
    session = Db.instance().session
    # First we create a subquery for retrieving the last state of each order
    subquery = session.query(Order_state.order_id, func.max(Order_state.date)).\
         group_by(Order_state.order_id).subquery()
    if login != None:
        return Order().queryObject().join(Order_state).filter(and_(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery),
        Order.user.has(login=login))).order_by(Order_state.state,\
        desc(Order_state.date)).all()
    else:
        return Order().queryObject().join(Order_state).filter(
        tuple_(Order_state.order_id, Order_state.date).in_(subquery)).\
        order_by(Order_state.state, desc(Order_state.date)).all()
