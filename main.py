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
    round = 0
    
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
        
        with open('log', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', Total number:'+str(len(self.gateways))+'\n')
            for gw in self.gateways:
                f.write(gw.address+','+str(gw.latency)+':'+ gw.ts.strftime("%Y-%m-%d %H:%M:%S")+':'+ str(gw.status)+'\n')
            f.close()
    
    def pingGateway(self, gateway):        
        cmd='''curl -x '''+gateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        lat, status = stdout.decode("utf-8").split(',')
        if(int(status) == 0):            
            with open('log','a') as f:                
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', removing:'+gateway.address+'\n')
            self.removeGateway(gateway)
        elif(int(status)!=200):
            gateway.ts = datetime.datetime.now()
            gateway.latency = 200
            self.setCategory(gateway)
        else:
            gateway.ts = datetime.datetime.now()
            gateway.latency = float(lat)      
            self.setCategory(gateway)
    
    def pingTest(self, address):
        response = subprocess.call(['ping', '-q', '-c', '1', '-w','5',address], stdout=subprocess.PIPE)
        if response == 0:
            return True
        else:
            return False
    
    
    def setCategory(self, gw):        
        if gw.latency < 3:
            gw.status= True
        else:
            gw.status = False
        
        
    def selectBest(self):
        selected = self.defaultGateway
        for gw in self.gateways:
            if gw.latency < selected.latency:
                selected = gw                
        self.defaultGateway = selected
    
    def senseGateways(self):        
        threading.Timer(300.0, self.senseGateways).start()
        for gw in self.gateways:
            self.pingGateway(gw)
        self.selectBest()
        self.printGatewayInformation()
        
    def connect(self):
        threading.Timer(60.0, self.connect).start()
        cmd='''curl -x '''+self.defaultGateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        ttfb, lat, status = stdout.decode("utf-8").split(',')
        with open('download_best','a') as f:
            f.write("{0},{1},{2},{3},{4}\n".format(datetime.datetime.now(),self.round,
                                                   self.defaultGateway.address,float(lat),int(status)))
        self.round += 1
                      
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


client4= Client('10.139.40.77', [], [node1,node2,node4, node8, node9, node10, node6,node7, node5, node3], node7)
for gw in client4.gateways:
    if client4.pingTest(gw.address) is False:
        client4.removeGateway(gw)
client4.senseGateways()
client4.connect()