import os
import signal
from contextlib import contextmanager

import pexpect

from lid_ds.core.objects.environment import ScenarioEnvironment
from lid_ds.core.objects.base import ScenarioContainerBase
from lid_ds.core.image import Image
from lid_ds.helpers import wait_until
from lid_ds.sim.dockerize import run_image
from lid_ds.utils import log


def kill_child(child):
        pid = child.pid
        tries = 0
        while child.isalive():
            tries += 1
            child.sendcontrol('c')
            if tries > 1000:
                break
        if child.isalive():
            os.kill(pid, signal.SIGINT)


class ScenarioVictim(ScenarioContainerBase):
    def __init__(self, image: Image):
        super().__init__(image)
        self.port_mapping = "all"
        self.container = None
        self.env = ScenarioEnvironment()
        self.logger = log.get_logger(self.env.victim_hostname, self.queue)

    @contextmanager
    def start_container(self, check_if_available, init=None):
        self.container = run_image(self.image.name, self.env.network, self.env.victim_hostname, self.port_mapping)
        self.logger.debug("Waiting for container to be available")
        self.container.reload()
        wait_until(check_if_available, 60, 1, container=self.container)
        self.logger.info("Container available on port(s) %s" % self.container.ports)
        if init is not None:
            init(self.container)
        yield self.container
        self.container.stop()

    @contextmanager
    def record_container(self, buffer_size=80):
        out_dir = os.environ.get('LIDDS_OUT_DIR', '.')
        sysdig = self._sysdig(out_dir, buffer_size)
        tcpdump = self._tcpdump(out_dir)
        yield sysdig, tcpdump
        kill_child(sysdig)
        tcpdump.kill()

    def _sysdig(self, out_dir, buffer_size):
        sysdig_out_path = os.path.join(out_dir, '{}.scap'.format(self.env.recording_name))
        self.logger.info('Saving to Sysdig to {}'.format(sysdig_out_path))
        return pexpect.spawn(
            'sysdig -w {} -s {} container.name={} --unbuffered'.format(sysdig_out_path, buffer_size, self.env.victim_hostname))

    def _tcpdump(self, out_dir):
        container = run_image("itsthenetwork/alpine-tcpdump",
                              volumes={os.path.abspath(out_dir): {'bind': '/capture', 'mode': 'rw'}},
                              name="tcpdump_%s" % self.env.recording_name,
                              network="container:%s" % self.container.name,
                              command="-i any -U -s0 -w /capture/%s.pcap" % self.env.recording_name)
        self.logger.info("Writing tcpdump to %s" % (os.path.join(out_dir, "%s.pcap" % self.env.recording_name)))
        return container