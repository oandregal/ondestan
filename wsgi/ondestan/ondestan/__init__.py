#!/usr/bin/python
# -*- coding: UTF-8 -*-
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from ondestan.config import Config
import helpers
import logging
import sys


def add_renderer_globals(event):
    """ add helpers """
    event['h'] = helpers


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings,
                          root_factory='ondestan.models.RootFactory')
    Config.init_settings(settings)

    encoding = Config.get_string_value('config.default_encoding')
    if encoding != '' and encoding != None:
        reload(sys)
        sys.setdefaultencoding(encoding)

    from ondestan.services import user_service
    from ondestan.utils.db import Db

    Db.instance()
    logger = logging.getLogger('ondestan')
    authn_policy = AuthTktAuthenticationPolicy(
        'ondestan', callback=user_service.group_finder
    )
    authz_policy = ACLAuthorizationPolicy()
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_translation_dirs('ondestan:locale')
    config.add_route('default', '/')
    config.add_route('tour', '/tour')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('reminder', '/users/reminder')
    config.add_route('password_reset', '/users/password_reset/{loginhash}')
    config.add_route('signup', '/users/signup')
    config.add_route('signup_success', '/users/signup_success')
    config.add_route('update_profile', '/users/update')
    config.add_route('activate_user', '/users/activate/{loginhash}')
    config.add_route('gps_update', '/gps_update')

    config.add_route('check_user_login', '/users/check_login')
    config.add_route('check_user_email', '/users/check_email')
    config.add_route('check_device_imei', '/devices/check_imei')
    config.add_route('check_device_phone', '/devices/check_phone')

    config.add_route('orders', '/orders')
    config.add_route('order_state_history', '/orders/history/{order_id}')
    config.add_route('order_devices', '/orders/devices/{order_id}')
    config.add_route('delete_device', '/devices/delete/{device_id}')

    config.add_route('notifications', '/notifications')

    config.add_route('activate_device', '/devices/activate/{device_id}')
    config.add_route('deactivate_device', '/devices/deactivate/' +
                     '{device_id}')
    config.add_route('update_animal_name', '/animals/update_name')

    config.add_route('create_plot', '/plots/create')
    config.add_route('update_plot_geom', '/plots/update_geom')
    config.add_route('delete_plot', '/plots/delete_plot')

    config.add_route('map', '/map')
    config.add_route('json_animals', '/json/animals.json')
    config.add_route('json_inactive_animals', '/json/inactive_animals.json')
    config.add_route('json_plots', '/json/plots.json')
    config.scan()

    logger.info('Application initialized')

    return config.make_wsgi_app()
