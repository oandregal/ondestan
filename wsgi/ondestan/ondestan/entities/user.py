# coding=UTF-8
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import array

from ondestan.entities import Entity, Role, Animal
from ondestan.utils import Base


class User(Entity, Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    password = Column(String)
    activated = Column(Boolean)
    last_login = Column(Date)
    locale = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", backref=backref('users',
                        order_by=login))

    @hybrid_property
    def get_bounding_box_as_json(self):
        positions = []
        if self.role.name == Role._ADMIN_ROLE:
            animals = Animal().queryObject().all()
        else:
            animals = self.animals
        for animal in animals:
            if len(animal.positions) > 0:
                positions.append(animal.positions[0].geom)
        return self.session.scalar(func.ST_AsGeoJson(func.ST_Envelope(
            func.ST_MakeLine(array(positions))))) if len(positions) > 0\
            else None

    @hybrid_property
    def get_bounding_box(self):
        positions = []
        if self.role.name == Role._ADMIN_ROLE:
            animals = Animal().queryObject().all()
        else:
            animals = self.animals
        for animal in animals:
            if len(animal.positions) > 0:
                positions.append(animal.positions[0].geom)
        return self.session.scalar(func.ST_Envelope(
            func.ST_MakeLine(array(positions)))) if len(positions) > 0\
            else None
