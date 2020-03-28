import logging
import os
import platform

logging_path_linux = '/mnt/tmp/logs'
logging_path_windows = 'T:/logs/'
host_name = platform.node()
operating_system = platform.platform()


def main(application):

    if 'linux' in operating_system.lower():
        logging_path = logging_path_linux

    else:
        logging_path = logging_path_windows

    base_name = os.path.splitext(os.path.basename(application))[0]
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(base_name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(os.path.join(logging_path, base_name + '.' + host_name + '.log'))

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


if __name__ == "__main__":
    main('test')
