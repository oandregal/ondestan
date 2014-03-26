import os
from pyramid.paster import get_app, setup_logging
here = os.path.dirname(os.path.abspath(__file__))
conf = os.path.join(here, 'production.ini')
setup_logging(conf)
application = get_app(conf, 'main')