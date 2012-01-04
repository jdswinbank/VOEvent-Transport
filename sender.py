# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys
from numpy import random

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString

# VOEvent transport protocol
from tcp.transport import VOEventSenderFactory

# Constructors for messages
from voevent.voevent import VOEventMessage

# Local configuration
from config import LOCAL_IVO
from config import CONNECT_TO
from config import N_OF_EVENTS
from config import PERIOD

def send_message(endpoint):
    # Set up a factory connected to the relevant endpoint
    d = endpoint.connect(VOEventSenderFactory())

    # And when the connection is ready, use it to send a message
    d.addCallback(lambda p: p.sendString(VOEventMessage(LOCAL_IVO).to_string()))

def schedule_messages(endpoint):
    event_times = random.uniform(0, PERIOD, N_OF_EVENTS)

    for event_time in event_times:
        reactor.callLater(event_time, send_message, endpoint)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    #endpoint = TCP4ClientEndpoint(reactor, "localhost", 8099)
    endpoint = clientFromString(reactor, CONNECT_TO)
#    reactor.callLater(1, send_message, endpoint)
#    reactor.callLater(2, send_message, endpoint)
#    for i in range(2000):
#        send_message(endpoint)
    schedule_messages(endpoint)
    reactor.run()
