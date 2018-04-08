import random
import datetime
from subprocess import check_output, PIPE, Popen
import subprocess
import shlex
import threading
import os

import sys
from twisted.python import log
from twisted.internet import reactor, protocol
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol

import Gateway as gt
import Client as cl
import MessageServerProtocol as server
import MessageClientProtocol as client
import PingTool as pt
import NeighbourManager as neighbour

class ClientManager():    
    client = None
    ping = pt.PingTool()
    neighbourManager = None
    
    gateways = []
    updatedGateways = []
    round = 0
    clientCount = 0
    proxyCount = 0
    receivedCount = 0
    rttLimit = 5
    

    def __init__(self, client, neighbours, gateways):
        self.client = client
        self.gateways = gateways
        self.ping = pt.PingTool()
        self.neighbourManager = neighbour.NeighbourManager(self, neighbours)
    
    def addGateway(self, gateway):
        self.gateways.append(gateway)
    
    def removeGateway(self, gateway):
        for gw in self.gateways:
            if gw.address == gateway.address:
                self.gateways.remove(gw)

    def addReceivedCount(self):
        self.receivedCount += 1
    def addClientCount(self):
        self.clientCount += 1
    def addProxyCount(self):
        self.proxyCount +=1
    
    def updateGateways(self, gateways):
        for gw in gateways:
            if self.checkGatewayExists(gw):
                for clientGw in self.gateways:
                    if gw.address == clientGw.address:
                        if gw.ts > clientGw.ts:
                            clientGw.changeInformation(gw.latency, gw.ts)
                            #print("Updated new information:", clientGw.address,":", clientGw.ts)
                        break
            else:
                #Add new gateway but check first
                if self.ping.pingTest(gw.address)>0:
                    print('Adding new gateway:', gw.address)
                    self.addGateway(gw)
    
    def checkGatewayExists(self, gateway):
        for gw in self.gateways:
            if gw.address == gateway.address:
                return True
        return False

                    
    def selectBestGateway(self):
        best = self.client.defaultGateway
        for gw in self.gateways:
            if  best.latency > gw.latency:
                best = gw        
        self.client.defaultGateway = best
            
    
    #SELECT BEST GW FROM THE GIVEN GWS BY PINGING
    def selectBest(self, gws):
        if len(gws) == 1:
            self.client.defaultGateway = gws[0]
            self.addProxyCount()
            return True
        
        for gw in gws:
            status = self.ping.pingGateway(gw) 
            if status == 0:
                self.removeGateway(gw)
                return False
            elif status == 1:
                return False
            
        best = self.client.defaultGateway
        for gw in gws:
            if best.latency > gw.latency:
                best = gw
        self.addProxyCount()
        self.addProxyCount()
        self.client.defaultGateway = best
        
        #add latest information of probed gws into separate list
        self.updatedGateways.extend(gws)
        return True
    
    #SAMPLE 2 RANDOM GATEWAYS
    def select2Random(self):
        status = True
        if len(self.gateways)>2:               
            return random.sample(set(self.gateways), 2)
        else:
            return self.gateways


    def sendInformation(self, status):        
        info = ""
        if status is True:
        #Sending all gateway information
            for gw in self.gateways:
                if info != "":
                    info += ","
                info += gw.address+'#'+str(gw.latency)+'#'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")
        else:            
        #sending updated information, not all information        
            for gw in self.updatedGateways:
                if info != "":
                    info += ","
                info += gw.address+'#'+str(gw.latency)+'#'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")        
        return info

    def senseGateways(self):
        self.round +=1
        threading.Timer(self.client.senseLatency, self.senseGateways).start()
        status = False
        while(status is not True):
            status =self.selectBest(self.select2Random())
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.client.printInformationConsole()
        self.neighbourManager.printCloseNeighbours()        
        self.neighbourManager.sendNeighbour()
