# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, column_property
from geoalchemy2 import Geometry

from ondestan.entities import Entity
from ondestan.utils import Base


class Plot(Entity, Base):

    __tablename__ = "plots"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    geom = Column(Geometry('POLYGON'))
    geojson = column_property(geom.ST_AsGeoJSON())
