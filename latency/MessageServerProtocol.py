import datetime
from subprocess import check_output, PIPE, Popen
import subprocess
import shlex
import threading
import os

import sys
from twisted.python import log
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ServerFactory, Protocol
import Gateway as gw

#SERVER SECTION
class MessageServerProtocol(Protocol):
    client = None
    
    def connectionMade(self):
        print('Server started running at: '+ self.client.address+'\n')

    # When receiving data from the client, it should update neighbour information
    def dataReceived(self,data):
        print("DATA:", data)
        connected = self.transport.getPeer().host
        
        if self.client is not None:
            print('Connection received:'+connected)
            #If information received from the unlisted new close neighbour 
            #then add it to the close neighbouring list
            if self.client.cManager.isNeighbourExists(connected) is False:
                self.client.cManager.addCloseNeigbour(connected)
            
            self.client.cManager.addReceivedCount()
            nlist = data.decode('utf-8').split(',')
            gateways = []
            for gwInfo in nlist:
                self.client.cManager.addReceivedCount()
                address, latency, ts = gwInfo.split('#')
                gwTemp =gw.Gateway(str(address), float(latency), datetime.datetime.strptime(ts,'%Y-%m-%d %H:%M:%S'), False)
                gateways.append(gwTemp)
                
            self.client.cManager.updateGateways(gateways)
            status = False
            self.client.printInformationConsole()
            
            


    def connectionLost(self, reason):
        with open('log','a') as f:  
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', Server connection lost\n')
        reactor.callFromThread(reactor.stop)
        if reactor.running:
                reactor.stop()
        os._exit(0)
