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

The sender was set to produce 2,000,000 events in 12 hours (ie, 46.3 events
every second).

Allowing only one simultaneous connection, the measured latency rapidly
increases, and there is a large queue of events backlogged on the sender::

  2012-01-05 15:45:02+0000 [-] Received 0 events
  2012-01-05 15:45:07+0000 [-] Received 5 events; Latency 0.744345/2.661718/1.702299s (min/max/avg)
  2012-01-05 15:45:12+0000 [-] Received 15 events; Latency 0.744345/7.461685/4.101424s (min/max/avg)
  2012-01-05 15:45:17+0000 [-] Received 25 events; Latency 0.744345/12.261735/6.501398s (min/max/avg)
  2012-01-05 15:45:22+0000 [-] Received 35 events; Latency 0.744345/17.061906/8.901790s (min/max/avg)
  2012-01-05 15:45:27+0000 [-] Received 45 events; Latency 0.744345/21.860622/11.301699s (min/max/avg)
  2012-01-05 15:45:32+0000 [-] Received 55 events; Latency 0.744345/26.657682/13.701169s (min/max/avg)

Over 30 seconds, 55 events have been received, but nearly 1400 (46.3 * 30)
have been generated; note that the maximum and average latencies are
increasing rapidly.

Allowing for 30 simultaneous connections (ie, setting ``MAX_CONNECT = 30`` in
``config.py``) mitigates the problem::

  2012-01-05 15:50:04+0000 [-] Received 0 events
  2012-01-05 15:50:09+0000 [-] Received 114 events; Latency 0.735258/0.742203/0.736949s (min/max/avg)
  2012-01-05 15:50:14+0000 [-] Received 345 events; Latency 0.735258/0.742203/0.736839s (min/max/avg)
  2012-01-05 15:50:19+0000 [-] Received 577 events; Latency 0.735099/0.742203/0.736771s (min/max/avg)
  2012-01-05 15:50:24+0000 [-] Received 808 events; Latency 0.735099/0.742203/0.736774s (min/max/avg)
  2012-01-05 15:50:29+0000 [-] Received 1040 events; Latency 0.735099/0.742203/0.736748s (min/max/avg)
  2012-01-05 15:50:34+0000 [-] Received 1271 events; Latency 0.735099/0.743539/0.736755s (min/max/avg)

Note that not all of the generated events have been received within the 30
seconds, but that the measured latency is effectively constant. Transmission
at this rate should be sustainable.
