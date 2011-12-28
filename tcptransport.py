# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ServerEndpoint

# Constructors for transport protocol messages
from messages import Ack

# Local configuration
from config import VOEVENT_ROLES
from eventindex import EventIndex

class VOEventReceiver(Int32StringReceiver):
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
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            outgoing = Ack(incoming.attrib['ivorn'])
            self.factory.event_index.receive_event(incoming.find("Who/Date").text)
        else:
            log.err("Incomprehensible data received")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

        # After receiving an event, we shut down the connection.
        self.transport.loseConnection()

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver
    def __init__(self):
        self.event_index = EventIndex()
