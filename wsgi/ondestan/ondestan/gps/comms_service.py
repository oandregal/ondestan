# coding=UTF-8
import pyproj
import logging
import md5
from datetime import datetime
from gps_update_error import GpsUpdateError

from ondestan.services import animal_service
from ondestan.entities.position import Position

wgs84 = pyproj.Proj("+init=EPSG:4326")
epsg3857 = pyproj.Proj("+init=EPSG:3857")
logger = logging.getLogger('ondestan')
date_format = '%Y-%m-%dT%H:%M:%S'

base_data = {
    'mac': None,
    'password': None,
    'date': None,
    'lat': None,
    'lon': None,
    'coverage': None,
    'battery': None
}


def process_gps_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length', 400)
    if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5', 400)
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.body).hexdigest():
        raise GpsUpdateError('Wrong MD5', 400)
    process_gps_params(request.params)


def process_gps_params(params):
    if 'mac' in params:
        data = base_data.copy()
        for key in params:
            data[key] = params[key]
        process_gps_data(data)
    elif 'mac[0]' in params:
        i = 0
        subfix = '[' + str(i) + ']'
        while 'mac' + subfix in params:
            data = base_data.copy()
            for key in params:
                if key.endswith(subfix):
                    data[key[:-len(subfix)]] = params[key]
            process_gps_data(data)
            i += 1
            subfix = '[' + str(i) + ']'
    else:
        raise GpsUpdateError('Insufficient POST params', 400)


def process_gps_data(data):
    try:
        if data['mac'] == None or data['password'] == None or data['date']\
            == None or data['longitude'] == None or data['latitude'] == None:
            raise GpsUpdateError('Insufficient POST params', 400)
        position = Position()
        try:
            x, y = pyproj.transform(wgs84, epsg3857,
                float(data['longitude']), float(data['latitude']))
            position.geom = 'SRID=3857;POINT(' + str(x) + ' ' + str(y) +\
            ')'
        except RuntimeError as e:
            raise GpsUpdateError(e.message, 400)
        animal = animal_service.get_animal(data['mac'], data['password'])
        if animal == None:
            raise GpsUpdateError("No animal matches the passed credentials " +
                                 "(mac: '" + data['mac'] + "'; password: '" +
                                 data['password'] + "')", 403)
        position.animal_id = animal.id
        position.date = datetime.strptime(data['date'], date_format)
        if data['battery'] != None:
            position.battery = float(data['battery'])
        if data['coverage'] != None:
            position.coverage = float(data['coverage'])
        position.save()
        logger.info('Processed update for mac: ' + animal.mac +
                ' for date ' + position.date.strftime(date_format))
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)
