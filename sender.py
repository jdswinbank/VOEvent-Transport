# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.endpoints import clientFromString
from twisted.internet import task

# VOEvent transport protocol
from tcp.transport import VOEventSenderFactory

# Constructors for messages
from voevent.voevent import VOEventMessage

# Local configuration
from config import LOCAL_IVO
from config import CONNECT_TO
from config import N_OF_EVENTS
from config import PERIOD
from config import MAX_CONNECT

def send_message(endpoint, dispatcher):
    outgoing_message = VOEventMessage(LOCAL_IVO)
    if dispatcher.ctr == N_OF_EVENTS:
        dispatcher.loop.stop()
    else:
        dispatcher.ctr += 1

    def do_send():
        # Set up a factory connected to the relevant endpoint
        d = endpoint.connect(VOEventSenderFactory())

        # And when the connection is ready, use it to send a message
        d.addCallback(lambda p: p.sendString(outgoing_message.to_string()))

        # The semaphore releases when the returned Deferred fires
        return d

    dispatcher.run(do_send)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = clientFromString(reactor, CONNECT_TO)
    dispatcher = DeferredSemaphore(MAX_CONNECT)
    dispatcher.loop = task.LoopingCall(send_message, endpoint, dispatcher)
    dispatcher.ctr = 1
    dispatcher.loop.start(float(PERIOD)/N_OF_EVENTS)

    reactor.run()
