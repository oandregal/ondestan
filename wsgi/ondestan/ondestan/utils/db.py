# coding=UTF-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from os.path import expandvars

from ondestan.config import Config
from ondestan.utils import Singleton

Base = declarative_base()


@Singleton
class Db(object):

    '''

    Should only exist once, thats why it has the @Singleton decorator.

    To Create an instance you have to use the instance method:

        db = Db.instance()

    '''

    engine = None

    session = None

    def __init__(self):

        self.session = scoped_session(
            sessionmaker(extension=ZopeTransactionExtension()))

        host = expandvars(Config.get_string_value('db.host'))
        port = expandvars(Config.get_string_value('db.port'))
        db = expandvars(Config.get_string_value('db.dbname'))
        user = expandvars(Config.get_string_value('db.user'))
        password = expandvars(Config.get_string_value('db.password'))

        conn_str = 'postgresql+psycopg2://' + user + ':' + password + \
                         '@' + host + ':' + port + '/' + db
        self.engine = create_engine(
            conn_str
        )
        self.session.configure(bind=self.engine)
        Base.metadata.bind = self.engine

    def instance(self, *args, **kwargs):

        '''

        Dummy method, because several IDEs can not handle singletons in Python

        '''

        pass
