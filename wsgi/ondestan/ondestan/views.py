# coding=UTF-8
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPOk,
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMethodNotAllowed
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
from ondestan.services import order_service, notification_service
from ondestan.gps import comms_service
from ondestan.gps.gps_update_error import GpsUpdateError

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
        # never use the login form itself as came_from
        # use main view instead
        referrer = 'map'
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


@view_config(route_name='gps_update')
def gps_update(request):
    if request.method == 'POST':
        response = 'fabi:0,0,0,0'
        try:
            comms_service.process_gps_updates(request)
            return HTTPOk(body_template=response)
        except GpsUpdateError as e:
            logger.error("Gps update couldn't be processed: " + e.msg)
            if e.code == 403:
                return HTTPForbidden(detail=e.msg, body_template=response)
            return HTTPBadRequest(detail=e.msg, body_template=response)
    logger.warning("Gps update requested with wrong method.")
    return HTTPMethodNotAllowed()


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


@view_config(route_name='update_animal_name', renderer='templates/signup.pt')
def update_animal_name(request):
    if 'name' in request.params and 'id' in request.params:
        animal_service.update_animal_name(request.params['id'],
                                          request.params['name'])
    return HTTPFound(location=request.route_url('map'))


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
        id=user_id,
        login=login,
        name=name,
        email=email,
        phone=phone
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


@view_config(route_name='check_device_phone', renderer='json',
             permission='admin')
def check_device_phone(request):
    if 'phone' in request.params:
        phone = request.params['phone']
        animal = animal_service.get_animal_by_phone(phone)
        if (animal == None):
            return True
        if 'id' in request.params:
            if animal.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('device_phone_already_use', domain='Ondestan')
    return localizer.translate(message_ts)


@view_config(route_name='check_device_imei', renderer='json',
             permission='admin')
def check_device_imei(request):
    if 'imei' in request.params:
        imei = request.params['imei']
        animal = animal_service.get_animal_by_imei(imei)
        if (animal == None):
            return True
        if 'id' in request.params:
            if animal.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('device_imei_already_use', domain='Ondestan')
    return localizer.translate(message_ts)


@view_config(route_name='check_user_login', renderer='json')
def check_user_login(request):
    if 'login' in request.params:
        login = request.params['login']
        user = user_service.get_user_by_login(login)
        if (user == None):
            return True
        if 'id' in request.params:
            if user.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('user_login_already_use', domain='Ondestan')
    return localizer.translate(message_ts)


@view_config(route_name='check_user_email', renderer='json')
def check_user_email(request):
    if 'email' in request.params:
        email = request.params['email']
        user = user_service.get_user_by_email(email)
        if (user == None):
            return True
        if 'id' in request.params:
            if user.id == int(request.params['id']):
                return True
    localizer = get_localizer(request)
    message_ts = _('user_email_already_use', domain='Ondestan')
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

    is_admin = check_permission('admin', request)

    return dict(
        message=message,
        units=units,
        address=address,
        pending_orders=pending_orders,
        processed_orders=processed_orders,
        is_admin=is_admin
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
        order=order
        )


@view_config(route_name='order_devices',
             renderer='templates/orderDevices.pt',
             permission='admin')
def order_devices(request):
    order = order_service.get_order_by_id(
                request.matchdict['order_id'])
    if (order == None):
        raise HTTPFound(request.route_url("orders"))
    if 'form.submitted' in request.params:
        if 'imei' in request.params and 'phone' in request.params:
            imei = request.params['imei']
            phone = request.params['phone']
            name = request.params['name']

            animal_service.create_animal(imei, phone, order, name)

    return dict(
        order=order,
        )


@view_config(route_name='notifications',
             renderer='templates/notifications.pt',
             permission='view')
def notifications(request):
    return dict(
        is_admin=check_permission('admin', request),
        notifications=notification_service.get_all_notifications(request)
        )


@view_config(route_name='delete_device',
             permission='admin')
def delete_device(request):
    order_id = animal_service.get_animal_by_id(request.matchdict['device_id'])\
               .order_id
    animal_service.delete_animal_by_id(
                request.matchdict['device_id'])
    raise HTTPFound(request.route_url("order_devices", order_id=order_id))


@view_config(route_name='activate_device',
             permission='view')
def activate_device(request):
    animal_service.activate_animal_by_id(request)
    raise HTTPFound(request.route_url("map"))


@view_config(route_name='deactivate_device',
             permission='view')
def deactivate_device(request):
    animal_service.deactivate_animal_by_id(request)
    raise HTTPFound(request.route_url("map"))


@view_config(route_name='map', renderer='templates/simpleViewer.pt',
             permission='view')
def viewer(request):
    user = user_service.get_user_by_login(get_user_login(request))
    is_admin = check_permission('admin', request)
    return dict(
        project=u'Ondestán',
        can_edit=check_permission('edit', request),
        is_admin=is_admin,
        non_admin_users=user_service.get_non_admin_users() if is_admin else [],
        view=user.get_bounding_box_as_json(),
        notifications=notification_service.\
            get_new_web_notifications_for_logged_user(request)
    )


@view_config(route_name='default')
def default(request):
    raise HTTPFound(request.route_url("map"))


@view_config(route_name='create_plot', renderer='json',
             permission='view')
def create_plot(request):
    points = []
    i = 0
    while ('x' + str(i)) in request.GET and ('y' + str(i)) in request.GET:
        points.append([float(request.GET['x' + str(i)]), float(request.GET['y'
                                                                + str(i)])])
        i += 1

    if 'userid' in request.GET:
        if check_permission('admin', request):
            userid = request.GET['userid']
        else:
            return {'success': False}
    else:
        userid = user_service.get_user_by_login(get_user_login(request)).id

    plot = plot_service.create_plot(points, userid)

    if plot == None:
        return {'success': False}
    else:
        feature = {
                    "type": "Feature",
                    "properties": {
                        "id": plot.id,
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": plot.name
                    },
                    "geometry": eval(plot.geojson)
                }
        return {'success': True, 'feature': feature}


