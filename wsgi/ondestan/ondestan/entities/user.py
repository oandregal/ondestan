# coding=UTF-8
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ondestan.entities import Entity
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
    role = relationship("Role")

    @hybrid_property
    def pending_orders(self):
        return filter(self.is_pending, self.orders)

    @hybrid_property
    def processed_orders(self):
        return filter(self.is_processed, self.orders)

    def is_pending(self, order):
        return order.is_pending

    def is_processed(self, order):
        return not order.is_pending
