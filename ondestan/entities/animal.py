# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry

from ondestan.entities import Entity
from ondestan.utils import Base


class Animal(Entity, Base):

    __tablename__ = "animals"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    battery_level = Column(Float)
    type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('animals',
                                                  order_by=name))
    plot_id = Column(Integer, ForeignKey("plots.id"))
    plot = relationship("Plot", backref=backref('animals',
                                                  order_by=name))
    geom = Column(Geometry('POINT'))
    geojson = column_property(geom.ST_AsGeoJSON())

    @hybrid_property
    def outside(self):
        if (self.plot != None):
            return not self.session.scalar(
                self.plot.geom.ST_Contains(self.geom)
            )
        return False
