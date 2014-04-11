# coding=UTF-8
import pyproj
#import md5
from datetime import datetime
from gps_update_error import GpsUpdateError

from ondestan.services import animal_service
from ondestan.entities.position import Position
from ondestan.utils import Config

import logging

logger = logging.getLogger('ondestan')

data_header = Config.get_string_value('gps.data_header')
beacon_header = Config.get_string_value('gps.beacon_header')
positions_divider = Config.get_string_value('gps.positions_divider')
params_divider = Config.get_string_value('gps.params_divider')
params_positions = Config.get_string_value('gps.params_positions').split(',')
date_format =  Config.get_string_value('gps.date_format')
gps_proj = pyproj.Proj("+init=" + Config.get_string_value('gps.proj'))
viewer_proj = pyproj.Proj("+init=" + Config.get_string_value('gps.viewer_proj'))

base_data = {
    'imei': None,
    'date': None,
    'lat': None,
    'lon': None,
    'battery': None,
    'coverage': None
}


def process_gps_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length', 400)
    """if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5', 400)
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.params.keys()[0]).hexdigest():
        raise GpsUpdateError('Wrong MD5', 400)"""
    process_gps_params(request.params.keys()[0])


def process_gps_params(base_params):
    if base_params.startswith(beacon_header):
        logger.info("Answering OK to beacon data: '"
                       + base_params + "'")
        return
    if base_params.startswith(data_header):
        base_params = base_params.replace(data_header, '').strip()
        positions = base_params.split(positions_divider)
        for position in positions:
            params = position.split(params_divider)
            i = 0
            data = base_data.copy()
            # Temporarily return OK if the petition has too many params
            if len(params) > len(params_positions):
                logger.warning("Received a GPS update with too many params: '"
                               + position + "'")
                continue
            if (len(params) != len(params_positions)):
                raise GpsUpdateError('Insufficient POST params', 400)
            for key in params_positions:
                if key in data:
                    data[key] = params[i]
                i += 1
            process_gps_data(data)


def process_gps_data(data):
    try:
        if data['imei'] == None or data['imei'] == '' or data['date'] == None\
        or data['date'] == '' or data['lon'] == None or\
        data['lon'] == '' or data['lat'] == None or\
        data['lat'] == '':
            raise GpsUpdateError('Insufficient POST params', 400)
        animal = animal_service.get_animal(data['imei'])
        if animal == None:
            raise GpsUpdateError("No animal matches the passed credentials " +
                                 "(IMEI: '" + data['imei'] + "')", 403)
        if animal.active:
            process_gps_data_active(data, animal)
        else:
            process_gps_data_inactive(data, animal)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)


def process_gps_data_active(data, animal):
    try:
        position = Position()
        try:
            x, y = pyproj.transform(gps_proj, viewer_proj,
                float(data['lon']), float(data['lat']))
            position.geom = 'SRID=3857;POINT(' + str(x) + ' ' + str(y) +\
            ')'
        except RuntimeError as e:
            raise GpsUpdateError(e.message, 400)
        position.animal_id = animal.id
        position.date = datetime.strptime(data['date'], date_format)
        if data['battery'] != None:
            position.battery = float(data['battery'])
        if data['coverage'] != None:
            position.coverage = float(data['coverage'])
        if animal_service.get_animal_position_by_date(position.animal_id,
           position.date) == None:
            position.save()
            logger.info('Processed update for IMEI: ' + animal.imei +
                    ' for date ' + position.date.strftime(date_format))
        else:
            logger.warn('Position already exists for animal: ' + str(animal.id)
                    + ' for date ' + position.date.strftime(date_format))
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)


def process_gps_data_inactive(data, animal):
    try:
        logger.info('Processed update for inactive IMEI: ' + animal.imei)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)
