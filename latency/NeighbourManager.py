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

class NeighbourManager():
    client = None
    
    neighbours = []
    closeNeighbours = None
    
    def __init__(self, client):
        self.client = client

    def senseNeighbours(self):
        for nb in self.neighbours:            
            rtt = self.pingTest(nb.address)
            print(nb.address,":", rtt)            
            if rtt == 0:
                self.removeNeighbour(nb)
            elif rtt < self.rttLimit:
                self.closeNeighbours.append(nb)
            else:
                if nb in self.closeNeighbours:
                    self.closeNeighbours.remove(nb)        
        self.printCloseNeighbours()
    
    def sendNeighbour(self):
        text = self.sendInformation(False)
        print("Sending information called")
        self.updatedGateways = []
        for neighbour in self.closeNeighbours:
            f = protocol.ClientFactory()
            f.protocol = client.MessageClientProtocol
            f.protocol.client = self
            f.protocol.mode='client'
            f.protocol.text = text
            f.protocol.addr = neighbour.address
            reactor.connectTCP(neighbour.address, 5555, f)
            self.addClientCount()
    
    def printCloseNeighbours(self):
        print("Close neighbours")
        if len(self.closeNeighbours) == 0:
            print('No close neighbours')
            return
        for nb in self.closeNeighbours:
            print(nb.address)
