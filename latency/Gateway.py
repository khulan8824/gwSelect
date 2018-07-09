import datetime
import os
import sys

class Gateway:
    address = "" # address of the gateway
    latency = 0.0 # latency TTLB
    ts = None # Last measurement information
    status = True # Gateway category information, True means best gateway, False is otherwise
    actualLatency = 0.0
    
    def __init__(self, address, latency, ts, status = True):
        self.address = address
        self.latency = latency
        self.actualLatency = latency
        self.ts = ts
        self.status = status
        
    def setStatus(self, status):
        self.status=status
    
    def getStatus(self):
        return self.status
    
    def changeInformation(self, latency, actualLatency, ts, status):
        self.latency = latency
        self.actualLatency = actualLatency
        self.ts = ts
        self.status = status
        
    def setActualLatency(self, latency):
        self.actualLatency = latency
    
    def getLatency(self):
        return self.latency
    
    def getTimestamp(self):
        return self.ts
    
    def printInformation(self):
        print(self.address,':',str(self.latency), ':', str(self.actualLatency),':', self.ts.strftime("%Y-%m-%d %H:%M:%S"),':', self.status)
    
    def printInformationFile(self, file):
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+','+
                self.address+':'+str(self.latency)+':'+ self.ts.strftime("%Y-%m-%d %H:%M:%S")+':'+
                str(self.status)+'\n')