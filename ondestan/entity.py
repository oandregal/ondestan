from .db import Db

class Entity():
    
    session = Db.instance().session
 
    '''
 
    This is a baseclass with delivers all basic database operations
 
    '''
 
    def save(self):
 
        self.session.add(self)
 
        self.session.commit()
 
    def saveMultiple(self, objects = []):
 
        self.session.add_all(objects)
 
        self.session.commit()
 
    def update(self):
 
        self.session.commit()
 
    def delete(self):
 
        self.session.delete(self)
 
        self.session.commit()
 
    def queryObject(self):
 
        return self.session.query(self.__class__)