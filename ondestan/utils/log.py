# coding=UTF-8
import logging
import config

if config.get_string_value('log_level').strip().lower() == 'debug':
    LOG_LEVEL = logging.DEBUG
elif config.get_string_value('log_level').strip().lower() == 'info':
    LOG_LEVEL = logging.INFO
elif config.get_string_value('log_level').strip().lower() == 'warning':
    LOG_LEVEL = logging.WARNING
elif config.get_string_value('log_level').strip().lower() == 'error':
    LOG_LEVEL = logging.ERROR
elif config.get_string_value('log_level').strip().lower() == 'critical':
    LOG_LEVEL = logging.CRITICAL
else:
    LOG_LEVEL = logging.WARNING
    
LOG_FILE = config.get_string_value('log_file')

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s  [%(module)s] %(message)s')
    log = logging.getLogger(name)
    log.setLevel(LOG_LEVEL)
    log.propagate = False
    sth = logging.StreamHandler()
    sth.setLevel(LOG_LEVEL)
    sth.setFormatter(formatter)
    log.addHandler(sth)
    if LOG_FILE != None and len(LOG_FILE) > 0:
        fhnd = logging.handlers.RotatingFileHandler(LOG_FILE, 'a', config.get_int_value('max_log_file_size') * 1000000, config.get_int_value('max_log_file_backups'))
        fhnd.setLevel(LOG_LEVEL)
        fhnd.setFormatter(formatter)
        log.addHandler(fhnd)
    return log