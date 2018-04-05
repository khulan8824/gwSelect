import datetime
from subprocess import check_output, PIPE, Popen
import subprocess
import shlex
import os

import sys

import Gateway as gt

class PingTool():
    
    def pingGateway(self, gateway):
        status = True
        cmd='''curl -x '''+gateway.address+''':3128 -U david.pinilla:"|Jn 5DJ\\7inbNniK|m@^ja&>C" -m 180 -w %{time_total},%{http_code} http://ovh.net/files/1Mb.dat -o /dev/null -s'''
        print('Sensing:',gateway.address)
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        lat, status = stdout.decode("utf-8").split(',')
        if(int(status) == 0):            
            with open('log','a') as f:                
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+', removing:'+gateway.address+'\n')
            status = False
            return 0
        
        elif(int(status)!=200):
            gateway.ts = datetime.datetime.now()
            gateway.latency = 200
            status = False            
            return 1
        
        else:
            gateway.ts = datetime.datetime.now()
            gateway.latency = float(lat)                    
            return 2
        
    def pingTest(self, address):
        cmd='ping -w 5 -c 3 -q '+address
        command = Popen(shlex.split(cmd),stdout=PIPE, stderr=PIPE)
        stdout, stderr = command.communicate()
        stdout = str(stdout)
        if '/' not in stdout:
            return 0
        else:
            return float(stdout.split('/')[-3])