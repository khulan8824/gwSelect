import sys
sys.path.append(".")
import Client as cl
import Gateway as gt
import ClientManager as cm
import MessageClientProtocol
import MessageServerProtocol as server

import datetime
import os
from twisted.internet import reactor,protocol

node1 = gt.Gateway('10.139.40.85', 0.15, datetime.datetime.strptime('2018-02-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node2 = gt.Gateway('10.139.40.122', 0.20, datetime.datetime.strptime('2018-02-15 18:20:15', '%Y-%m-%d %H:%M:%S'),False)
node3 = gt.Gateway('10.138.57.2', 0.02, datetime.datetime.strptime('2018-02-15 18:45:07', '%Y-%m-%d %H:%M:%S'), False)
node4 = gt.Gateway('10.228.0.83', 0.5, datetime.datetime.strptime('2018-02-15 18:47:21', '%Y-%m-%d %H:%M:%S'), False)
node5 = gt.Gateway('10.138.77.2', 0.78, datetime.datetime.strptime('2018-02-15 18:26:19', '%Y-%m-%d %H:%M:%S'), False)
node6 = gt.Gateway('10.138.85.130', 0.35, datetime.datetime.strptime('2018-02-15 19:00:01', '%Y-%m-%d %H:%M:%S'), True)
node7 = gt.Gateway('10.139.17.4', 2.1, datetime.datetime.strptime('2018-02-15 18:26:04', '%Y-%m-%d %H:%M:%S'), False)
node8 = gt.Gateway('10.139.37.194', 1.5, datetime.datetime.strptime('2018-02-15 18:30:14', '%Y-%m-%d %H:%M:%S'), True)
node9 = gt.Gateway('10.138.62.2', 0.04, datetime.datetime.strptime('2018-02-15 19:47:59', '%Y-%m-%d %H:%M:%S'), False)
node10 = gt.Gateway('10.138.25.67', 0.09, datetime.datetime.strptime('2018-02-15 17:59:07', '%Y-%m-%d %H:%M:%S'), False)

listGW = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]

neighbour1 = cl.Client('10.228.207.66',[],[],None)
neighbour2 = cl.Client('10.228.207.65',[],[],None)
neighbour3 = cl.Client('10.139.40.87',[],[],None)
neighbour4 = cl.Client('10.139.94.108',[],[],None)
#neighbour5 = cl.Client('10.1.13.106',[],[],None)
#neighbour6 = cl.Client('10.1.9.75',[],[],None)
#neighbour7 = cl.Client('10.1.9.47',[],[],None)
#neighbour8 = cl.Client('10.1.15.70',[],[],None)
#neighbour9 = cl.Client('10.228.205.132',[],[],None)

#listNbs = [neighbour3, neighbour4,neighbour5,neighbour6, neighbour7, neighbour8, neighbour9]
listNbs = [neighbour1, neighbour3, neighbour4]

client4= cl.Client('10.228.207.200', listNbs, listGW, node7)
client4.senseLatency = 60
client4.cManager.rttLimit = 5

for gw in client4.cManager.gateways:
    #print(gw.address, ":", client4.cManager.pingTest(gw.address))
    if client4.cManager.ping.pingTest(gw.address) == 0:
        client4.removeGateway(gw)

client4.cManager.senseNeighbours()

client4.cManager.senseGateways()

if reactor.running:
    reactor.stop()

factory = protocol.ServerFactory()
factory.protocol = server.MessageServerProtocol
factory.protocol.client = client4
reactor.listenTCP(5555, factory)

reactor.callWhenRunning(client4.cManager.sendNeighbour)

reactor.run()
