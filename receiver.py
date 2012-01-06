h VOEvent receiver.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# Python standard library
import sys
import datetime

# Twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.internet import task

# Transport protocol definitions
from tcp.transport import VOEventReceiver
from tcp.transport import VOEventReceiverFactory

# Local configuration
from config import LISTEN_ON
from config import LOCAL_IVO

class EventIndex(object):
    """
    Simple list of receieved VOEvents.
    """
    def __init__(self):
        self.latencies = []

    def receive_event(self, timestring):
        timestamp = datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
        received_time = datetime.datetime.utcnow()
        if not hasattr(self, "earliest") or received_time < self.earliest:
            self.earliest = received_time
        if not hasattr(self, "latest") or received_time > self.latest:
            self.latest = received_time
        self.latencies.append((received_time - timestamp).total_seconds())

    def print_status(self):
        if self.latencies:
            print "Received %d events in %fs; latency %f/%f/%fs (min/max/avg)" % (
                len(self.latencies),
                (self.latest - self.earliest).total_seconds(),
                min(self.latencies),
                max(self.latencies),
                float(sum(self.latencies))/len(self.latencies)
            )

class IndexingVOEventReceiver(VOEventReceiver):
    def voEventHandler(self, event):
        self.factory.event_index.receive_event(event.find("Who/Date").text)

class IndexingVOEventReceiverFactory(VOEventReceiverFactory):
    protocol = IndexingVOEventReceiver
    def __init__(self, local_ivo):
        VOEventReceiverFactory.__init__(self, local_ivo)
        self.event_index = EventIndex()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    endpoint = serverFromString(reactor, LISTEN_ON)
    factory = IndexingVOEventReceiverFactory(LOCAL_IVO)
    endpoint.listen(factory)
    l = task.LoopingCall(factory.event_index.print_status)
    l.start(5.0)
    reactor.run()
