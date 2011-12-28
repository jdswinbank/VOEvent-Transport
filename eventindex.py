import datetime

class EventIndex(object):
    def __init__(self):
        self.latencies = []

    def receive_event(self, timestring):
        timestamp = datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
        if not hasattr(self, "earliest") or timestamp < self.earliest:
            self.earliest = timestamp
        received_time = datetime.datetime.now()
        self.latencies.append((received_time - timestamp).total_seconds())

    def print_status(self):
        if self.latencies:
            print "Received %d events; Latency %f/%f/%fs (min/max/avg)" % (
                len(self.latencies),
                min(self.latencies),
                max(self.latencies),
                float(sum(self.latencies))/len(self.latencies)
            )
