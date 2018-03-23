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

class ClientManager():    
    client = None
    neighbours = []
    closeNeighbours = []
    gateways = []
    updatedGateways = []
    round = 0
    
    def __init__(self, client, neighbours, gateways):
        self.client = client
        self.neighbours = neighbours
        self.gateways = gateways
    
    def addNeighbour(self, neighbour):
        self.neighbours.append(neighbour)
    
    def removeNeighbour(self, neighbour):
        self.neighbours.remove(neighbour)
    
    def addGateway(self, gateway):
        self.gateways.append(gateway)
    
    def removeGateway(self, gateway):
        if(gateway in self.gateways):
            self.gateways.remove(gateway)

    def updateGateways(self, gateways):
        for gw in gateways:
            if self.checkGatewayExists(gw):
                for clientGw in self.gateways:
                    if gw.address == clientGw.address:
                        if gw.ts > clientGw.ts:
                            clientGw.changeInformation(gw.latency, gw.ts)
                            print("Updated new information:", clientGw.address,":", clientGw.ts)
                        break
            else:
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
            return True
        
        for gw in gws:
            if self.pingGateway(gw) is False:
                return False
        
        best = self.client.defaultGateway
        for gw in gws:
            if best.latency > gw.latency:
                best = gw
        
        self.client.defaultGateway = best
        
        #add latest information of probed gws into separate list
        #self.updatedGateways = gws
        self.updatedGateways.extend(gws)
        return True
    
    #SAMPLE 2 RANDOM GATEWAYS
    def select2Random(self):
        status = True
        if len(self.gateways)>2:               
            return random.sample(set(self.gateways), 2)
        else:
            return self.gateways
        
        
    def pingTest(self, address):
        cmd='ping -w 5 -c 3 -q '+address
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        stdout = str(stdout)
        if '/' not in stdout:
            return 0
        else:
            return float(stdout.split('/')[-3])

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
    
    # Send info rmation to neighbour 
    def sendNeighbour(self):
        print("Sending information called")
        text = self.sendInformation(False)
        self.updatedGateways = []
        for neighbour in self.closeNeighbours:
            f = protocol.ClientFactory()
            f.protocol = client.MessageClientProtocol
            f.protocol.client = self
            f.protocol.mode='client'
            f.protocol.text = text
            f.protocol.addr = neighbour.address
            reactor.connectTCP(neighbour.address, 5555, f)
        self.round +=1
        
    def senseGateways(self):
        threading.Timer(self.client.senseLatency, self.senseGateways).start()
        status = False
        while(status is not True):
            status =self.selectBest(self.select2Random())
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.client.printInformationConsole()
        
        self.sendNeighbour()
        

    def senseNeighbours(self):
        for nb in self.neighbours:            
            rtt = self.pingTest(nb.address)
            print(nb.address,":", rtt)            
            if rtt == 0:
                self.removeNeighbour(nb)
            elif rtt < 1:
                self.closeNeighbours.append(nb)
            else:
                if nb in self.closeNeighbours:
                    self.closeNeighbours.remove(nb)        
        self.printCloseNeighbours()
    
    def printCloseNeighbours(self):
        print("Close neighbours")
        if len(self.closeNeighbours) == 0:
            print('No close neighbours')
            return
        for nb in self.closeNeighbours:
            print(nb.address)

    #MONITORING GW PERFORMANCE BY SENDING PROBING PACKET        
    def pingGateway(self, gateway):
        status = True
        cmd='''curl -x '''+gateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        lat, status = stdout.decode("utf-8").split(',')
        if(int(status) == 0):            
            with open('log','a') as f:                
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', removing:'+gateway.address+'\n')
            self.removeGateway(gateway)
            status = False
        elif(int(status)!=200):
            gateway.ts = datetime.datetime.now()
            gateway.latency = 200
            status = False
        else:
            gateway.ts = datetime.datetime.now()
            gateway.latency = float(lat)        
        return status
    