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
from twisted.internet import defer

class Gateway():
    address = ""
    latency = 0.0
    ts = None
    status = True
    def __init__(self, address, latency, ts, status = True):
        self.address = address
        self.latency = latency
        self.ts = ts
        self.status = status
        
    def setStatus(self, status):
        self.status=status
    
    def getStatus(self):
        return self.status
    
    def changeInformation(self, latency, ts):
        self.latency = latency
        self.ts = ts
    
    def getLatency(self):
        return self.latency
    
    def getTimestamp(self):
        return self.ts

# Client node information    
class Client():
    address = ""
    neighbours = []
    gateways = []
    rank = []
    defaultGateway = None
    round = 0
    lastProbingTs = None
    similarityMatrix = {} # Save information about similarity of neighbours
    senseLatency = 60
    
    def __init__(self, address, neighbours = [], gateways = [], defaultGateway = None):
        self.address = address
        self.neighbours = neighbours
        self.gateways = gateways
        self.defaultGateway = defaultGateway
        
    def getKey(gateway):
        return gateway.latency
        
    
    def getDefaultGateway(self):
        return self.defaultGateway
    
    def setDefaultGateway(self, gw):
        self.defaultGateway = gw
    
    def addNeighbour(self, neighbour):
        self.neighbours.append(neighbour)
    
    def removeNeighbour(self, neighbour):
        self.neighbours.remove(neighbour)
    
    def addGateway(self, gateway):
        self.gateways.append(gateway)
    
    def removeGateway(self, gateway):
        if(gateway in self.gateways):
            self.gateways.remove(gateway)
    
    def updateGateway(self, gateway):
        gw = next(x for x in self.gateways if x.address == gateway.address)
    
    def printGatewayInformation(self):
        print('Total number:', len(self.gateways))
        for gw in self.gateways:
            print(gw.address,':',str(gw.latency),':', gw.ts.strftime("%Y-%m-%d %H:%M:%S"),':', str(gw.status))
            
    def pingGateway(self, gateway):
        status = True
        cmd='''curl -x '''+gateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        lat, status = stdout.decode("utf-8").split(',')
        if(int(status) == 0):            
            with open('log_output','a') as f:                
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
    
    def pingTest(self, address):
        response = subprocess.call(['ping', '-q', '-c', '1', '-w','5',address], stdout=PIPE)
        if response == 0:
            return True
        else:
            return False
      
        
    def selectBest(self, gws):
        if len(gws) == 1:
            self.defaultGateway = gws[0]
            return True
        
        for gw in gws:
            if self.pingGateway(gw) is False:
                return False
        if gws[0].latency > gws[1].latency:
            self.defaultGateway = gws[1]
        else:
            self.defaultGateway = gws[0]
        
        return True
    
    #GATEWAY SELECTION LOGIC
    def select2Random(self):
        #return random.sample(set([gw for gw in gateways if gw.status is True]), 2)
        status = True
        if len(self.gateways)>2:               
            return random.sample(set(self.gateways), 2)
        else:
            return self.gateways

    def senseGateways(self):
        threading.Timer(self.senseLatency, self.senseGateways).start()
        status = False
        while(status is not True):
            status =self.selectBest(self.select2Random())
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.printGatewayInformation()

    def connect(self):
        threading.Timer(60.0, self.connect).start()        
        
        cmd='''curl -x '''+self.defaultGateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        ttfb, lat, status = stdout.decode("utf-8").split(',')
        #print(datetime.datetime.now(),self.round, self.defaultGateway.address,float(lat),int(status))
        with open('download_random2_cluster','a') as f:
            f.write("{0},{1},{2},{3},{4}\n".format(datetime.datetime.now(),self.round,
                                                   self.defaultGateway.address,float(lat),int(status)))
        self.round += 1
        
    
    def findSimilarity(self, client):
        count = 0
        iterCount = 0
        if(len(self.gateways) > len(client.gateways)):
            iterCount = len(client.gateways)
        else:
            iterCount = len(self.gateways)
        
        client.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        i=0
        while(i<iterCount):
            if(self.gateways[i].address == client.gateways[i].address):
                count +=1
                i +=1
            else:
                break
        #print('Similarity:', count/iterCount)
        return float(count)/float(iterCount)

        
    def sendNeighbour(self):
        for neighbour in self.neighbours:
            print('Sending to:',self.round, ':', neighbour.address)
            f = protocol.ClientFactory()
            f.protocol = MessageClientProtocol
            f.protocol.client = self
            f.protocol.mode='client'
            f.protocol.addr = neighbour.address
            reactor.connectTCP(neighbour.address, 5555, f)
        self.round +=1
        reactor.callLater(self.senseLatency,self.sendNeighbour)

    def updateGateways(self, gateways):
        self.gateways = gateways
    
    def printInformation(self):
        print('Address:', self.address)
        for gw in self.gateways:
            print(gw.address, ':', str(gw.latency),':',gw.ts)
        
        print('Similarity matrix')
        for k, v in self.similarityMatrix.items():
            print(k, '>', v)
        if self.defaultGateway is not None:
            print('Default gateway:', self.defaultGateway.address)
    
    def sendInformation(self):
        info = ""
        for gw in self.gateways:
            if info != "":
                info += ","
            info += gw.address+'#'+str(gw.latency)+'#'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")
        
        return info
    
