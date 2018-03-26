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
    def connectionMade(self):
        if self.client is not None:
            if self.text != "":
                #print("Sending:"+self.text)
                self.transport.write(self.text.encode())
            else:
                print('No information to write')

    
    #def connectionLost(self, reason):
    #    with open('log','a') as f:  
    #        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', Client connection lost: '+self.addr+'\n')
