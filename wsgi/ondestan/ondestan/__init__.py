from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from ondestan.utils import Config
import logging


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings,
                          root_factory='ondestan.models.RootFactory')
    Config.init_settings(settings)

    from ondestan.services import user_service
    from ondestan.utils.db import Db

    Db.instance()
    logger = logging.getLogger('ondestan')
    authn_policy = AuthTktAuthenticationPolicy(
        'ondestan', callback=user_service.group_finder
    )
    authz_policy = ACLAuthorizationPolicy()
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_translation_dirs('ondestan:locale')
    config.add_route('default', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('reminder', '/reminder')
    config.add_route('password_reset', '/password_reset/{loginhash}')
    config.add_route('signup', '/signup')
    config.add_route('signup_success', '/signup_success')
    config.add_route('update_profile', '/update_profile')
    config.add_route('activate_user', '/activate/{loginhash}')
    config.add_route('gps_update', '/gps_update')

    config.add_route('check_login', '/check_login')
    config.add_route('check_email', '/check_email')
    config.add_route('check_imei', '/check_imei')

    config.add_route('orders', '/orders')
    config.add_route('order_state_history', '/orders/history/{order_id}')
    config.add_route('order_devices', '/orders/devices/{order_id}')
    config.add_route('delete_device', '/orders/devices/delete/{device_id}')
    config.add_route('activate_device', '/orders/devices/activate/{device_id}')
    config.add_route('deactivate_device', '/orders/devices/deactivate/' +
                     '{device_id}')
    config.add_route('update_animal_name', '/animals/update_name')

    config.add_route('map', '/map')
    config.add_route('json_animals', '/json/animals.json')
    config.add_route('json_inactive_animals', '/json/inactive_animals.json')
    config.add_route('json_plots', '/json/plots.json')
    config.scan()

    logger.info('Application initialized')

    return config.make_wsgi_app()
