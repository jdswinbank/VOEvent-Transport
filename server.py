# VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.internet import task

# Transport protocol definitions
from tcptransport import VOEventReceiverFactory

# Local configuration
from config import LISTEN_ON

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = serverFromString(reactor, LISTEN_ON)
    factory = VOEventReceiverFactory()
    endpoint.listen(factory)
    l = task.LoopingCall(factory.event_index.print_status)
    l.start(5.0)
    reactor.run()
