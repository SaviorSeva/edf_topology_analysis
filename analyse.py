import json
import xml.etree.ElementTree as etree

# According to Enedis, the average SNR value (in dB) equals to (LQIvalue / 4) - 10
def calc_SNR(lqi_value):
    return (lqi_value / 4) - 10

def to_eui(id):
    if id < 15 :
        return "FF:FF:FF:FF:FE:00:00:0" + format(id+1, 'x')
    elif id < 255:
        return "FF:FF:FF:FF:FE:00:00:" + format(id+1, 'x')
    else :
        return None
    

# SNR(dB) to Attenuation(dB) when noise=48dBuV: Att = 72-SNR, SNR range [-10, 22]
# LQI to Attenuation(dB) when noise=48dBuV: Att = 82-0.25*LQI, LQI range [0, 128]
# Attuation range: [50, 82]
def lqi_to_att(lqi_value):
    return int(82 - 0.25*int(lqi_value))


# A class for storing link info.
# pvt: pos table valid time, used for choosing a valid link_quality value from multiple entries
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

# A class for storing link info.
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
    
    # Return the first index of a link, identified by start & end node id.
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
    node_count = node_count + 1

    # Create a list of nodes for further use
    node_list = []
    for i in range (0, node_count):
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
            
            # Find the node with such mac address from the node list
            id = 0
            found = False
            for node in node_list:
                if found: break
                if node.mac_addr == vc_data['macEtendue']:
                    found = True
                    id = node.id
            
            # Create links from neighbours from neighbour table.
            # Note in node_A's neighbour table, if an entry with node_B exists, the direction of link is node_B -> node_A.
            # If the link list already contains such link, the value in neighbour table will be ignored.
            for neighbour in vc_data['neighbours']:
                temp_link_index = node_list[neighbour['shortMac']].indexOfLink(neighbour['shortMac'], id)
                if temp_link_index is None:
                    link = Link(neighbour['shortMac'], id, neighbour['linkQuality'], -1)
                    node_list[neighbour['shortMac']].addLink(link)


            # Create links to neighbours from pos table.
            # Note in node_A's pos table, if an entry with node_B exists, the direction of link is node_A -> node_B.
            # If multiple entries for a same link exists, choose the one with the highest posValidTime (according to Enedis).
            for pos in vc_data['pos']:
                temp_link_index = node_list[id].indexOfLink(id, pos['shortMac'])
                if temp_link_index is not None:
                    temp_link_pvt = node_list[id].links[temp_link_index].pvt
                    if temp_link_pvt < pos['posValidTime']:
                        node_list[id].links[temp_link_index].link_quality = pos['forwardLqi']
                        node_list[id].links[temp_link_index].pvt = pos['posValidTime']
                else :
                    link = Link(id, pos['shortMac'], pos['forwardLqi'], pos['posValidTime'])
                    node_list[id].addLink(link)

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
                        if node_list[0].indexOfLink(0, node.id) is None:
                            link = Link(0, node.id, vk_data['LQIStatistics']['AverageRevLQI'], -2)
                            node_list[0].addLink(link)

    # Calculate the root = gfg.Element("Catalog")success rate for each link 
    # First, get the max hop count
    max_hop_count = -1
    current_count = 2
    for i in range (1, node_count):
        if node_list[i].hop_from_main > max_hop_count:
            max_hop_count = node_list[i].hop_from_main

    # Easy one: the nodes with 1 hop count: set the link success rate by the node success rate directly
    for i in range (1, node_count):
        if node_list[i].hop_from_main == 1:
           node_list[0].links[node_list[0].indexOfLink(0, i)].setSuccessRate(node_list[i].success_rate)

    # Then for node with hop_count h, msg will pass a node that has h-1 hop count, thus calculate the success rate of link
    while current_count <= max_hop_count:
        for i in range (1, node_count):
            if node_list[i].hop_from_main == current_count:
                for m in range (1, node_count):
                    if node_list[m].hop_from_main == current_count-1:
                        link_success_rate = node_list[i].success_rate / node_list[m].success_rate
                        if link_success_rate <= 1.0:
                            temp = node_list[m].indexOfLink(m, i)
                            if temp is not None:
                                node_list[m].links[temp].setSuccessRate(link_success_rate)
        current_count = current_count + 1        
            
    # Print all infos to the terminal. 
    # To show all infos please redirect the output to a file.
    # i = 0
    # for node in node_list:
    #     l = 1
    #     print(f"Node {node.id}:\nmacAddr: {node.mac_addr}, hop_to_main: {node.hop_from_main}, success_rate: {node.success_rate}\nNeighbours:")
    #     for link in node.links:
    #         print("Link {}:".format(l), link.toString())
    #         l = l + 1

    #     print()
    #     i = i + 1

    print(f"Node count: {node_count}")

    # Translate the info from node_list to nSim xml config file
    sim_config = etree.Element("simulation_config")
    
    sim_config.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    sim_config.set('xsi:noNamespaceSchemaLocation', "../../../share/xml/schema/nsim/g3_config.xsd")

    simu = etree.Element("simulator")
    sim_config.append(simu)

    nodes = etree.SubElement(simu, "nodes")
    nodes.text = str(node_count)

    target = etree.SubElement(simu, "target")
    target.text = "lib/x64/libg3_target.so"

    sp_target = etree.SubElement(simu, "special_target")
    sp_target.set('eui', to_eui(0))
    sp_target.text = "lib/x64/libg3_coord_target.so"

    min_time_step = etree.SubElement(simu, "min_time_step")
    min_time_step.text = "100000"

    max_time_step = etree.SubElement(simu, "max_time_step")
    max_time_step.text = "500000000"

    # node_configuration
    node_config = etree.Element("node_configuration")
    sim_config.append(node_config)
    defaults = etree.Element("defaults")
    node_config.append(defaults)

    g3app = etree.Element("g3app")
    defaults.append(g3app)
    pan_id = etree.Element("pan_id")
    pan_id.text = "23620"
    g3app.append(pan_id)


    g3tstapp = etree.Element("g3tstapp")
    defaults.append(g3tstapp)
    mode = etree.Element("mode")
    mode.text = "0"
    g3tstapp.append(mode)

    # connectivity
    connectivity = etree.Element("connectivity")
    sim_config.append(connectivity)
    defaults = etree.Element("defaults")
    connectivity.append(defaults)
    droprate = etree.Element("droprate")
    droprate.text = "100"
    defaults.append(droprate)
    g3_noise = etree.Element("g3_noise")
    g3_noise.text = "48"
    defaults.append(g3_noise)
    g3_maxlqi = etree.Element("g3_maxlqi")
    g3_maxlqi.text = "128"
    defaults.append(g3_maxlqi)

    for node in node_list:
        node_xml = etree.Element("node")
        node_xml.set('eui', to_eui(node.id))
        connectivity.append(node_xml)

        for link in node.links:
            peer = etree.Element("peer")
            peer.set('eui', to_eui(link.id_end))
            node_xml.append(peer)
            droprate = etree.Element("droprate")
            droprate.text = "0"
            peer.append(droprate)

            g3_attenuation = etree.Element("g3_attenuation")
            g3_attenuation.text = str(lqi_to_att(link.link_quality))
            peer.append(g3_attenuation)


    tree = etree.ElementTree(sim_config)
    etree.indent(tree, '  ')

    with open ("topo.xml", "wb") as output :
        tree.write(output, encoding='utf-8', xml_declaration=True)


    # This following code verifies no duplicated link exists for every node
    # i = 0
    # for node in node_list:
    #     l = 0
    #     while l < len(node.links):
    #         m = 1
    #         linkA = node.links[l]
    #         while l+m < len(node.links):
    #             linkB = node.links[l+m]
    #             if linkA.id_start == linkB.id_start and linkA.id_end == linkB.id_end:
    #                 print("ERROR: Repeat detected for\n", linkA.toString(), "\n", linkB.toString())
    #             m = m + 1
    #         l = l + 1
    #     i = i + 1

if __name__ == "__main__":
    main()
