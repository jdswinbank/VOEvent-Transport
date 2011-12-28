# VOEvent -> ZeroMQ configuration.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# This is quick and dirty!
LOCAL_IVO = "ivo://lofar/transients"
LISTEN_ON = "tcp:8099"
ALIVE_ROLES = ("iamalive")
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')
