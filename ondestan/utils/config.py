# coding=UTF-8
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('ondestan.cfg')

def get_string_value(field):
    return config.get('default', field)

def get_boolean_value(field):
    return config.getboolean('default', field)

def get_int_value(field):
    return config.getint('default', field)

def get_float_value(field):
    return config.getfloat('default', field)