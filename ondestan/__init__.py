from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .services import user_service
from .utils.db import Db
from utils.log import setup_custom_logger

def main(global_config, **settings):
    logger = setup_custom_logger('ondestan')
    """ This function returns a Pyramid WSGI application.
    """
    authn_policy = AuthTktAuthenticationPolicy('ondestan', callback=user_service.group_finder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='ondestan.models.RootFactory')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_route('default', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('signup_success', '/signup_success')
    config.add_route('activate_user', '/activate/{loginhash}')

    config.add_route('map', '/map')
    config.add_route('json_cows', '/json/cows.json')
    config.add_route('json_plots', '/json/plots.json')
    config.scan()
    
    Db.instance()
    logger.info('Application initialized')
    
    return config.make_wsgi_app()
