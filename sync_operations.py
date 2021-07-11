
import os
import platform
import shutil
import subprocess
import time
from lumacode import luma_log

# Get Logger
logger = luma_log.main(__file__)


def copy_command(src, dst):

    logger.info('copying %s to %s ' % (src, dst))
    shutil.copy2(src, dst)


def main(sync_op):

    if sync_op == 'security_sync':
        logger.info('running security sync')
        backup_dirs = ['Media Room', 'Back Room']
        source_path = '/volume1/surveillance'
        backup_path = '/volume1/Dropbox/Archive/Security/'

        for directory in backup_dirs:
            full_source_path = os.path.join(source_path, directory)
            logger.info("src: %s \ndst: %s\n" % (full_source_path, backup_path))

            cmd = ['/bin/sh', '-c', 'rsync -urv --delete-before --chmod=ugo=rw  \"' + full_source_path + '\" \"' + backup_path + '\"']
            proc = subprocess.run(cmd, stdout=subprocess.PIPE)
            logger.info(proc.stdout)

    if sync_op == 'code_sync':
        logger.info('running code sync')

        # Windows
        if "Windows" in platform.platform():
            logger.info("windows environment detected.")

            source_path = 'Z:\\python\\lumacode'
            destination_path = 'L:\\lumacode'

        # Linux
        else:
            source_path = '/mnt/Dropbox/python/lumacode'
            destination_path = '/mnt/python/lumacode'

        # Remove old destination
        try:
            shutil.rmtree(destination_path, ignore_errors=False)

        # Can't remove.
        except Exception as e:
            logger.error(e)

        # Allow File System to Catchup
        time.sleep(5)

        # Copy to destination
        shutil.copytree(
            source_path, destination_path, copy_function=copy_command,
            ignore=shutil.ignore_patterns('.git', '.idea', '__pycache__')
        )

    logger.info('Done')


if __name__ == "__main__":
    main('code_sync')
