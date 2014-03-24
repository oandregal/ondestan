# coding=UTF-8
import logging
import md5
from datetime import datetime
from gps_update_error import GpsUpdateError

logger = logging.getLogger('ondestan')
date_format = '%Y-%m-%dT%H:%M:%S'


def process_data_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length')
    if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5')
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.body).hexdigest():
        raise GpsUpdateError('Wrong MD5')
    process_data(request.params)


def process_data(params):
    if 'mac' in params and 'password' in params and 'date' in params:
        mac = str(params['mac'])
        date = datetime.strptime(str(params['date']), date_format)
        battery = float(params['battery'])
        coverage = float(params['coverage'])
        latitude = float(params['latitude'])
        longitude = float(params['longitude'])
        logger.info('Processing update for mac: ' + mac +
                ' for date ' + date.strftime(date_format) +
                ' with battery level ' + str(battery) +
                ' with coverage ' + str(coverage) +
                ' at latitude ' + str(latitude) +
                ' and longitude ' + str(longitude))
    elif 'mac[0]' in params and 'password[0]' in params and\
        'date[0]' in params:
        i = 0
        while ('mac[' + str(i) + ']' in params):
            mac = str(params['mac[' + str(i) + ']'])
            date = datetime.strptime(str(params['date[' + str(i) + ']']),
                                     date_format)
            battery = float(params['battery[' + str(i) + ']'])
            coverage = float(params['coverage[' + str(i) + ']'])
            latitude = float(params['latitude[' + str(i) + ']'])
            longitude = float(params['longitude[' + str(i) + ']'])
            logger.info('Processing update for mac: ' + mac +
                ' for date ' + date.strftime(date_format) +
                ' with battery level ' + str(battery) +
                ' with coverage ' + str(coverage) +
                ' at latitude ' + str(latitude) +
                ' and longitude ' + str(longitude))
            i += 1
    else:
        raise GpsUpdateError('Insufficient params')
