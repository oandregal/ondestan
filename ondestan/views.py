# coding=UTF-8
from pyramid.httpexceptions import (
    HTTPFound
    )

from pyramid.view import (
    view_config,
    forbidden_view_config
    )

from pyramid.security import (
    remember,
    forget
    )

from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

from ondestan.security import get_user_login, check_permission
from ondestan.services import plot_service, animal_service, user_service
from ondestan.services import order_service
import logging

logger = logging.getLogger('ondestan')


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    activated = False
    if 'activated' in request.params:
        activated = request.params['activated'].lower() == 'true'
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        if user_service.check_login_request(request):
            headers = remember(request, login)
            return HTTPFound(location=came_from,
                             headers=headers)

        localizer = get_localizer(request)
        message_ts = _('failed_login', domain='Ondestan')
        message = localizer.translate(message_ts)

    return dict(
        message=message,
        came_from=came_from,
        login=login,
        activated=activated
        )


@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    message = ''
    login = ''
    name = ''
    email = ''
    phone = ''
    if 'form.submitted' in request.params:
        message = user_service.create_user(request)
        if message != '':
            login = request.params['login']
            name = request.params['name']
            email = request.params['email']
            phone = request.params['phone']

    return dict(
        message=message,
        login=login,
        name=name,
        email=email,
        phone=phone,
        )


@view_config(route_name='update_profile',
             renderer='templates/updateProfile.pt',
             permission='view')
def update_profile(request):
    message = ''

    if 'form.submitted' in request.params:
        message = user_service.update_user(request)
        login = request.params['login']
        name = request.params['name']
        email = request.params['email']
        phone = request.params['phone']
        user_id = request.params['id']
    else:
        login = get_user_login(request)
        user = user_service.get_user_by_login(login)
        user_id = user.id
        name = user.name
        email = user.email
        phone = user.phone

    return dict(
        message=message,
        user_id=login,
        id=user_id,
        login=login,
        name=name,
        email=email,
        phone=phone,
        )


@view_config(route_name='reminder', renderer='templates/reminder.pt')
def reminder(request):
    email = ''
    if 'form.submitted' in request.params:
        user_service.remind_user(request)
        email = request.params['email']

    return dict(
        email=email,
        )


@view_config(route_name='activate_user')
def activate_usr(request):
    user_service.activate_user(request)
    return HTTPFound(location=request.route_url('login') + '?activated=true')


@view_config(route_name='password_reset',
             renderer='templates/passwordReset.pt')
def reset_password(request):
    user_service.reset_password(request)
    return dict()


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('login'),
                     headers=headers)


@view_config(route_name='check_login', renderer='json')
def check_login(request):
    if 'login' in request.params:
        login = request.params['login']
        user = user_service.get_user_by_login(login)
        if (user == None):
            return True
        if 'id' in request.params:
            if user.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('login_already_use', domain='Ondestan')
    return localizer.translate(message_ts)


@view_config(route_name='check_email', renderer='json')
def check_email(request):
    if 'email' in request.params:
        email = request.params['email']
        user = user_service.get_user_by_email(email)
        if (user == None):
            return True
        if 'id' in request.params:
            if user.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('email_already_use', domain='Ondestan')
    return localizer.translate(message_ts)


@view_config(route_name='orders', renderer='templates/orders.pt',
             permission='view')
def orders(request):
    message = ''
    units = ''
    address = ''
    if 'form.submitted' in request.params:
        if 'id' in request.params:
            order_id = int(request.params['id'])
            state = int(request.params['state'])

            message = order_service.update_order_state(order_id, state,
                                                       request)
        else:
            message = order_service.create_order(request)
            if message != '':
                units = request.params['units']
                address = request.params['address']

    is_admin = check_permission('admin', request)
    if is_admin:
        pending_orders = order_service.get_all_pending_orders()
        processed_orders = order_service.get_all_processed_orders()
    else:
        pending_orders = order_service.get_all_pending_orders(
            get_user_login(request))
        processed_orders = order_service.get_all_processed_orders(
            get_user_login(request))

    return dict(
        user_id=get_user_login(request),
        message=message,
        units=units,
        address=address,
        pending_orders=pending_orders,
        processed_orders=processed_orders,
        is_admin=is_admin,
        )


@view_config(route_name='order_state_history',
             renderer='templates/orderStateHistory.pt',
             permission='admin')
def order_state_history(request):
    order = order_service.get_order_by_id(
                request.matchdict['order_id'])
    if (order == None):
        raise HTTPFound(request.route_url("orders"))
    return dict(
        user_id=get_user_login(request),
        order=order,
        )


@view_config(route_name='map', renderer='templates/simpleViewer.pt',
             permission='view')
def viewer(request):
    is_admin = check_permission('admin', request)
    n_new_orders = 0
    if is_admin:
        n_new_orders = len(order_service.get_all_new_orders())
    else:
        n_new_orders = len(
            order_service.get_all_orders(get_user_login(request))
        )
    return dict(project=u'Ondestán',
                user_id=get_user_login(request),
                can_edit=check_permission('edit', request),
                is_admin=is_admin,
                orders_msg=n_new_orders)


@view_config(route_name='default')
def default(request):
    raise HTTPFound(request.route_url("map"))


@view_config(route_name='json_animals', renderer='json',
             permission='view')
def json_animals(request):
    geojson = []
    if (check_permission('admin', request)):
        animals = animal_service.get_all_animals()
        if animals != None:
            logger.debug("Found " + str(len(animals)) +
                         " animals for all users")
            for animal in animals:
                popup_str = animal.name + \
                            " (" + str(animal.battery_level) + \
                            "%), property of " + animal.user.name + \
                            " (" + animal.user.login + ")"
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": animal.name,
                        "battery_level": animal.battery_level,
                        "owner": animal.user.login,
                        "outside": animal.outside,
                        "popup": popup_str
                    },
                    "geometry": eval(animal.geojson)
                })
        else:
            logger.debug("Found no animals for any user")
    else:
        login = get_user_login(request)
        animals = animal_service.get_all_animals(login)
        if animals != None:
            logger.debug("Found " + str(len(animals)) +
                         " animals for user " + login)
            for animal in animals:
                popup_str = animal.name + " (" + str(animal.battery_level) + "%)"
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": animal.name,
                        "battery_level": animal.battery_level,
                        "owner": animal.user.login,
                        "outside": animal.outside,
                        "popup": popup_str
                    },
                    "geometry": eval(animal.geojson)
                })
        else:
            logger.debug("Found no animals for user " + login)
    return geojson


@view_config(route_name='json_plots', renderer='json',
             permission='view')
def json_plots(request):
    geojson = []
    if (check_permission('admin', request)):
        plots = plot_service.get_all_plots()
        if plots != None:
            logger.debug("Found " + str(len(plots)) + " plots for all users")
            for plot in plots:
                popup_str = plot.name + \
                            " property of " + plot.user.name + \
                            " (" + plot.user.login + ")"
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": popup_str
                    },
                    "geometry": eval(plot.geojson)
                })
        else:
            logger.debug("Found no plots for any user")
    else:
        login = get_user_login(request)
        plots = plot_service.get_all_plots(login)
        if plots != None:
            logger.debug("Found " + str(len(plots)) + " plots " + \
                         "for user " + login)
            for plot in plots:
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": plot.name
                    },
                    "geometry": eval(plot.geojson)
                })
        else:
            logger.debug("Found no plots for user " + login)
    return geojson
