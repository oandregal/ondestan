# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry

from ondestan.entities import Entity
from ondestan.utils import Base


class Position(Entity, Base):

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    battery_level = Column(Float)
    date = Column(DateTime)
    animal_id = Column(Integer, ForeignKey("animals.id"))
    animal = relationship("Animal", backref=backref('positions',
                                                  order_by=date.desc()))
    geom = Column(Geometry('POINT'))
    geojson = column_property(geom.ST_AsGeoJSON())

    @hybrid_property
    def outside(self):
        if (self.animal != None and self.animal.plot != None):
            return not self.session.scalar(
                self.animal.plot.geom.ST_Contains(self.geom)
            )
        return False
