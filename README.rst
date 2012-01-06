====================
VOEvent TCP Protocol
====================

This is a proof-of-concept concept Twisted Python implementation of (parts of)
the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_. It is not production
ready and not intended for "serious" use.


Requirements
------------

- Python 2.6 or 2.7 (other versions untested).
- `Twisted <http://twistedmatrix.com/trac/>`_ 11.0 or greater.

Usage
-----

Sender
======

The sender connects to a remote host and sends a number of (simulated;
containing no scientific payload) VOEvent packets according to the TCP
transport protocol.

The number of packets to be sent, as well as the period over which they are
sent, may be configured by editing ``config.py``. This file may also be edited
to set the target host & port, the maximum number of simulatenous connections,
and the local IVO to use in packet generation.

Usage::

  $ python sender.py

Use ``ctrl+c`` to exit.

Receiver
========

The receiver listens for VOEvent packets and keeps basic statistics about the
latency (defined as the difference between the time at which the packet is
deserialised and the timestamp included in the packet itself). For this
measurement to be meaningful, the clocks on the sender and the receiver must
be synchronised.

The hostname and port on which to listen, as well as the local IVO, may be
configured by editing ``config.py``.

Usage::

  $ python receiver.py

Use ``ctrl+c`` to exit.

Benchmarking
------------

The `LSST <http://www.lsst.org/>`_ will produce up to 2,000,000 VOEvents per
night. It is at the end of a high-latency internet connection. Is the existing
VOEvent Transport Protocol suitable?

This code was installed on two (virtual) machines running Debian Testing. The
machines were hosted on `VirtualBox 4.1.6 <http://www.virtualbox.org/>`_ and
connected using a VirtualBox "internal network". NTP was used to synchronise
the clocks on the machines (this is not a perfect technique -- to be
investigated is proper syncing to the host clock using VirtualBox).
Artificial network latency is introduced using ``tc``::

  $ sudo tc qdisc add dev eth1 root netem delay 250ms

Note that ``tc`` adds latency to *outgoing* packets, but not to incoming
packets. Hence this command must be run on *both* machines.

2,000,000 events in a 12 hour night is equivalent to 46.3 events per second,
or 2778 events every minute. For the initial test, we allow only one
connection at any given time. In ``config.py`` we set::

  N_OF_EVENTS = 93 # Two seconds worth of data
  PERIOD      = 2
  MAX_CONNECT = 1

The result is::

  2012-01-06 13:10:55+0000 [-] Received 5 events in 2.001398s; latency 0.750891/2.666349/1.707543s (min/max/avg)
  2012-01-06 13:11:00+0000 [-] Received 15 events in 7.020242s; latency 0.750891/7.470119/4.108328s (min/max/avg)
  2012-01-06 13:11:05+0000 [-] Received 25 events in 12.038195s; latency 0.750891/12.273038/6.509082s (min/max/avg)
  2012-01-06 13:11:10+0000 [-] Received 35 events in 17.050756s; latency 0.750891/17.070541/8.909878s (min/max/avg)
  2012-01-06 13:11:15+0000 [-] Received 45 events in 22.063666s; latency 0.750891/21.868405/11.309699s (min/max/avg)
  2012-01-06 13:11:20+0000 [-] Received 55 events in 27.075773s; latency 0.750891/26.665451/13.709110s (min/max/avg)
  2012-01-06 13:11:25+0000 [-] Received 65 events in 32.090319s; latency 0.750891/31.464942/16.108537s (min/max/avg)
  2012-01-06 13:11:30+0000 [-] Received 74 events in 36.603541s; latency 0.750891/35.784622/18.268118s (min/max/avg)
  2012-01-06 13:11:35+0000 [-] Received 84 events in 41.619221s; latency 0.750891/40.585238/20.667791s (min/max/avg)
  2012-01-06 13:11:40+0000 [-] Received 93 events in 46.134361s; latency 0.750891/44.906831/22.827636s (min/max/avg)

Transmitting 2 seconds worth of events took over 46 seconds: we are a factor
of 23 too slow. However, we can overcome this by allowing more parallel
connections::

  N_OF_EVENTS = 93 # Two seconds worth of data
  PERIOD      = 2
  MAX_CONNECT = 25

Resulting in::

  2012-01-06 13:14:15+0000 [-] Received 93 events in 1.972147s; latency 0.743693/0.751070/0.744923s (min/max/avg)

This rate is sustainable for the longer term::

  N_OF_EVENTS = 2778 # One minute worth of data
  PERIOD      = 60
  MAX_CONNECT = 25

