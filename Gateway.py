class Gateway():
    address = ""
    latency = 0.0
    ts = None
    def __init__(self, address, latency, ts):
        self.address = address
        self.latency = latency
        self.ts = ts