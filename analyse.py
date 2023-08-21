import json

class Link:
    def __init__(self, id_start, id_end, link_quality, forward_lqi):
        self.id_start = id_start
        self.id_end = id_end
        self.link_quality = link_quality
        self.forwardLqi = forward_lqi


class Node:
    def __init__(self, id, mac_addr):
        self.id = id
        self.mac_addr = mac_addr
        self.links = []
    
    def __init__(self, id, mac_addr, links):
        self.id = id
        self.mac_addr = mac_addr
        self.links = links
    
    def __str__(self):
        return self.id
    
    def addLink(self, link: Link):
        if link.id_start == self.id:
            self.links.append(link)


def main():
    node_list = []

    with open('voisins-c/voisins-c.log') as voisins_c_file:
        for voisins_c_line in voisins_c_file:

            vc_data = json.loads(voisins_c_line)

            for neighbours in vc_data['neighbours']:
                if "shortMac" in neighbours:
                    if "macEtendue" in neighbours:
                        node = Node(neighbours['shortMac'], neighbours['macEtendue'])
                        node_list[neighbours['shortMac']] = node
    
    for node in node_list:
        print("Node id: {}, macAddr: {}".format(node.id, node.mac_addr))


    # with open('stats-cpl-k/stats-cpl-k.log') as stats_cpl_k_file:
    #     for stats_cpl_k_line in stats_cpl_k_file:

    #         data = json.loads(stats_cpl_k_line)

    #         print(data['MacEtendue'])

if __name__ == "__main__":
    main()
