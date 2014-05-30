# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, func, and_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import array

from ondestan.entities import Entity
from ondestan.entities.position import Position
from ondestan.utils import Base


class Animal(Entity, Base):

    __tablename__ = "animals"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    imei = Column(String)
    phone = Column(String)
    active = Column(Boolean)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('animals',
                                                  order_by=name))
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", backref=backref('devices',
                                                  order_by=name))
    """plot_id = Column(Integer, ForeignKey("plots.id"))
    plot = relationship("Plot", backref=backref('animals',
                                                  order_by=name))"""

    @hybrid_property
    def n_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id).count()
        return 0

    @hybrid_property
    def positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id).order_by(Position.date.desc()).yield_per(100)
        return []

    @hybrid_property
    def currently_outside(self):
        if self.n_positions > 0:
            return self.positions[0].outside()
        return None

    def filter_positions(self, start=None, end=None):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id)
            if start != None:
                query = query.filter(Position.date >= start)
            if end != None:
                query = query.filter(Position.date <= end)
            return query.order_by(Position.date.asc()).yield_per(100)
        return []

    def n_filter_positions(self, start=None, end=None):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id)
            if start != None:
                query = query.filter(Position.date >= start)
            if end != None:
                query = query.filter(Position.date <= end)
            return query.count()
        return []

    def get_bounding_box_as_json(self):
        positions = []
        for position in self.positions:
            positions.append(position.geom)
            if len(positions) == 300:
                break
        return self.session.scalar(func.ST_AsGeoJson(func.ST_Envelope(
            func.ST_MakeLine(array(positions))))) if len(positions) > 0\
            else None

    def get_bounding_box(self):
        positions = []
        for position in self.positions:
            positions.append(position.geom)
            if len(positions) == 300:
                break
        return self.session.scalar(func.ST_Envelope(
            func.ST_MakeLine(array(positions)))) if len(positions) > 0\
            else None
