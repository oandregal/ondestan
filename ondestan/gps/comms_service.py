# coding=UTF-8
import logging

logger = logging.getLogger('ondestan')


def process_data_updates(params):
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
    return True


def process_data_update(mac, battery):
    logger.info('Processing update for mac: ' + mac +
                ' with battery level ' + battery)
