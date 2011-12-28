# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011.

import sys
from numpy import random

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition

from twisted.python import log
from twisted.internet import reactor
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint

# Constructors for transport protocol messages
from messages import Ack
from voevent import VOEventMessage

# Local configuration
from config import VOEVENT_ROLES
N_OF_EVENTS = 5000
PERIOD = 100

class VOEventSender(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.

    When a VOEvent is received, we broadcast it onto a ZeroMQ PUB socket.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        log.msg("Got response")
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') in "ack":
            log.msg("Acknowledgement received")
        else:
            log.err("Incomprehensible data received")

        # After receiving an event, we shut down the connection.
        self.transport.loseConnection()

class VOEventSenderFactory(Factory):
    protocol = VOEventSender

def send_message(endpoint):
    d = endpoint.connect(VOEventSenderFactory())
    d.addCallback(lambda p: p.sendString(VOEventMessage().to_string()))

def schedule_messages(endpoint):
    event_times = random.uniform(0, PERIOD, N_OF_EVENTS)

    for event_time in event_times:
        reactor.callLater(event_time, send_message, endpoint)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = TCP4ClientEndpoint(reactor, "localhost", 8099)
#    reactor.callLater(1, send_message, endpoint)
#    reactor.callLater(2, send_message, endpoint)
#    for i in range(2000):
#        send_message(endpoint)
    schedule_messages(endpoint)
    reactor.run()
