VDSM code coverage
==================

It enables code coverage of VDSM.

Build
-----
    make

Install
-------

    yum install vdsmcodecoverage

Run
----

To enable

    chkconfig vdsmcodecoveraged on
    service vdsmcodecoveraged start

do what ever you want to do ... restart vdsm, reboot host, remove vdsm and
then install vdsm back.

To disable
     chkconfig vdsmcodecoveraged off
     service vdsmcodecoveraged stop