Results in::

  2012-01-06 13:14:55+0000 [-] Received 119 events in 2.543387s; latency 0.743660/0.749975/0.744784s (min/max/avg)
  2012-01-06 13:15:00+0000 [-] Received 350 events in 7.532642s; latency 0.743467/0.749975/0.744829s (min/max/avg)
  2012-01-06 13:15:05+0000 [-] Received 582 events in 12.543766s; latency 0.743467/0.749975/0.744823s (min/max/avg)
  2012-01-06 13:15:10+0000 [-] Received 813 events in 17.532468s; latency 0.743375/0.749975/0.744806s (min/max/avg)
  2012-01-06 13:15:15+0000 [-] Received 1045 events in 22.543058s; latency 0.743375/0.749975/0.744821s (min/max/avg)
  2012-01-06 13:15:20+0000 [-] Received 1276 events in 27.533140s; latency 0.743137/0.749975/0.744822s (min/max/avg)
  2012-01-06 13:15:25+0000 [-] Received 1508 events in 32.543870s; latency 0.743137/0.749975/0.744817s (min/max/avg)
  2012-01-06 13:15:30+0000 [-] Received 1739 events in 37.533085s; latency 0.743137/0.757149/0.744841s (min/max/avg)
  2012-01-06 13:15:35+0000 [-] Received 1971 events in 42.543209s; latency 0.743137/0.757149/0.744831s (min/max/avg)
  2012-01-06 13:15:40+0000 [-] Received 2202 events in 47.533150s; latency 0.743137/0.757149/0.744821s (min/max/avg)
  2012-01-06 13:15:45+0000 [-] Received 2434 events in 52.543570s; latency 0.743137/0.757149/0.744810s (min/max/avg)
  2012-01-06 13:15:50+0000 [-] Received 2665 events in 57.532145s; latency 0.743137/0.757149/0.744805s (min/max/avg)
  2012-01-06 13:15:55+0000 [-] Received 2778 events in 59.972822s; latency 0.743137/0.757149/0.744805s (min/max/avg)

Note that no backlog is building up; this could be sustained indefinitely.
Indeed, we can reach higher peak rates by allowing more connections::

  N_OF_EVENTS = 8000 # 133 events/second, or 5,760,000/12 hour night
  PERIOD      = 60
  MAX_CONNECT = 100

  2012-01-06 13:19:14+0000 [-] Received 378 events in 2.821892s; latency 0.743167/0.750918/0.745386s (min/max/avg)
  2012-01-06 13:19:19+0000 [-] Received 1044 events in 7.817489s; latency 0.743167/0.751525/0.745724s (min/max/avg)
  2012-01-06 13:19:24+0000 [-] Received 1709 events in 12.818858s; latency 0.743167/0.769118/0.745793s (min/max/avg)
  2012-01-06 13:19:29+0000 [-] Received 2375 events in 17.813449s; latency 0.743167/0.769118/0.745809s (min/max/avg)
  2012-01-06 13:19:34+0000 [-] Received 3042 events in 22.818932s; latency 0.743167/0.769118/0.745842s (min/max/avg)
  2012-01-06 13:19:39+0000 [-] Received 3709 events in 27.820821s; latency 0.743167/0.769118/0.745861s (min/max/avg)
  2012-01-06 13:19:44+0000 [-] Received 4372 events in 32.821184s; latency 0.743167/0.777354/0.745940s (min/max/avg)
  2012-01-06 13:19:49+0000 [-] Received 5038 events in 37.819161s; latency 0.743167/0.777354/0.745977s (min/max/avg)
  2012-01-06 13:19:54+0000 [-] Received 5705 events in 42.822015s; latency 0.743167/0.777354/0.746010s (min/max/avg)
  2012-01-06 13:19:59+0000 [-] Received 6371 events in 47.813787s; latency 0.743167/0.777354/0.746077s (min/max/avg)
  2012-01-06 13:20:04+0000 [-] Received 7034 events in 52.819816s; latency 0.743034/0.784909/0.746116s (min/max/avg)
  2012-01-06 13:20:09+0000 [-] Received 7701 events in 57.820593s; latency 0.743034/0.784909/0.746131s (min/max/avg)
  2012-01-06 13:20:14+0000 [-] Received 8000 events in 60.061759s; latency 0.743034/0.784909/0.746133s (min/max/avg)

Again, it is clear from the latency figures that no backlog is building up.
