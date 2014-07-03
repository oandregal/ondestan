# coding=UTF-8
from pyramid.settings import asbool
from os.path import expandvars


class Config:

    config = {}

    @staticmethod
    def init_settings(settings):
        Config.config = settings

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
