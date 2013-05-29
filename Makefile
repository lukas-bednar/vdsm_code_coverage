PYTHON_ARGPARSER=$(shell python -c 'import sys;print "python-argparse" if sys.version_info < (2, 7) else ""')
RELEASE?=1

all: run

rpm:
	python setup.py bdist_rpm \
		--requires "$(PYTHON_ARGPARSER) \
								chkconfig \
								initscripts \
								logrotate \
								python-configobj \
								python-coverage >= 3.5.3 \
								python-inotify" \
		--post-install scripts/post_install \
		--pre-uninstall scripts/pre_uninstall
		--release=$(RELEASE)

run:
	python -m vdsmcodecoverage.run -c configs/vdsmcodecoverage.conf

clean:
	rm -rf MANIFEST build dist
