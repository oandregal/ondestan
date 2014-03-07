# coding=UTF-8
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .singleton import Singleton

Base = declarative_base()

host = Config.get_string_value('db.host')
port = Config.get_string_value('db.port')
db = Config.get_string_value('db.dbname')
user = Config.get_string_value('db.user')
password = Config.get_string_value('db.password')

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
