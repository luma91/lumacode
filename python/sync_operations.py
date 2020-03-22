import os
import subprocess
import luma_log

# Get Logger
logger = luma_log.main(__file__)


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
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
            logger.info(proc.stdout)

    if sync_op == 'code_sync':
        logger.info('running code sync')
        source_path = '/mnt/Dropbox/lumacode/'
        backup_path = '/mnt/lumacode'
        cmd = ['/bin/sh', '-c', 'rsync -av \"' + source_path + '\" \"' + backup_path + '\" --delete']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        logger.info(proc.stdout)

    logger.info('Done')


if __name__ == "__main__":
    main('code_sync')
