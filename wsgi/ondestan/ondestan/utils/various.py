# coding=UTF-8
from pyramid.interfaces import (
    ILocalizer,
    ITranslationDirectories
    )
from pyramid.i18n import (
    get_localizer,
    TranslationString as _,
    make_localizer
    )

from ondestan.config import Config

from os import urandom
from itertools import islice, imap, repeat
import string
from datetime import datetime
from dateutil import tz
from dateutil.relativedelta import relativedelta

# We put these 18n strings here so they're detected when parsing files
_('year', domain='Ondestan')
_('years', domain='Ondestan')
_('month', domain='Ondestan')
_('months', domain='Ondestan')
_('day', domain='Ondestan')
_('days', domain='Ondestan')
_('hour', domain='Ondestan')
_('hours', domain='Ondestan')
_('minute', domain='Ondestan')
_('minutes', domain='Ondestan')
_('second', domain='Ondestan')
_('seconds', domain='Ondestan')

utc_timezone = tz.tzutc()
default_timezone = tz.gettz(Config.get_string_value('config.default_timezone'))
date_format = Config.get_string_value('config.get_date_format')


def rand_string(length=10):
    chars = set(string.ascii_uppercase + string.ascii_lowercase
                + string.digits)
    char_gen = (c for c in imap(urandom, repeat(1)) if c in chars)
    return ''.join(islice(char_gen, None, length))


def get_custom_localizer(locale):
    if locale == None:
        locale = Config.get_string_value('pyramid.default_locale_name')

    registry = Config.registry
    localizer = registry.queryUtility(ILocalizer, name=locale)

    if localizer is None:
        # no localizer utility registered yet
        tdirs = registry.queryUtility(ITranslationDirectories, default=[])
        localizer = make_localizer(locale, tdirs)

        registry.registerUtility(localizer, ILocalizer,
                                 name=locale)
    return localizer


def get_time_difference_now_from_utc(date):
    return get_time_difference_now(date.replace(tzinfo=utc_timezone))


def get_time_difference_now(date):
    now = datetime.utcnow()
    now = now.replace(tzinfo=utc_timezone)
    return relativedelta(now, date)  # capture the date difference


def compare_datetime_ago_from_utc(date, rdelta):
    return compare_datetime_ago(date.replace(tzinfo=utc_timezone), rdelta)


def compare_datetime_ago(date, rdelta):
    now = datetime.utcnow()
    now = now.replace(tzinfo=utc_timezone)
    return (date + rdelta) < now


def get_fancy_time(d, display_full_version=True, request=None, locale=None):

    """Returns a user friendly date format
    d: some datetime instace in the past
    display_second_unit: True/False

    Author: Sunil Arora (http://sunilarora.org/)
    """

    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    #some helpers lambda's
    plural = lambda x: 's' if x > 1 else ''
    singular = lambda x: x[:-1]
    #convert pluran (years) --> to singular (year)
    display_unit = lambda unit, name: '%s%s' %\
        (name, plural(unit)) if unit > 0 else ''

    #time units we are interested in descending order of significance
    tm_units = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']

    rdelta = get_time_difference_now(d)  # capture the date difference
    time_format = localizer.translate(_('meta_time_format_wo_seconds',
                                        domain='Ondestan'))
    exact_time = convert_from_utc(d, default_timezone).strftime(time_format)
    for idx, tm_unit in enumerate(tm_units):
        first_unit_val = getattr(rdelta, tm_unit)
        if first_unit_val > 0:
            primary_unit = localizer.translate(_(
                        display_unit(first_unit_val, singular(tm_unit)),
                        domain='Ondestan'))
            if display_full_version and idx < len(tm_units) - 1:
                next_unit = tm_units[idx + 1]
                second_unit_val = getattr(rdelta, next_unit)
                if second_unit_val > 0:
                    secondary_unit = localizer.translate(_(
                        display_unit(second_unit_val, singular(next_unit)),
                        domain='Ondestan'))
                    parameters = {
                        'primary_val': first_unit_val,
                        'primary_unit': primary_unit,
                        'secondary_val': second_unit_val,
                        'secondary_unit': secondary_unit,
                        'exact_time': exact_time
                    }
                    return localizer.translate(_("fancy_time_two_units",
                                                 domain='Ondestan',
                                                 mapping=parameters))
            parameters = {
                'primary_val': first_unit_val,
                'primary_unit': primary_unit,
                'exact_time': exact_time
            }
            return localizer.translate(_("fancy_time_one_unit",
                                         domain='Ondestan',
                                         mapping=parameters))
    return format_utcdatetime(d.astimezone(utc_timezone), request=request,
                              locale=locale)


