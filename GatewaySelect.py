import Gateway

class GatewaySelect():
    gateways = []
    
    def __init__(self, gateways):
        self.gateways = gateways
        
    def selectRandomize(self):
        selected = None
        if len(self.gateways) > 2:
            rand_choice = random.sample(set(self.gateways), 2)                    
            if rand_choice[0].latency > rand_choice[1].latency:
                selected = rand_choice[1]
            else:
                selected = rand_choice[0]
        else:
            selected = self.gateways[0]
        print(rand_choice[0].address,':', rand_choice[0].latency)
        print(rand_choice[1].address,':', rand_choice[1].latency)
        return selected
    
    def selectBest(self):
        selected = None
        for gw in self.gateways:
            if selected is None:
                print("Coming")
                selected = gw
                continue
            if gw.latency < selected.latency:
                selected = gw
                
        return selected