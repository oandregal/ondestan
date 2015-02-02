# coding=UTF-8
from pyramid.settings import asbool
from os.path import expandvars
from apscheduler.scheduler import Scheduler


class Config:

    config = {}
    sched = None
    registry = None

    @staticmethod
    def init_settings(settings, registry):
        Config.config = settings
        Config.sched = Scheduler(settings)
        Config.sched.start()
        Config.registry = registry

    @staticmethod
    def get_string_value(field):
        return str(expandvars(Config.config[field]))

    @staticmethod
    def get_boolean_value(field):
        return asbool(expandvars(Config.config[field]))

    @staticmethod
    def get_int_value(field):
        return int(expandvars(Config.config[field]))

    @staticmethod
    def get_float_value(field):
        return float(expandvars(Config.config[field]))
