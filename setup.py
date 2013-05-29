#!/usr/bin/env python

from distutils.core import setup
import vdsmcodecoverage as vcc


setup(name=vcc.__name__,
      version= vcc.__version__,
      description="VDSM code coverage",
      long_description=' '.join(vcc.__doc__.splitlines()),
      author=vcc.__authors__,
      author_email=vcc.__contact__,
      packages=['vdsmcodecoverage'],
      url='nowhere',
      data_files=[('/etc', ['configs/vdsmcodecoverage.conf']),
                  ('/etc/init.d', ['scripts/vdsmcodecoveraged']),
                  ('/etc/logrotate.d', ['configs/logrotate/vdsmcodecoverage']),
                  ('/var/lib/vdsmcodecoverage', ['configs/coveragerc']),
                  ('/usr/bin', ['scripts/vdsmcodecoverage'])],
      )
