import random
import datetime
import time
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
    actualGateways = []
    updatedGateways = []
    round = 0
    connectRound = 0
    clientCount = 0
    proxyCount = 0
    receivedCount = 0
    rttLimit = 5
    
    # Used for connection section
    connectTime = None
    connectTimeRandom = None
    defaultGateway = None
    defaultGatewayRandom = None
    

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
                            self.setCategory(gw)
                            clientGw.changeInformation(gw.latency, gw.actualLatency, gw.ts, gw.status)
                            print("Updated:", clientGw.address,":", clientGw.ts, ":",clientGw.latency,":", clientGw.status)
                        break
                if gw.address == '10.139.40.122':
                    self.printSelectedGateway()
            else:
                #Add new gateway but check first
                if self.ping.pingTest(gw.address)>0:
                    print('Adding new gateway:', gw.address)
                    self.setCategory(gw)
                    self.addGateway(gw)
    
    def checkGatewayExists(self, gateway):
        for gw in self.gateways:
            if gw.address == gateway.address:
                return True
        return False

                    
    def selectBestGateway(self):
        best = None
        for gw in [x for x in self.gateways if x.status == True]:  
            if best == None:
                best = gw
            if  best.latency > gw.latency:
                best = gw        
        return best
            
    
    #SELECT BEST GW FROM THE GIVEN GWS BY PINGING
    def selectBest(self, gws):
        if len(gws) == 1:
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
            gw.actualLatency = gw.latency # UPDATING ACTUAL LATENCY
            self.setCategory(gw)
            if best.latency > gw.latency:
                best = gw
        
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
	    cnt = 1
            for gw in self.updatedGateways:
                if info != "":
                    info += ","
		if cnt ==1:
                    info += gw.address+'#'+str(gw.latency)+'#'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")        
		else:
		    info += gw.address+'#'+str(20)+'#'+gw.ts.strftime("%Y-%m-%d %H:%M:%S")
		cnt +=1
        return info

    def senseGateways(self):
        self.round +=1
        threading.Timer(self.client.senseLatency, self.senseGateways).start()
        status = False
        while(status is not True):
            status =self.selectBest(self.select2Random())
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.neighbourManager.sendNeighbour()
        self.printSimilarity()
        

    def senseAllGateways(self):
        #self.round +=1
        threading.Timer(self.client.senseLatency, self.senseAllGateways).start()
        
        for gw in self.actualGateways:
            status = self.ping.pingGateway(gw) 
            if status == 0:
                self.removeGateway(gw)
            else:
                self.setCategory(gw)
                
        self.gateways.sort(key=lambda x: (x.latency, x.ts), reverse=False)
        self.printSelectedGateway()
        
        
    def printSelectedGateway(self):
        gw = [x for x in self.gateways if x.address == '10.139.40.122']
        with open('selected_gw','a') as f:
            f.write("{0},{1},{2}\n".format(datetime.datetime.now(), gw[0].latency, gw[0].actualLatency))
        
    def printSimilarity(self):
        
        total = 0
        count1 = 0
        recent = [x for x in self.gateways if (datetime.datetime.now() - x.ts).seconds <= 180]
        print("=======================SIMILARITY MEASUREMENT================")
        print([x.address for x in recent])
        for gw in recent:
            if gw.latency > gw.actualLatency:
                total += float(gw.actualLatency/gw.latency)
            else:
                total += float(gw.latency/gw.actualLatency)
            print(gw.address,':',gw.latency,":",gw.actualLatency,":", gw.ts)
        print('Total recent measurement sim:',':',float(total/len(recent)))
        with open('similar_measure','a') as f:
                f.write("{0},{1}\n".format(datetime.datetime.now(),total/len(recent)))

    def setCategory(self, gw):
        if gw.latency < 0.1:
            gw.status = True
        else:
            gw.status = False
        #print(gw.address,";", gw.status,";",gw.latency)
            
    def selectRandomBest(self):
        for gw in self.gateways:
            self.setCategory(gw)
        good_gws = [x for x in self.gateways if x.status == True]
        print("Best random:", [x.address for x in good_gws])
        choice = random.choice(list(good_gws))
        print("Best random choice:", choice.address)
        return choice

    def connect(self):
        print("Connecting collab random")
        threading.Timer(60.0, self.connect).start()
        if len([x for x in self.gateways if x.status == True]) == 0:
            return
        
        while True:
                
            if self.defaultGatewayRandom == None:
                self.defaultGatewayRandom = self.selectRandomBest()
                self.connectTimeRandom = datetime.datetime.now()

            if (datetime.datetime.now() - self.connectTimeRandom).seconds >300:
                self.connectTimeRandom = datetime.datetime.now()
                self.defaultGatewayRandom = self.selectRandomBest()
        
            if self.defaultGatewayRandom == None:
                return

            cmd='''curl -x '''+self.defaultGatewayRandom.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code},%{size_download} http://ovh.net/files/10Mb.dat -o /dev/null -s'''
            command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
            stdout, stderr = command.communicate()
            ttfb, lat, status,size = stdout.decode("utf-8").split(',')
            if status !=0:                
                with open('download_collab_random','a') as f:
                    f.write("{0},{1},{2},{3},{4},{5}\n".format(datetime.datetime.now(), self.defaultGatewayRandom.address,float(ttfb),float(lat),int(status),int(size)))
                    break
            
        
    def connectBest(self):
        print("Connecting collab best")
        threading.Timer(60.0, self.connectBest).start()
        
        if self.defaultGateway == None:
            self.defaultGateway = self.selectBestGateway()
            self.connectTime = datetime.datetime.now()
        elif (datetime.datetime.now() - self.connectTime).seconds >=300:
            self.connectTime = datetime.datetime.now()
            self.defaultGateway = self.selectBestGateway()
            
        if self.defaultGateway == None:
            return
        

        cmd='''curl -x '''+self.defaultGateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code},%{size_download} http://ovh.net/files/10Mb.dat -o /dev/null -s'''
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        ttfb, lat, status,size = stdout.decode("utf-8").split(',')
        with open('download_collab_best','a') as f:
            f.write("{0},{1},{2},{3},{4},{5}\n".format(datetime.datetime.now(), self.defaultGateway.address,float(ttfb),float(lat),int(status),int(size)))
            
    
    def connectBruteForce(self):
        print("Connecting Brute Force")
        threading.Timer(300.0, self.connectBruteForce).start()
        gwAddress = [x.address for x in self.gateways]
        bestGW = None
        for gw in gwAddress:
            tempGW = gt.Gateway(gw, 0.5, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
            status = self.ping.pingGateway(tempGW) 
            if status != 0:
                self.setCategory(tempGW)
            if bestGW == None:
                bestGW = tempGW
            elif bestGW.latency > tempGW.latency:
                bestGW = tempGW

        if bestGW == None:
            return
        count = 0        
        print("Best gw:", bestGW.address)
        while count <5:
            cmd='''curl -x '''+bestGW.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code},%{size_download} http://ovh.net/files/1Gio.dat -o /dev/null -s'''
            command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
            stdout, stderr = command.communicate()
            ttfb, lat, status,size = stdout.decode("utf-8").split(',')
            with open('download_brute_force','a') as f:
                f.write("{0},{1},{2},{3},{4},{5}\n".format(datetime.datetime.now(),
                                                       bestGW.address,float(ttfb),float(lat),int(status),int(size)))
            time.sleep(60)
            count +=1
            

    def connectPowerTwo(self):
        print("Connecting Power Two")
        threading.Timer(300.0, self.connectPowerTwo).start()
        gwAddress = []
        gateways = None
        bestGW = None
        while True:
            gwAddress = random.sample(set([x.address for x in self.gateways]), 2)
            count = 0
            temp = []
            for gw in gwAddress:
                tempGW = gt.Gateway(gw, 0.5, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
                status = self.ping.pingGateway(tempGW) 
                if status != 0:
                    temp.append(tempGW)
                else:
                    temp = []
                    continue #Skip the loop
                    
            if len(temp) == 2: #If they have 2 candidates
                gateways = temp
                break

        #=============AFTER RESULT OF 2 FEASIBLE MEASUREMENT
            
        for gw in gateways:
            if bestGW == None:
                bestGW = gw
            elif bestGW.latency > gw.latency:
                bestGW = gw

        if bestGW == None:
            return
        count = 0        
        while count <5:
            cmd='''curl -x '''+bestGW.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_starttransfer},%{time_total},%{http_code},%{size_download} http://ovh.net/files/10Mb.dat -o /dev/null -s'''
            command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
            stdout, stderr = command.communicate()
            ttfb, lat, status,size = stdout.decode("utf-8").split(',')
            with open('download_power_two','a') as f:
                f.write("{0},{1},{2},{3},{4},{5}\n".format(datetime.datetime.now(),
                                                       bestGW.address,float(ttfb),float(lat),int(status),int(size)))
            time.sleep(60)
            count +=1


                
        
