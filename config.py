# VOEvent system configuration.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# This is quick and dirty!
LISTEN_ON   = "tcp:8099"                     # Receiver listents for connections
CONNECT_TO  = "tcp:host=localhost:port=8099" # Sender connects here
LOCAL_IVO   = "ivo://lofar/transients"       # Our local IVO
N_OF_EVENTS = 5                              # Number of events to send
PERIOD      = 5                              # Distributed over PERIOD seconds
MAX_CONNECT = 1                              # Parallel connections
