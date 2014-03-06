# coding=UTF-8
import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .singleton import Singleton

Base = declarative_base()

host = config.get_string_value('db_host')
port = config.get_string_value('db_port')
db = config.get_string_value('db_dbname')
user = config.get_string_value('db_user')
password = config.get_string_value('db_password')

@Singleton
class Db(object):
 
    '''
 
    The DB Class should only exist once, thats why it has the @Singleton decorator.
 
    To Create an instance you have to use the instance method:
 
        db = Db.instance()
 
    '''
 
    engine = None
 
    session = None
 
    def __init__(self):
 
        self.engine = create_engine('postgresql+psycopg2://' + user + ':' + password + '@' + host + ':' + port + '/' + db, echo=True)
 
        Session = sessionmaker(bind=self.engine)
 
        self.session = Session()
 
        ## Create all Tables
 
        Base.metadata.create_all(self.engine)
 
    def instance(self, *args, **kwargs): 
 
        '''
 
        Dummy method, because several IDEs can not handle singletons in Python
 
        '''
 
        pass
