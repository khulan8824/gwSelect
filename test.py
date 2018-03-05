import Gateway
import GatewaySelect

                
node1 = Gateway('10.139.40.85', 0.15, '2018 Feb 15 18:59:15')
node2 = Gateway('10.139.40.122', 0.20, '2018 Feb 15 18:20:15')
node3 = Gateway('10.138.57.2', 0.02, '2018 Feb 15 18:45:07')
node4 = Gateway('10.228.0.83', 0.5, '2018 Feb 15 18:47:21')
node5 = Gateway('10.138.77.2', 0.78, '2018 Feb 15 18:26:19')
node6 = Gateway('10.138.85.130', 0.35, '2018 Feb 15 19:00:01')
node7 = Gateway('10.139.17.4', 2.1, '2018 Feb 15 18:26:04')
node8 = Gateway('10.139.37.194', 1.5, '2018 Feb 15 18:30:14')
node9 = Gateway('10.138.62.2', 0.04, '2018 Feb 15 19:47:59')
node10 = Gateway('10.138.25.67', 0.09, '2018 Feb 15 17:59:07')

gws = GatewaySelect([node1, node2, node3, node4, node5, node6, 
                    node7, node8, node9, node10])
bestR = gws.selectRandomize()
print(bestR.address, '>>', bestR.latency)

best = gws.selectBest()
print(best.address, '>>', best.latency)