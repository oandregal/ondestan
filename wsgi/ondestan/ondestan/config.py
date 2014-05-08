# coding=UTF-8
from pyramid.settings import asbool


class Config:

    config = {}

    @staticmethod
    def init_settings(settings):
        Config.config = settings

    @staticmethod
    def get_string_value(field):
        return str(Config.config[field])

    @staticmethod
    def get_boolean_value(field):
        return asbool(Config.config[field])

    @staticmethod
    def get_int_value(field):
        return int(Config.config[field])

    @staticmethod
    def get_float_value(field):
        return float(Config.config[field])
