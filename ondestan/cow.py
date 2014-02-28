from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry

from .entity import Entity
from .db import Base

class Cow(Entity, Base):

    __tablename__ = "cows"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    battery_level = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    plot_id = Column(Integer, ForeignKey("plots.id"))
    plot = relationship("Plot")
    geom = Column(Geometry('POINT'))
    geojson = column_property(geom.ST_AsGeoJSON())

    @hybrid_property
    def outside(self):
        if (self.plot != None):
            return not self.session.scalar(self.plot.geom.ST_Contains(self.geom));
        return False