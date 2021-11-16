
import subprocess
import os
import time
import threading
from lumacode.citadel import constants


def make_thread(python_file):

    thread = threading.Thread(target=run_subprocess, args=(python_file, ))
    return thread


def run_subprocess(python_file):

    cmd = ['/bin/bash', '-c', 'export PYTHONPATH="%s" & %s %s' %
           (constants.BASE_PATH, constants.PYTHON_PATH, os.path.join(constants.BASE_PATH, 'lumacode', python_file))]

    while True:

        print(cmd)
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='')  # process line here

        # We should not get here, but if we do go back to start.
        print('process ended abnormally.')
        time.sleep(10)
