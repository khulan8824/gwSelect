import random
import datetime
from subprocess import check_output, PIPE, Popen
import subprocess
import shlex
import threading
import os

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
    defaultGateway = None
    
    def __init__(self, address, neighbours = [], gateways = [], defaultGateway = None):
        self.address = address
        self.neighbours = neighbours
        self.gateways = gateways
        self.defaultGateway = defaultGateway
    
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
            print(gw.address,':',gw.latency,':', gw.ts,':', gw.status)
    
    def pingGateway(self, gateway):        
        cmd='''curl -x '''+gateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        lat, status = stdout.decode("utf-8").split(',')
        if(int(status) != 200):
            print('removing ',':', gateway.address)
            self.removeGateway(gateway)
        else:
            gateway.ts = datetime.datetime.now()
            gateway.latency = float(lat)      
            self.setCategory(gateway)
            print(gateway.address,':',gateway.ts,':',float(lat), ':', int(status))
    
    def pingTest(self, address):
        response = subprocess.call(['ping', '-q', '-c', '1', '-w','5',address], stdout=subprocess.DEVNULL)
        if response == 0:
            return True
        else:
            return False
    
    def updateGoodGateways(self):        
        threading.Timer(120.0, self.updateGoodGateways).start()
        goodGateways = [gw for gw in self.gateways if gw.status is True]
        print(len(goodGateways))
        for randomGw in self.select2Random(goodGateways):
            print('pinging good:',randomGw.address)
            self.pingGateway(randomGw)

    def updateBadGateways(self):
        threading.Timer(600.0, self.updateBadGateways).start()
        badGateways = [gw for gw in self.gateways if gw.status is False]
        print(len(badGateways))
        for randomGw in self.select2Random(badGateways):
            print('pinging bad:',randomGw.address)
            self.pingGateway(randomGw)
    
    def setCategory(self, gw):        
        if gw.latency < 3:
            gw.status= True
        else:
            gw.status = False
        
    
    #GATEWAY SELECTION LOGIC
    def select2Random(self, gateways):
        #return random.sample(set([gw for gw in gateways if gw.status is True]), 2)
        if len(gateways)>2:
            return random.sample(set(gateways), 2)
        else:
            return gateways
    
    def selectRandomize(self):
        selected = None
        if len(self.gateways) > 2:
            rand_choice = self.select2Random()
            if rand_choice[0].latency > rand_choice[1].latency:
                selected = rand_choice[1]
            else:
                selected = rand_choice[0]
        else:
            selected = self.gateways[0]
        return selected
    
    def selectBest(self):
        selected = None
        for gw in self.gateways:
            if selected is None:
                selected = gw
                continue
            if gw.latency < selected.latency:
                selected = gw                
        self.defaultGateway = selected
    
    def selectNext(self):
        self.defaultGateway = self.gateways[0]
        
    
    def connect(self):
        #Checking if gw is responsive, connectable
        if self.pingTest(self.defaultGateway.address) is False:
            print('Changing the unresponsive gw:', self.defaultGateway.address)
            self.removeGateway(self.defaultGateway)
            self.selectNext()
        print('Connecting to:', self.defaultGateway.address)
        
        threading.Timer(180.0, self.connect).start()
        cmd='''curl -x '''+self.defaultGateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        ttfb, lat, status = stdout.decode("utf-8").split(',')
        if(int(status) == 0):
            print('removing ',':', self.defaultGateway.address)
            self.removeGateway(self.defaultGateway)
            self.selectNext()
        else:
            self.defaultGateway.ts = datetime.datetime.now()
            self.defaultGateway.latency = float(lat)      
            self.setCategory(self.defaultGateway)
        print(self.defaultGateway.address,':',self.defaultGateway.ts,':',float(lat), ':', int(status))
        
        
                
node1 = Gateway('10.139.40.85', 0.15, '2018 Feb 15 18:59:15', False)
node2 = Gateway('10.139.40.122', 0.20, '2018 Feb 15 18:20:15',False)
node3 = Gateway('10.138.57.2', 0.02, '2018 Feb 15 18:45:07', False)
node4 = Gateway('10.228.0.83', 0.5, '2018 Feb 15 18:47:21', False)
node5 = Gateway('10.138.77.2', 0.78, '2018 Feb 15 18:26:19', False)
node6 = Gateway('10.138.85.130', 0.35, '2018 Feb 15 19:00:01', True)
node7 = Gateway('10.139.17.4', 2.1, '2018 Feb 15 18:26:04', False)
node8 = Gateway('10.139.37.194', 1.5, '2018 Feb 15 18:30:14', True)
node9 = Gateway('10.138.62.2', 0.04, '2018 Feb 15 19:47:59', False)
node10 = Gateway('10.138.25.67', 0.09, '2018 Feb 15 17:59:07', False)


client4= Client('10.139.40.77', [], [node1,node2,node4, node8, node9, node10, node6,node7, node5, node3], node9)
for gw in client4.gateways:
    if client4.pingTest(gw.address) is False:
        if gw.address == client4.defaultGateway.address:
            client4.selectNext()
        client4.removeGateway(gw)
client4.connect()
#client4.updateGoodGateways()
#client4.updateBadGateways()