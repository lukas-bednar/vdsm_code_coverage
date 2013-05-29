"""
Classes in this module takes care about watching vdsm exec file and
instruments it in case of creation, modification.
"""
import os
import logging
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent
from subprocess import Popen, PIPE


logger = logging.getLogger(__name__)


class Codes(EventsCodes):
    @classmethod
    def value(cls, name):
        return cls.ALL_FLAGS[name]


class Handler(ProcessEvent):
    """
    Processes events
    """
    def __init__(self, manager):
        super(ProcessEvent, self).__init__()
        self.mng = manager

    def process_IN_CREATE(self, event):
        path = os.path.join(event.path, event.name)
        logger.info("Create: %s", os.path.join(event.path, event.name))
        count = 0
        for a, b in zip(path.split('/'), self.mng.path):
            if a == b:
                count += 1
                continue
            break
        else:
            self.mng.add_watch(path)
        if count == len(self.mng.path):
            self.mng.enable_coverage(path)

    def process_IN_DELETE(self, event):
        path = os.path.join(event.path, event.name)
        logger.info("Remove: %s", path)
        self.mng.wdd.pop(path, None)

    def process_IN_MODIFY(self, event):
#    def process_IN_CLOSE_WRITE(self, event):
        path = os.path.join(event.path, event.name)
        logger.info("Modify: %s",  path)
        if path == self.mng.target_file:
            self.mng.enable_coverage(path)


class VdsmWatcher(WatchManager):
    """
    Implements watch manager
    """
    MASK = Codes.value('IN_DELETE') | Codes.value('IN_CREATE')

    def __init__(self, path_to_vdsm, path_to_config, service_name):
        """
        C'tor
        * path_to_vdsm - path to vdsm bin file
        * path_to_config - path to code coverage config
        * service_name - name of vdsm service
        """
        super(VdsmWatcher, self).__init__()
        self.config = path_to_config
        self.service_name = service_name
        self.notifier = Notifier(self, Handler(self))
        self.path = path_to_vdsm.split(os.sep)
        self.wdd = {}

    @property
    def target_file(self):
        """
        vdsm bin file
        """
        return '/' + os.path.join(*self.path)

    def get_mask(self, path):
        """
        returns mask for specific file
        """
        if os.path.isfile(path):
            return self.MASK | Codes.value('IN_MODIFY')
#            return self.MASK | Codes.value('IN_CLOSE_WRITE')
        return self.MASK

    def add_watch(self, path):
        """
        Overrides add_watch method to work with path only
        """
        mask = self.get_mask(path)
        logger.info("Adding watch for %s, mask %s", path, mask)
        wdd = super(VdsmWatcher, self).add_watch(path, mask)
        for dir_, wd in wdd.items():
            if wd >= 0:
                self.wdd[dir_] = wd

    def add(self):
        """
        Adds watchers to all available nodes on path
        """
        path = '/'
        for part in self.path:
            path = os.path.join(path, part)
            if not os.path.exists(path):
                break
            self.add_watch(path)

    def rm(self):
        """
        Removes watchers on all available nodes on path
        """
        for path in self.wdd.keys():
            self.rm_watch(path)

    def rm_watch(self, path):
        """
        Overrides rm_watch method to work with path only
        """
        logger.info("Removing watch for %s", path)
        super(VdsmWatcher, self).rm_watch(self.wdd[path])

    def run(self):
        """
        Live cycle of watch manager
        """
        self.add()
        try:
            self.enable_coverage(self.target_file)
            while True:
                self.notifier.process_events()
                if self.notifier.check_events():
                    self.notifier.read_events()
        finally:
            self.rm()
            self.notifier.stop()
            self.disable_coverage(self.target_file)

    def exec_cmd(self, cmd):
        """
        Executes local command, and return RC
        """
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode
        logger.info("Excecuted %s", cmd)
        logger.info("stdout %s", out)
        logger.info("stderr %s", err)
        logger.info("rc %s", rc)
        return rc

    def restart_service(self):
        """
        Restart service in order to take effect of instrumentation
        """
        logger.info("vdsm was restarted")
        cmd = ['service', self.service_name, 'restart']
        self.exec_cmd(cmd)

    def enable_coverage(self, path):
        """
        Tries to instrument vdsm bin file
        """
        if not os.path.exists(path):
            return
        logger.info("Instrument path: %s", path)
        cmd = ['grep', 'vdsmcodecoverage', path]
        rc = self.exec_cmd(cmd)
        if not rc:
            cmd = ['grep', self.config, path]
            rc = self.exec_cmd(cmd)
            if rc:
                cmd = ['sed', '-i',
                       's|instrument([^)]*)|instrument("%s")|g' % self.config,
                       path]
                rc = self.exec_cmd(cmd)
            else:
                return
        else:
            cmd = 'from vdsmcodecoverage.hook import instrument;'\
                  'instrument("%s")' % self.config
            cmd = ['sed', '-i', '2 i \%s' % cmd, path]
            rc = self.exec_cmd(cmd)
        if rc:
            logger.error("failed to instrument vdsm")
        else:
            self.restart_service()

    def disable_coverage(self, path):
        """
        Tries to un-instrument vdsm bin file
        """
        if not os.path.exists(path):
            return

        cmd = ['sed', '-i', '/vdsmcodecoverage/ d', path]
        self.exec_cmd(cmd)

        self.restart_service()