@view_config(route_name='update_plot_geom', renderer='json',
             permission='view')
def update_plot_geom(request):
    user = user_service.get_user_by_login(get_user_login(request))
    points = []
    i = 0
    while ('x' + str(i)) in request.GET and ('y' + str(i)) in request.GET:
        points.append([float(request.GET['x' + str(i)]), float(request.GET['y'
                                                                + str(i)])])
        i += 1
    plot_id = request.GET['id']
    plot = plot_service.update_plot_geom(points, plot_id, user.id)

    if plot == None:
        return {'success': False}
    else:
        feature = {
                    "type": "Feature",
                    "properties": {
                        "id": plot_id,
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": plot.name
                    },
                    "geometry": eval(plot.geojson)
                }
        return {'success': True, 'feature': feature}


@view_config(route_name='delete_plot', renderer='json',
             permission='view')
def delete_plot(request):
    user = user_service.get_user_by_login(get_user_login(request))
    plot_id = request.GET['id']
    return {'success': plot_service.delete_plot(plot_id, user.id)}


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
                if animal.n_positions > 0:
                    if animal.name != None and len(animal.name) > 0:
                        name = animal.name
                    else:
                        name = animal.imei
                    parameters = {'animal_name': name,
                        'name': animal.user.name,
                        'battery': str(animal.positions[0].battery)
                        }
                    popup_str = _("animal_popup_admin", domain='Ondestan', mapping=parameters);
                    geojson.append({
                        "type": "Feature",
                        "properties": {
                            "id": animal.id,
                            "name": animal.name,
                            "imei": animal.imei,
                            "battery": animal.positions[0].battery,
                            "owner": animal.user.login,
                            "active": animal.active,
                            "outside": animal.positions[0].outside(),
                            "popup": get_localizer(request).translate(popup_str)
                        },
                        "geometry": eval(animal.positions[0].geojson)
                    })
                else:
                    geojson.append({
                        "type": "Feature",
                        "properties": {
                            "id": animal.id,
                            "name": animal.name,
                            "imei": animal.imei,
                            "battery": None,
                            "owner": animal.user.login,
                            "active": animal.active,
                            "outside": None,
                            "popup": None
                        },
                        "geometry": None
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
                if animal.n_positions > 0:
                    if animal.name != None and len(animal.name) > 0:
                        name = animal.name
                    else:
                        name = animal.imei
                    parameters = {'animal_name': name,
                        'battery': str(animal.positions[0].battery)
                        }
                    popup_str = _("animal_popup", domain='Ondestan', mapping=parameters);
                    geojson.append({
                        "type": "Feature",
                        "properties": {
                            "id": animal.id,
                            "name": animal.name,
                            "imei": animal.imei,
                            "battery": animal.positions[0].battery,
                            "owner": animal.user.login,
                            "active": animal.active,
                            "outside": animal.positions[0].outside(),
                            "popup": get_localizer(request).translate(popup_str)
                        },
                        "geometry": eval(animal.positions[0].geojson)
                    })
                else:
                    geojson.append({
                        "type": "Feature",
                        "properties": {
                            "id": animal.id,
                            "name": animal.name,
                            "imei": animal.imei,
                            "battery": None,
                            "owner": animal.user.login,
                            "active": animal.active,
                            "outside": None,
                            "popup": None
                        },
                        "geometry": None
                    })
        else:
            logger.debug("Found no animals for user " + login)
    return geojson


@view_config(route_name='json_inactive_animals', renderer='json',
             permission='view')
def json_inactive_animals(request):
    json = []
    if (check_permission('admin', request)):
        animals = animal_service.get_inactive_animals()
        if animals != None:
            logger.debug("Found " + str(len(animals)) +
                         " inactive animals for all users")
            for animal in animals:
                json.append({
                    "id": animal.id,
                    "name": animal.name,
                    "owner": animal.user.login,
                })
        else:
            logger.debug("Found no inactive animals for any user")
    else:
        login = get_user_login(request)
        animals = animal_service.get_inactive_animals(login)
        if animals != None:
            logger.debug("Found " + str(len(animals)) +
                         " inactive animals for user " + login)
            for animal in animals:
                json.append({
                    "id": animal.id,
                    "name": animal.name,
                    "owner": animal.user.login,
                })
        else:
            logger.debug("Found no inactive animals for user " + login)
    return json


@view_config(route_name='json_plots', renderer='json',
             permission='view')
def json_plots(request):
    geojson = []
    if (check_permission('admin', request)):
        plots = plot_service.get_all_plots()
        if plots != None:
            logger.debug("Found " + str(len(plots)) + " plots for all users")
            for plot in plots:
                parameters = {'plot_name': plot.name,
                    'name': plot.user.name
                    }
                popup_str = _("plot_popup_admin", domain='Ondestan', mapping=parameters);
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "id": plot.id,
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": get_localizer(request).translate(popup_str)
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
                parameters = {'plot_name': plot.name,
                    'name': plot.user.name
                    }
                popup_str = _("plot_popup", domain='Ondestan', mapping=parameters);
                geojson.append({
                    "type": "Feature",
                    "properties": {
                        "id": plot.id,
                        "name": plot.name,
                        "owner": plot.user.login,
                        "popup": get_localizer(request).translate(popup_str)
                    },
                    "geometry": eval(plot.geojson)
                })
        else:
            logger.debug("Found no plots for user " + login)
    return geojson