#SERVER SECTION
class MessageServerProtocol(Protocol):
    client = None
    
    def connectionMade(self):
        print('Server started running at: ', self.client.address)

    # When receiving data from the client, it should update neighbour information
    def dataReceived(self,data):
        connected = self.transport.getPeer().host
        print('Connection received from:', connected)
        if self.client is not None:
            nlist = data.decode('utf-8').split(',')
            gateways = []
            for gwInfo in nlist:
                address, latency, ts = gwInfo.split('#')
                gateways.append(Gateway(str(address), float(latency), datetime.datetime.strptime(ts,'%Y-%m-%d %H:%M:%S'), False))
            
            status = False
            #searching for neighbour to update received information
            for nb in self.client.neighbours:
                if nb.address == connected:
                    nb.updateGateways(gateways)
                    nb.printInformation()
                    status = True
                    #Updating similarity matrix information
                    self.client.similarityMatrix[nb.address] = self.client.findSimilarity(nb)
                    break

    def connectionLost(self, reason):
        print("Server connection lost")
        reactor.callFromThread(reactor.stop)

        if reactor.running:
                reactor.stop()
        os._exit(0)

    
        
#CLIENT SECTION
class MessageClientProtocol(Protocol):    
    client = None
    addr = ""
    
    def connectionMade(self):
        if self.client is not None:
            text = self.client.sendInformation()
            if text != "":
                self.transport.write(text.encode())
            else:
                print("No information to write")

    
    def connectionLost(self, reason):
        print("Connection lost:", reason)
        if self.addr != "":
                self.client.similarityMatrix[self.addr] = 0
                print(self.addr, ':', 0)


node1 = Gateway('10.139.40.85', 0.15, datetime.datetime.strptime('2018-02-15 18:59:15', '%Y-%m-%d %H:%M:%S'), False)
node2 = Gateway('10.139.40.122', 0.20, datetime.datetime.strptime('2018-02-15 18:20:15', '%Y-%m-%d %H:%M:%S'),False)
node3 = Gateway('10.138.57.2', 0.02, datetime.datetime.strptime('2018-02-15 18:45:07', '%Y-%m-%d %H:%M:%S'), False)
node4 = Gateway('10.228.0.83', 0.5, datetime.datetime.strptime('2018-02-15 18:47:21', '%Y-%m-%d %H:%M:%S'), False)
node5 = Gateway('10.138.77.2', 0.78, datetime.datetime.strptime('2018-02-15 18:26:19', '%Y-%m-%d %H:%M:%S'), False)
node6 = Gateway('10.138.85.130', 0.35, datetime.datetime.strptime('2018-02-15 19:00:01', '%Y-%m-%d %H:%M:%S'), True)
node7 = Gateway('10.139.17.4', 2.1, datetime.datetime.strptime('2018-02-15 18:26:04', '%Y-%m-%d %H:%M:%S'), False)
node8 = Gateway('10.139.37.194', 1.5, datetime.datetime.strptime('2018-02-15 18:30:14', '%Y-%m-%d %H:%M:%S'), True)
node9 = Gateway('10.138.62.2', 0.04, datetime.datetime.strptime('2018-02-15 19:47:59', '%Y-%m-%d %H:%M:%S'), False)
node10 = Gateway('10.138.25.67', 0.09, datetime.datetime.strptime('2018-02-15 17:59:07', '%Y-%m-%d %H:%M:%S'), False)

listGW = [node2, node4, node5, node8, node9, node10, node6,node7, node3]

neighbour1 = Client('10.228.207.66',[],[],None)
neighbour2 = Client('10.228.207.65',[],[],None)
neighbour3 = Client('10.139.40.87',[],[],None)
neighbour4 = Client('10.139.94.108',[],[],None)

client4= Client('10.228.207.65', [neighbour1, neighbour2, neighbour3, neighbour4], listGW, node7)

for gw in client4.gateways:
    if client4.pingTest(gw.address) is False:
        client4.removeGateway(gw)

client4.senseGateways()
#client4.connect()

if reactor.running:
    reactor.stop()

factory = protocol.ServerFactory()
factory.protocol = MessageServerProtocol
factory.protocol.client = client4
reactor.listenTCP(5555, factory)

reactor.callWhenRunning(client4.sendNeighbour)

reactor.run()
