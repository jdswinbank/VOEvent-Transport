# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ServerFactory

# Constructors for transport protocol messages
from .messages import Ack

# Constants
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

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
            outgoing = Ack(self.factory.local_ivo, incoming.attrib['ivorn'])
        else:
            log.err("Incomprehensible data received")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

        # After receiving an event, we shut down the connection.
        self.transport.loseConnection()

        # Call the local handler
        self.voEventHandler(incoming)

    def voEventHandler(self, event):
        """
        End-users should define voEventHandler which is called when an event
        is received.
        """
        raise NotImplementedError("Subclass VOEventReceiver to define handlers")

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo):
        self.local_ivo = local_ivo

class VOEventSender(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.
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
