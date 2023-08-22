import json

class Link:
    def __init__(self, id_start, id_end, link_quality):
        self.id_start = id_start
        self.id_end = id_end
        self.link_quality = link_quality

class Node:
    def __init__(self, id):
        if id == 0:
            self.id = -1
        else:
            self.id = id
        self.mac_addr = "-1"
        self.hop_from_main = -1
        self.success_rate = 0.0
        self.links = []
    
    def __str__(self):
        return self.id
    
    def addLink(self, link: Link):
        if link.id_start == self.id:
            self.links.append(link)


def main():
    # Get the total number of nodes    
    node_count = 0
    with open('traces-cpl/traces-cpl.log') as traces_cpl_file:
        for traces_cpl_line in traces_cpl_file:
            tc_data = json.loads(traces_cpl_line)
            if "shortMac" in tc_data:
                if tc_data['shortMac'] > node_count:
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

    # Get the distance to coordinator 

    with open('indicateurs-adp-k/indicateurs-adp-k.log') as indicateurs_adp_k_file:
        iak_data = json.load(indicateurs_adp_k_file)
        for entry in iak_data['AdpRoutingTable']:
            node_list[int(entry['DestAddress'])].hop_from_main = int(entry['HopCount'])

    # Get the droprate (from main coordinator) for each node
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
    with open('voisins-c/something.json') as voisins_c_file:
        # for voisins_c_line in voisins_c_file:
        vc_data = json.load(voisins_c_file)
        id = 0
        found = False
        for node in node_list:
            if found: break
            if node.mac_addr == vc_data['macEtendue']:
                found = True
                id = node.id
        
        for neighbour in vc_data['neighbours']:
            link = Link(id, neighbour['shortMac'], neighbour['linkQuality'])
            node_list[id].addLink(link)

        for pos in vc_data['pos']:
            link = Link(pos['shortMac'], id, pos['forwardLqi'])
            node_list[pos['shortMac']].addLink(link)

    i = 0
    for node in node_list:
        l = 1
        print("Node {}:\nmacAddr: {}, hop_to_main: {}, success_rate: {}\nNeighbours:".format(node.id, node.mac_addr, node.hop_from_main, node.success_rate))
        for link in node.links:
            print("Link {}: from {} to {}, quality {}".format(l, link.id_start, link.id_end, link.link_quality))
            l = l + 1

        print()
        i = i + 1




if __name__ == "__main__":
    main()
