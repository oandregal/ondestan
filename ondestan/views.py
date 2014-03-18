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
from ondestan.services import plot_service, cow_service, user_service
from ondestan.services import order_service
import logging

logger = logging.getLogger('ondestan')


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
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
    login = get_user_login(request)
    user = user_service.get_user_by_login(login)
    user_id = user.id
    name = user.name
    email = user.email
    phone = user.phone

    if 'form.submitted' in request.params:
        message = user_service.update_user(request)

    return dict(
        message=message,
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


@view_config(route_name='activate_user')
def activate_usr(request):
    user_service.activate_user(request)
    return HTTPFound(location=request.route_url('login'))


@view_config(route_name='new_order', renderer='templates/newOrder.pt',
             permission='view')
def new_order(request):
    message = ''
    units = ''
    address = ''
    if 'form.submitted' in request.params:
        message = order_service.create_order(request)
        if message != '':
            units = request.params['units']
            address = request.params['address']

    return dict(
        message=message,
        url=request.path_url,
        units=units,
        address=address,
        )


@view_config(route_name='map', renderer='templates/simpleViewer.pt',
             permission='view')
def viewer(request):
    is_admin = check_permission('admin', request)
    if is_admin:
        n_new_orders = len(order_service.get_all_new_orders())
        localizer = get_localizer(request)
        new_orders_msg = str(n_new_orders) + ' ' + localizer.pluralize('new_order', 'new_orders', n_new_orders, 'Ondestan')
    else:
        new_orders_msg = ''
    return dict(project=u'Ondestán',
                user_id=get_user_login(request),
                can_edit=check_permission('edit', request),
                is_admin=is_admin,
                new_orders_msg=new_orders_msg)


@view_config(route_name='default')
def default(request):
    raise HTTPFound(request.route_url("map"))


@view_config(route_name='json_cows', renderer='json',
             permission='view')
def json_cows(request):
    geojson = []
    if (check_permission('admin', request)):
        cows = cow_service.get_all_cows()
        if cows != None:
            logger.debug("Found " + str(len(cows)) + " cows for all users")
            for cow in cows:
                popup_str = cow.name + \
                            " (" + str(cow.battery_level) + \
                            "%), property of " + cow.user.name + \
                            " (" + cow.user.login + ")"
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": cow.name,
                        "battery_level": cow.battery_level,
                        "owner": cow.user.login,
                        "outside": cow.outside,
                        "popup": popup_str
                    },
                    "geometry": eval(cow.geojson)
                })
        else:
            logger.debug("Found no cows for any user")
    else:
        login = get_user_login(request)
        cows = cow_service.get_all_cows(login)
        if cows != None:
            logger.debug("Found " + str(len(cows)) + " cows for user " + login)
            for cow in cows:
                popup_str = cow.name + " (" + str(cow.battery_level) + "%)"
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "name": cow.name,
                        "battery_level": cow.battery_level,
                        "owner": cow.user.login,
                        "outside": cow.outside,
                        "popup": popup_str
                    },
                    "geometry": eval(cow.geojson)
                })
        else:
            logger.debug("Found no cows for user " + login)
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
