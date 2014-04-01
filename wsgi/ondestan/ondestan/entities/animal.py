# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from ondestan.entities import Entity
from ondestan.utils import Base


class Animal(Entity, Base):

    __tablename__ = "animals"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    mac = Column(String)
    password = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('animals',
                                                  order_by=name))
    plot_id = Column(Integer, ForeignKey("plots.id"))
    plot = relationship("Plot", backref=backref('animals',
                                                  order_by=name))

    @hybrid_property
    def outside(self):
        if (len(self.positions) > 0 and self.plot != None):
            return not self.session.scalar(
                self.plot.geom.ST_Contains(self.positions[0].geom)
            )
        return False
