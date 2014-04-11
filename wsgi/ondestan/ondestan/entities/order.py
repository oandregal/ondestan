# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from ondestan.entities import Entity
from ondestan.utils import Base


class Order(Entity, Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    units = Column(Integer)
    address = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('orders',
                                                  order_by=id))

    @hybrid_property
    def state(self):
        return self.states[0].state

    @hybrid_property
    def is_pending(self):
        return (self.state != self.states[0].ACTIVATED)

    def __json__(self, request):
        return {
            'id': self.id,
            'units': self.units,
            'address': self.address,
            'username': self.user.name,
            'state': self.state,
            'states': self.states
        }
