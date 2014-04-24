# coding=UTF-8
from ondestan.utils import Db, Config


class Entity():

    session = Db.instance().session
    srid = Config.get_string_value('config.viewer_proj')

    '''

    This is a baseclass with delivers all basic database operations

    '''

    def save(self):

        result = self.session.add(self)

        self.session.flush()

    def saveMultiple(self, objects=[]):

        self.session.add_all(objects)

        self.session.flush()

    def update(self):

        self.session.merge(self)

        self.session.flush()

    def delete(self):

        self.session.delete(self)

        self.session.flush()

    def queryObject(self):

        return self.session.query(self.__class__)
