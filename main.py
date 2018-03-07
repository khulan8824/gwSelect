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


client= Client('10.139.40.77', [], [node1,node2,node4, node8, node9, node10, node6,node7, node5, node3], node9)
for gw in client.gateways:
    if client.pingTest(gw.address) is False:
        if gw.address == client.defaultGateway.address:
            client.selectNext()
        client.removeGateway(gw)
client.connect()