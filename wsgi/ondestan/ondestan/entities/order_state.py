# coding=UTF-8
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from ondestan.entities import Entity
from ondestan.utils import Base


class Order_state(Entity, Base):

    AWAITING = 0
    IN_PROCESS = 1
    DISPATCHED = 2
    ACTIVATED = 3

    __tablename__ = "order_states"
    _STATES = [AWAITING, IN_PROCESS, DISPATCHED, ACTIVATED]

    id = Column(Integer, primary_key=True)
    state = Column(Integer)
    date = Column(DateTime)
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", backref=backref('states',
                                                  order_by=date.desc()))

    def __json__(self, request):
        return {
            'id': self.id,
            'state': self.state,
            'date': self.date,
        }
