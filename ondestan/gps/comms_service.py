# coding=UTF-8
import logging
import md5
from gps_update_error import GpsUpdateError

logger = logging.getLogger('ondestan')


def process_data_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length')
    if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5')
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.body).hexdigest():
        raise GpsUpdateError('Wrong MD5')
    params = request.params
    if ('mac' in params):
        mac = str(params['mac'])
        battery = str(params['battery'])
        process_data_update(mac, battery)
    elif ('mac[0]' in params):
        i = 0
        while ('mac[' + str(i) + ']' in params):
            mac = str(params['mac[' + str(i) + ']'])
            battery = str(params['battery[' + str(i) + ']'])
            process_data_update(mac, battery)
            i += 1


def process_data_update(mac, battery):
    logger.info('Processing update for mac: ' + mac +
                ' with battery level ' + battery)
