# coding=UTF-8
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import array

from ondestan.entities import Entity
from ondestan.entities.position import Position
from ondestan.entities.configuration import Configuration
from ondestan.utils import Base
from ondestan.config import Config

from datetime import datetime

max_positions = Config.get_int_value('config.history_max_positions')

default_config_readtime = Config.get_int_value('gps.default_config_readtime')
default_config_sampletime = Config.get_int_value('gps.default_config_sampletime')
default_config_datatime = Config.get_int_value('gps.default_config_datatime')


class Animal(Entity, Base):

    __tablename__ = "animals"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    imei = Column(String)
    phone = Column(String)
    active = Column(Boolean)
    checks_wo_pos = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('animals',
                                                  order_by=name))
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", backref=backref('devices',
                                                  order_by=name))
    plot_id = Column(Integer, ForeignKey("plots.id"))
    plot = relationship("Plot", backref=backref('animals',
                                                  order_by=name))

    @hybrid_property
    def n_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == False).count()
        return 0

    @hybrid_property
    def positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == False).\
                    order_by(Position.date.desc()).yield_per(100)
        return []

    @hybrid_property
    def current_battery(self):
        if self.n_positions > 0:
            if int(self.all_positions[0].battery) == self.all_positions[0].battery:
                return int(self.all_positions[0].battery)
            else:
                return self.all_positions[0].battery
        return None

    @hybrid_property
    def current_battery_wo_charging(self):
        if self.n_positions > 0:
            if int(self.positions[0].battery) == self.positions[0].battery:
                return int(self.positions[0].battery)
            else:
                return self.positions[0].battery
        return None

    @hybrid_property
    def currently_charging(self):
        if self.n_positions > 0:
            return self.all_positions[0].charging
        return None

    @hybrid_property
    def currently_outside(self):
        if self.n_positions > 0:
            return self.positions[0].outside()
        return None

    @hybrid_property
    def n_all_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id).count()
        return 0

    @hybrid_property
    def all_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id).order_by(Position.date.desc()).yield_per(100)
        return []

    @hybrid_property
    def n_charging_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == True).count()
        return 0

    @hybrid_property
    def charging_positions(self):
        if self.id != None:
            return Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == True).\
                    order_by(Position.date.desc()).yield_per(100)
        return []

    def get_approx_position_as_geojson(self, time=datetime.utcnow(),
                                       filter_charging=True):
        positions = []
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id)
            if filter_charging:
                query = query.filter(Position.charging == False)
            query = query.filter(func.abs(
                    func.date_part('hour', Position.date - time)) <= 2)
            aux = query.order_by(Position.date.desc()).limit(50)
            for position in aux:
                positions.append(position.geom)
        return self.session.scalar(func.ST_AsGeoJson(
            func.ST_MinimumBoundingCircle(func.ST_Collect(
            array(positions))))) if len(positions) > 1\
            else None

    def filter_positions(self, start=None, end=None,
                                       filter_charging=True):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id)
            if filter_charging:
                query.filter(Position.charging == False)
            if start != None:
                query = query.filter(Position.date >= start)
            if end != None:
                query = query.filter(Position.date <= end)
            return query.order_by(Position.date.asc()).yield_per(100)
        return []

    def n_filter_positions(self, start=None, end=None,
                                        filter_charging=True):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id)
            if filter_charging:
                query.filter(Position.charging == False)
            if start != None:
                query = query.filter(Position.date >= start)
            if end != None:
                query = query.filter(Position.date <= end)
            return query.count()
        return []

    def filter_charging_positions(self, start=None, end=None):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == True)
            if start != None:
                query = query.filter(Position.date >= start)
            if end != None:
                query = query.filter(Position.date <= end)
            return query.order_by(Position.date.asc()).yield_per(100)
        return []

    def n_filter_charging_positions(self, start=None, end=None):
        if self.id != None:
            query = Position().queryObject().filter(Position.animal_id
                    == self.id, Position.charging == True)
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
            # We return the max number of positions plus one, so it can detect
            # there are more and not just the barrier number
            if len(positions) == (max_positions + 1):
                break
        return self.session.scalar(func.ST_AsGeoJson(func.ST_Envelope(
            func.ST_MakeLine(array(positions))))) if len(positions) > 0\
            else None

    def get_bounding_box(self):
        positions = []
        for position in self.positions:
            positions.append(position.geom)
            # We return the max number of positions plus one, so it can detect
            # there are more and not just the barrier number
            if len(positions) == (max_positions + 1):
                break
        return self.session.scalar(func.ST_Envelope(
            func.ST_MakeLine(array(positions)))) if len(positions) > 0\
            else None

    def save_new_configuration(self, readtime, sampletime, datatime):
        configuration = Configuration()
        configuration.readtime = readtime
        configuration.sampletime = sampletime
        configuration.datatime = datatime
        # If latest saved configuration hasn't been sent yet, then we delete it
        if len(self.configurations) != 0 and self.configurations[0].sent_date == None:
            self.configurations[0].delete()
        configuration.animal_id = self.id
        self.configurations.insert(0, configuration)
        self.configurations[0].save()

    def get_confirm_pending_configuration(self):
        # If latest saved configuration hasn't been sent yet, then we set its sent_date and return it
        if len(self.configurations) != 0 and self.configurations[0].sent_date == None:
            self.configurations[0].sent_date = datetime.utcnow()
            self.configurations[0].update()
            return self.configurations[0]
        return None

    def get_current_configuration(self):
        for configuration in self.configurations:
            if configuration.sent_date != None:
                return configuration
        configuration = Configuration()
        configuration.readtime = default_config_readtime
        configuration.sampletime = default_config_sampletime
        configuration.datatime = default_config_datatime
        return configuration
