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
from twisted.internet.protocol import ClientFactory, Protocol

#CLIENT SECTION
class MessageClientProtocol(Protocol):    
    client = None
    addr = ""
    status = False
    text = ""
    mode = "client"
    def connectionMade(self):
        if self.client is not None:
            if self.text != "":
                print('Sending information to:', self.transport.getPeer().host)
                self.transport.write(self.text.encode())
            else:
                print('No information to write')
        self.transport.loseConnection()
            
    def dataReceived(self,data):
        print('Data received at client side:>', data)
    
    #def connectionLost(self, reason):
    #    with open('log','a') as f:  
    #        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', Client connection lost: '+self.addr+'\n')
