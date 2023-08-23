import json

def calc_SNR(lqi_value):
    return (lqi_value / 4) - 10

class Link:
    def __init__(self, id_start, id_end, link_quality, pvt):
        self.id_start = id_start
        self.id_end = id_end
        self.link_quality = link_quality
        self.pvt = pvt
        self.success_rate = -1
        self.snr = calc_SNR(int(link_quality))
    
    def toString(self):
        return "from {} to {}, quality {}, pvt {}, success_rate {}, SNR {}".format(self.id_start, self.id_end, self.link_quality, self.pvt, self.success_rate, self.snr)

    def setSuccessRate(self, success_rate):
        self.success_rate = success_rate
    
    def setSNR(self, snr):
        self.snr = snr

    def hasValidsuccess_rate(self):
        if self.success_rate != -1: return True
        else: return False

class Node:
    def __init__(self, id):
        self.id = id
        self.mac_addr = "-1"
        self.hop_from_main = -1
        self.success_rate = 0.0
        self.links = []
    
    def addLink(self, link: Link):
        if link.id_start == self.id:
            self.links.append(link)
    
    def indexOfLink(self, start, end):
        for link in self.links:
            if start == link.id_start and end == link.id_end:
                return self.links.index(link)

def main():
    # Get the total number of nodes    
    node_count = 0
    with open('traces-cpl/traces-cpl.log') as traces_cpl_file:
        for traces_cpl_line in traces_cpl_file:
            tc_data = json.loads(traces_cpl_line)
            if "shortMac" in tc_data and tc_data['shortMac'] > node_count:
                node_count = tc_data['shortMac']
    
    node_list = []
    for i in range (0, node_count+1):
        node_list.append(Node(i))
    
    # Get the mac address of each node
    with open('traces-cpl/traces-cpl.log') as traces_cpl_file:
        for traces_cpl_line in traces_cpl_file:
            tc_data = json.loads(traces_cpl_line)

            if "mac" in tc_data:
                if "shortMac" in tc_data:
                    node_list[tc_data['shortMac']].id = tc_data['shortMac']
                    node_list[tc_data['shortMac']].mac_addr = tc_data['mac']

    # Get the distance (hop count) to coordinator for each node
    with open('indicateurs-adp-k/indicateurs-adp-k.log') as indicateurs_adp_k_file:
        iak_data = json.load(indicateurs_adp_k_file)
        for entry in iak_data['AdpRoutingTable']:
            node_list[int(entry['DestAddress'])].hop_from_main = int(entry['HopCount'])

    # Get the success rate (from main coordinator) for each node
    with open('stats-cpl-k/stats-cpl-k.log') as stats_cpl_k_file:
        for stats_cpl_k_line in stats_cpl_k_file:
            sck_data = json.loads(stats_cpl_k_line)
            found = False
            for node in node_list:
                if found: break
                if node.mac_addr == sck_data['MacEtendue']:
                    found = True
                    node.success_rate = int(sck_data['ComOkNumber']) / int(sck_data['ComNumber'])  

    # Get the neighbour data of each node
    with open('voisins-c/voisins-c.log') as voisins_c_file:
        for voisins_c_line in voisins_c_file:
            vc_data = json.loads(voisins_c_line)
            id = 0
            found = False
            for node in node_list:
                if found: break
                if node.mac_addr == vc_data['macEtendue']:
                    found = True
                    id = node.id
            
            for neighbour in vc_data['neighbours']:
                link = Link(id, neighbour['shortMac'], neighbour['linkQuality'], -1)
                node_list[id].addLink(link)

            for pos in vc_data['pos']:
                temp_link_index = node_list[pos['shortMac']].indexOfLink(pos['shortMac'], id)
                if temp_link_index is not None:
                    temp_link_pvt = node_list[pos['shortMac']].links[temp_link_index].pvt
                    if temp_link_pvt < pos['posValidTime']:
                        node_list[pos['shortMac']].links[temp_link_index].link_quality = pos['forwardLqi']
                        node_list[pos['shortMac']].links[temp_link_index].pvt = pos['posValidTime']

                else :
                    link = Link(pos['shortMac'], id, pos['forwardLqi'], pos['posValidTime'])
                    node_list[pos['shortMac']].addLink(link)

    # Get the neighbours for coodindator
    with open('voisins-k/voisins-k.log') as voisins_k_file:
        for voisins_k_line in voisins_k_file:
            vk_data = json.loads(voisins_k_line)
            if int(vk_data['LQIStatistics']['AverageRevLQI']) != 0 :
                temp_mac_addr = vk_data['MacEtendue']
                found = False
                for node in node_list:
                    if found: break
                    if node.mac_addr == vk_data['MacEtendue']:
                        found = True
                        if not node_list[0].indexOfLink(0, node.id):
                            link = Link(0, node.id, vk_data['LQIStatistics']['AverageRevLQI'], -1)
                            node_list[0].addLink(link)

    # Calculate the SNR for each link 
    # First, get the max hop count
    max_hop_count = -1
    for i in range (1, node_count+1):
        if node_list[i].hop_from_main > max_hop_count:
            max_hop_count = node_list[i].hop_from_main

    # Easy one: the nodes with 1 hop count: set the link success rate by the node success rate directly
    for i in range (1, node_count+1):
        if node_list[i].hop_from_main == 1:
           node_list[0].links[node_list[0].indexOfLink(0, i)].setSuccessRate(node_list[i].success_rate * 100)

    # Then for node with hop_count h, msg will pass a node that has h-1 hop count, thus calculate the success rate of link
    # for i in range (1, node_count+1):
    #     if node_list[i].hop_from_main == 2:
            
            

    i = 0
    for node in node_list:
        l = 1
        print("Node {}:\nmacAddr: {}, hop_to_main: {}, success_rate: {}\nNeighbours:".format(node.id, node.mac_addr, node.hop_from_main, node.success_rate))
        for link in node.links:
            print("Link {}:".format(l), link.toString())
            l = l + 1

        print()
        i = i + 1

if __name__ == "__main__":
    main()
