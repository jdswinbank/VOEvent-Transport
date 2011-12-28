# VOEvent transport protocol messages.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
from datetime import datetime

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Local configuration
from config import LOCAL_IVO

# For neatness only; requires Python 2.7
#ElementTree.register_namespace("trn", "http://www.telescope-networks.org/xml/Transport/v1.1")

class VOEventMessage(object):
    def __init__(self):
        self.root_element = ElementTree.Element("{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent",
            attrib={
                "ivorn": LOCAL_IVO + "#1",
                "role": "test",
                "version": "2.0",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns:voe": "http://www.ivoa.net/xml/VOEvent/v2.0",
                "xsi:schemaLocation": "http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
            }
        )
        who = ElementTree.SubElement(self.root_element, "Who")
        author_ivorn = ElementTree.SubElement(who, "AuthorIVORN")
        author_ivorn.text = LOCAL_IVO
        date = ElementTree.SubElement(who, "Date")
        date.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")

    def to_string(self):
        """
        Serialise the message to an XML string.
        """
        return ElementTree.tostring(self.root_element)

