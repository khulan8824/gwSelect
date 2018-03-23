import datetime
import os
import sys
import ClientManager as cm

# Client node information    
class Client():
    address = ""
    defaultGateway = None
    
    cManager = None
    
    def __init__(self, address, neighbours = [], gateways = [], defaultGateway = None):
        self.address = address
        self.defaultGateway = defaultGateway
        self.cManager = cm.ClientManager(self, neighbours, gateways)
        
    def getDefaultGateway(self):
        return self.defaultGateway
    
    def setDefaultGateway(self, gw):
        self.defaultGateway = gw
    
    def addNeighbour(self, neighbour):
        self.cManager.addNeighbour(neighbour)
    
    def removeNeighbour(self, neighbour):
        self.cManager.removeNeighbour(neighbour)

    def removeGateway(self, gateway):
        self.cManager.removeGateway(gateway)
  
    
    def printInformation(self):
        with open('log','a') as f:  
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', '+str(self.round)+',Address:'+ self.address+'\n')
            for gw in self.cManager.gateways:
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', '+gw.address+':'+ str(gw.latency)+':'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")+'\n')

            if self.defaultGateway is not None:
                f.write('Default gateway: '+self.defaultGateway.address+'\n')

    def printInformationConsole(self):
        print('Address:', self.address)
        for gw in self.cManager.gateways:
            print(gw.address, ':', str(gw.latency),':',gw.ts)
            
        if self.defaultGateway is not None:
            print('Default gateway:', self.defaultGateway.address)
        


    