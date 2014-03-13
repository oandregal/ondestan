# coding=UTF-8
import logging

logger = logging.getLogger('ondestan')

def process_data_updates(params):
    if ('mac' in params):
        mac = str(params['mac'])
        process_data_update(mac)
    elif ('mac[0]' in params):
        i = 0
        while ('mac[' + str(i) + ']' in params):
            mac = str(params['mac[' + str(i) + ']'])
            process_data_update(mac)
            i += 1
    return True

def process_data_update(mac):
    logger.info('Processing update for mac: ' + mac)