def get_fancy_time_from_utc(d, display_full_version=True, request=None,
                            locale=None):
    return get_fancy_time(d.replace(tzinfo=utc_timezone), display_full_version,
                          request, locale)


def convert_to_utc(d, from_tz):
    return d.replace(tzinfo=from_tz).\
        astimezone(utc_timezone).replace(tzinfo=None)


def convert_from_utc(d, to_tz):
    return d.replace(tzinfo=utc_timezone).\
        astimezone(to_tz)


def format_utcdate(date, request=None, locale=None):
    local_date = convert_from_utc(date, default_timezone)
    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    date_format = localizer.translate(_('meta_date_format', domain='Ondestan'))
    return local_date.strftime(date_format)


def format_utcdatetime(datetime, request=None, locale=None):
    local_datetime = convert_from_utc(datetime, default_timezone)
    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    date_format = localizer.translate(_('meta_datetime_format',
                                        domain='Ondestan'))
    return local_datetime.strftime(date_format)


def format_utctime(time, request=None, locale=None):
    local_time = convert_from_utc(time, default_timezone)
    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    date_format = localizer.translate(_('meta_time_format', domain='Ondestan'))
    return local_time.strftime(date_format)


def parse_to_utcdatetime(dttm):
    local_datetime = internal_parse_datetime(dttm)
    return convert_to_utc(local_datetime, default_timezone)


def internal_parse_datetime(dttm):
    return datetime.strptime(dttm, date_format)


def internal_format_datetime(dttm):
    return dttm.strftime(date_format)


def escape_code_to_eval(st):
    return 'eval[' + st + ']eval'


def unescape_code_to_eval(st):
    return st.replace("'eval[", '').replace('"eval[', '').\
        replace("]eval'", '').replace(']eval"', '')

def get_device_preconfig_names(request=None, locale=None):
    nr = 1
    try:
        while True:
            Config.get_int_value('gps.preconfig_' + str(nr) + '_readtime')
            Config.get_int_value('gps.preconfig_' + str(nr) + '_sampletime')
            Config.get_int_value('gps.preconfig_' + str(nr) + '_datatime')
            nr = nr + 1
    except:
        pass

    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    device_preconfig_names = []
    for i in range(1, nr):
        device_preconfig_names.append(localizer.translate(_('gps_preconfig_' + str(i) + '_name', domain='Ondestan')))
    return device_preconfig_names

def get_device_config_fancy_description(config, request=None, locale=None):

    if request != None:
        localizer = get_localizer(request)
    else:
        localizer = get_custom_localizer(locale)

    datatime = get_device_config_fancy_description_unit_value(config.datatime)
    sampletime = get_device_config_fancy_description_unit_value(config.sampletime)
    readtime = get_device_config_fancy_description_unit_value(config.readtime)
    parameters = {
        'datatime_val': datatime[0],
        'datatime_unit': localizer.translate(_(datatime[1],
            domain='Ondestan')),
        'sampletime_val': sampletime[0],
        'sampletime_unit': localizer.translate(_(sampletime[1],
            domain='Ondestan')),
        'readtime_val': readtime[0],
        'readtime_unit': localizer.translate(_(readtime[1],
            domain='Ondestan'))
    }

    return localizer.translate(_("fancy_config_description",
         domain='Ondestan',
         mapping=parameters))

def get_device_config_fancy_description_unit_value(value):
    if value % 86400 == 0:
        if value == 86400:
            return ['', 'day']
        else:
            return [str(value / 86400), 'days']
    elif value % 3600 == 0:
        if value == 3600:
            return ['', 'hour']
        else:
            return [str(value / 3600), 'hours']
    elif value % 60 == 0:
        if value == 60:
            return ['', 'minute']
        else:
            return [str(value / 60), 'minutes']
    else:
        if value == 1:
            return ['', 'second']
        else:
            return [str(value), 'seconds']
