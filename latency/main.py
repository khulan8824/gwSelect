import sys
sys.path.append(".")
import Client as cl
import Gateway as gt
import ClientManager as cm
import MessageClientProtocol
import MessageServerProtocol as server

import datetime
import time
import os
from twisted.internet import reactor,protocol

node1 = gt.Gateway('10.139.39.98', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node2 = gt.Gateway('10.139.37.194', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node3 = gt.Gateway('10.228.192.210', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node4 = gt.Gateway('10.139.7.4', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node5 = gt.Gateway('10.1.33.36', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node6 = gt.Gateway('10.139.40.85', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node7 = gt.Gateway('10.139.40.122', 0.20, datetime.datetime.strptime('2018-02-15 18:20:15', '%Y-%m-%d %H:%M:%S'),False)
node8 = gt.Gateway('10.138.25.67', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node9 = gt.Gateway('10.138.57.2', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node10 = gt.Gateway('10.139.17.4', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node11 = gt.Gateway('10.138.85.130', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node12 = gt.Gateway('10.138.120.66', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node13 = gt.Gateway('10.140.93.35', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node14 = gt.Gateway('10.228.193.210', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
node15 = gt.Gateway('10.228.204.9', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)




n1 = gt.Gateway('10.139.39.98', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n2 = gt.Gateway('10.139.37.194', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n3 = gt.Gateway('10.228.192.210', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n4 = gt.Gateway('10.139.7.4', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n5 = gt.Gateway('10.1.33.36', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n6 = gt.Gateway('10.139.40.85', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n7 = gt.Gateway('10.139.40.122', 0.20, datetime.datetime.strptime('2018-02-15 18:20:15', '%Y-%m-%d %H:%M:%S'),False)
n8 = gt.Gateway('10.138.25.67', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n9 = gt.Gateway('10.138.57.2', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n10 = gt.Gateway('10.139.17.4', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n11 = gt.Gateway('10.138.85.130', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n12 = gt.Gateway('10.138.120.66', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n13 = gt.Gateway('10.140.93.35', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n14 = gt.Gateway('10.228.193.210', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)
n15 = gt.Gateway('10.228.204.9', 0.15, datetime.datetime.strptime('2018-03-15 18:59:15', '%Y-%m-%d %H:%M:%S'), status = False)


listGW = [node1, node2, node3, node4, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15]
#listGw = [node6, node7]
listActual = [n1,n2,n3,n4,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15]
#listActual = [n6,n7]

neighbour1 = cl.Client('10.228.207.66',[],[],None)
neighbour2 = cl.Client('10.139.40.87',[],[],None)
neighbour3 = cl.Client('10.228.205.132',[],[],None)
neighbour4 = cl.Client('10.1.15.70',[],[],None)
neighbour5 = cl.Client('10.1.13.106',[],[],None)
neighbour6 = cl.Client('10.1.9.132',[],[],None)
neighbour7 = cl.Client('10.139.94.108',[],[],None)


listNbs = [neighbour1, neighbour2, neighbour3]
#listNbs = [neighbour1, neighbour2, neighbour3, neighbour4, neighbour5]
#listNbs = [neighbour1, neighbour2, neighbour3, neighbour4, neighbour5, neighbour6, neighbour7]
#listNbs = [neighbour2, neighbour1]

client4= cl.Client('10.228.207.65', listNbs, listGW, node7)
client4.senseLatency = 120
client4.cManager.rttLimit = 5

client4.cManager.actualGateways = listActual

for gw in client4.cManager.gateways:
    if client4.cManager.ping.pingTest(gw.address) == 0:
        client4.removeGateway(gw)

client4.cManager.neighbourManager.senseNeighbours()


if reactor.running:
    reactor.stop()

factory = protocol.ServerFactory()
factory.protocol = server.MessageServerProtocol
factory.protocol.client = client4
reactor.listenTCP(5555, factory)

reactor.callWhenRunning(client4.cManager.neighbourManager.askMeasurements)

#client4.cManager.connect()

reactor.callLater(5, client4.cManager.senseGateways)
reactor.callLater(5, client4.cManager.senseAllGateways)
#reactor.callLater(5, client4.cManager.connectBest)
reactor.callLater(5, client4.cManager.connect)

reactor.run()


