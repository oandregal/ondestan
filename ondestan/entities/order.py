# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from ondestan.entities import Entity
from ondestan.utils import Base


class Order(Entity, Base):

    __tablename__ = "orders"
    _STATES = [0, 1]

    id = Column(Integer, primary_key=True)
    units = Column(Integer)
    address = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    state = Column(Integer)
    user = relationship("User")
