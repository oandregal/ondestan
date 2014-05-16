# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from geoalchemy2 import Geometry

from ondestan.entities import Entity
from ondestan.utils import Base

from types import NoneType


class Position(Entity, Base):

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    battery = Column(Float)
    coverage = Column(Float)
    date = Column(DateTime)
    animal_id = Column(Integer, ForeignKey("animals.id"))
    animal = relationship("Animal")
    geom = Column(Geometry('POINT', Entity.srid))
    geojson = column_property(geom.ST_AsGeoJSON())

    def outside(self):
        if (self.animal != None and self.animal.user != None
            and self.animal.user.plots != None
            and len(self.animal.user.plots) > 0):
            for plot in self.animal.user.plots:
                if self.session.scalar(plot.geom.ST_Contains(self.geom)):
                    return False
            return True
        return False

    def similar_to_position(self, position):
        if type(self.geom) is str and not type(position.geom) is NoneType and not type(position.geom) is str:
            return self.geom == str(self.session.scalar(func.ST_AsEWKT(position.geom)))
        if type(position.geom) is str and not type(self.geom) is NoneType and not type(self.geom) is str:
            return position.geom == str(self.session.scalar(func.ST_AsEWKT(self.geom)))
        if type(self.geom) is str and type(position.geom) is str:
            return self.geom == position.geom
        if not type(self.geom) is NoneType and self.geom.data != None and\
           not type(position.geom) is NoneType and position.geom.data != None:
            return self.geom.data == position.geom.data
        return False
