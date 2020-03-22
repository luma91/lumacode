import logging
import os

logging_path = '/mnt/tmp/logs'


def main(application, machine_name=None):
    base_name = os.path.splitext(os.path.basename(application))[0]
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(base_name)
    logger.setLevel(logging.DEBUG)

    if machine_name:
        fh = logging.FileHandler(os.path.join(logging_path, base_name + '.' + machine_name + '.log'))
    else:
        fh = logging.FileHandler(os.path.join(logging_path, base_name + '.log'))

    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    formatter.datefmt = '%d/%m/%Y %H:%M:%S'
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
