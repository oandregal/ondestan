# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from ondestan.entities import Entity
from ondestan.utils import Base


class Configuration(Entity, Base):

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    readtime = Column(Integer)
    sampletime = Column(Integer)
    datatime = Column(Integer)
    sent_date = Column(DateTime)
    animal_id = Column(Integer, ForeignKey("animals.id"))
    animal = relationship("Animal", backref=backref('configurations',
                                                  order_by=sent_date.desc()))

    def get_configuration_description(self):
        return "Sampletime: " + str(self.sampletime) + " Datatime: " + str(self.datatime)