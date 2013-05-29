import os
import sys
from argparse import ArgumentParser, FileType
from configobj import ConfigObj
import logging
from vdsmcodecoverage.daemon import VdsmWatcher
import signal


class LogFileType(FileType):
    """
    Log file type, always 'append' mode, and needs to make sure that target
    dir exists.
    """
    def __init__(self):
        super(LogFileType, self).__init__('a')

    def __call__(self, path):
        dir_ = os.path.dirname(path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        return super(LogFileType, self).__call__(path)


def sigterm_handler(sig, frame):
    raise SystemExit(0)


def create_parser():
    parser = ArgumentParser("daemon which keeps vdsm enabled")
    parser.add_argument('-c', '--conf', action='store', required=True)
    parser.add_argument('--log', action='store', default=None,
                        type=LogFileType())
    parser.add_argument('--debug', action='store_const', default=None,
                        const='INFO')
    parser.add_argument('--daemon', action='store_true', default=False)
    return parser


def merge_config(config, opt):
    config['log_level'] = 'DEBUG' if opt.debug\
        else config.get('log_level', 'INFO')


def main():
    parser = create_parser()
    opt = parser.parse_args()

    config = ConfigObj(infile=opt.conf)
    general = config.setdefault('general')
    merge_config(general, opt)

    level = getattr(logging, general['log_level'])
    stream = opt.log
    if not stream:
        if general.get('logfile', None):
            stream = LogFileType()(general['logfile'])
        else:
            stream = sys.stderr
    logging.basicConfig(level=level, stream=stream)

    pidfile = general['pidfile']
    if opt.daemon:
        pid = os.fork()
        if pid > 0:
            raise SystemExit(0)
        with open(general['pidfile'], 'w') as fh:
            fh.write(str(os.getpid()))

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)
    try:
        daemon = VdsmWatcher(general['path_to_vdsm'],
                             general['coverage_config'],
                             general['service_name'])
        daemon.run()
    finally:
        if pidfile and os.path.exists(pidfile):
            os.unlink(pidfile)


if __name__ == "__main__":
    main()
