from analyse import *

def to_prefix(id) -> str:
    if id < 15 :
        return "FD00:0000:0000:000" + format(id+1, 'x') + "::/64"
    elif id < 255:
        return "FD00:0000:0000:00" + format(id+1, 'X') + "::/64"
    else :
        return ""

def ac_on_furthest(node_count, node_list):
    # Get the furthest nodes
    hop_max = get_max_hop_count(node_list, node_count)
    furthest_nodes = []
    for node in node_list:
        if node.hop_from_main == hop_max:
            furthest_nodes.append(node)

    # Compare which one has the most links
    selected_node = furthest_nodes[0]
    for node in furthest_nodes:
        if len(node.links) > len(selected_node.links):
            selected_node = node
    
    # print(f"Node {selected_node.id}:\nmacAddr: {selected_node.mac_addr}, hop_to_main: {selected_node.hop_from_main}, success_rate: {selected_node.success_rate}")
    ac_id_list = [selected_node]
    return ac_id_list

def get_min_node(Q: list, dist: list):
    min = 255
    # print(f"Q is {Q} and dist is {dist}")
    res = -1
    for i in Q:
        if dist[i] < min: 
            min = dist[i]
            res = i
    # print(f"res is {res}")
    return res

# A route finding algorithm based on dijkstra's algorithm
def find_route(node_list, node_count, start_id, end_id):
    if start_id == end_id: return [start_id]
    dist = []
    prev = []
    # Q is a list of id (integer) rather than a list of nodes
    Q = []
    for i in range (0, node_count):
        dist.append(255)
        prev.append(-1)
        Q.append(i)
    dist[start_id] = 0
    
    while len(Q):
        u = get_min_node(Q, dist)
        if u == end_id: break
        Q.remove(u)

        for link in node_list[u].links:
            alt = dist[u] + 1
            if alt < dist[link.id_end]:
                dist[link.id_end] = alt
                prev[link.id_end] = u

    S = []
    u = end_id
    if prev[u] is not None or u == start_id:
        while u != -1:
            S.insert(0, u)
            u = prev[u]

    print(f"Route from {start_id} to {end_id} is {S}.")
    return S

def find_route_test(node_list, start_id, end_id):
    if start_id == 1:
        if(end_id == 0): return [1, 0]
        if(end_id == 1): return [1]
        if(end_id == 2): return [1, 2]
        if(end_id == 3): return [1, 2, 3]
        if(end_id == 4): return [1, 2, 3, 4]
        if(end_id == 5): return [1, 2, 3, 5]
        if(end_id == 6): return [1, 2, 3, 6]
        if(end_id == 7): return [1, 2, 3, 6, 7]
    if start_id == 2:
        if(end_id == 0): return [2, 1, 0]
        if(end_id == 1): return [2, 1]
        if(end_id == 2): return [2]
        if(end_id == 3): return [2, 3]
        if(end_id == 4): return [2, 3, 4]
        if(end_id == 5): return [2, 3, 5]
        if(end_id == 6): return [2, 3, 6]
        if(end_id == 7): return [2, 3, 6, 7]
    if start_id == 3:
        if(end_id == 0): return [3, 2, 1, 0]
        if(end_id == 1): return [3, 2, 1]
        if(end_id == 2): return [3, 2]
        if(end_id == 3): return [3]
        if(end_id == 4): return [3, 4]
        if(end_id == 5): return [3, 5]
        if(end_id == 6): return [3, 6]
        if(end_id == 7): return [3, 6, 7]
    if start_id == 4:
        if(end_id == 0): return [4, 3, 2, 1, 0]
        if(end_id == 1): return [4, 3, 2, 1]
        if(end_id == 2): return [4, 3, 2]
        if(end_id == 3): return [4, 3]
        if(end_id == 4): return [4]
        if(end_id == 5): return [4, 3, 5]
        if(end_id == 6): return [4, 3, 6]
        if(end_id == 7): return [4, 3, 6, 7]
    if start_id == 5:
        if(end_id == 0): return [5, 3, 2, 1, 0]
        if(end_id == 1): return [5, 3, 2, 1]
        if(end_id == 2): return [5, 3, 2]
        if(end_id == 3): return [5, 3]
        if(end_id == 4): return [5, 3, 4]
        if(end_id == 5): return [5]
        if(end_id == 6): return [5, 3, 6]
        if(end_id == 7): return [5, 3, 6, 7]
    if start_id == 6:
        if(end_id == 0): return [6, 3, 2, 1, 0]
        if(end_id == 1): return [6, 3, 2, 1]
        if(end_id == 2): return [6, 3, 2]
        if(end_id == 3): return [6, 3]
        if(end_id == 4): return [6, 3, 4]
        if(end_id == 5): return [6, 3, 5]
        if(end_id == 6): return [6]
        if(end_id == 7): return [6, 7]
    if start_id == 7:
        if(end_id == 0): return [7, 6, 3, 2, 1, 0]
        if(end_id == 1): return [7, 6, 3, 2, 1]
        if(end_id == 2): return [7, 6, 3, 2]
        if(end_id == 3): return [7, 6, 3]
        if(end_id == 4): return [7, 6, 3, 4]
        if(end_id == 5): return [7, 6, 3, 4]
        if(end_id == 6): return [7, 6]
        if(end_id == 7): return [7]
    

def ac_by_total_count(node_count, node_list):
    ac_id_list = []
    total_dist_list = [1e7]
    for i in range (1, node_count):
        total_dist_list.append(0)
        for node in node_list:
            dist_mc = node.hop_from_main
            route = find_route(node_list, node_count, i, node.id)
            dist_ac = len(route) - 1
            # print(f"For {node.id}, dist_mc to N0 = {dist_mc}, dist_ac to N{i} = {dist_ac}, value {min(dist_mc, dist_ac)} selected.")
            total_dist_list[i] = total_dist_list[i] + min(dist_mc, dist_ac)
        # print(f"Total dist for N{i} is {total_dist_list[i]}")
    selected_node_id = (total_dist_list.index(min(total_dist_list)))
    ac_id_list.append(node_list[selected_node_id])
    return ac_id_list


def write_to_xml_with_ac(node_list, node_count, add_concentrator_id_list, file_name):
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

    # node_configuration
    node_config = etree.Element("node_configuration")
    sim_config.append(node_config)
    defaults = etree.Element("defaults")
    node_config.append(defaults)

    # Supernode section
    g3adp = etree.Element("g3adp")
    defaults.append(g3adp)
    g3_ib = etree.Element("g3_informationbase")
    g3adp.append(g3_ib)
    for ac_id in add_concentrator_id_list:
        g3_st = etree.Element("g3_subnettable")
        prefix = etree.Element("prefix")
        prefix.text = to_prefix(ac_id)
        g3_st.append(prefix)
        sa = etree.Element("short_addr")
        sa.text = str(ac_id)
        g3_st.append(sa)
        g3_ib.append(g3_st)

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

    for ac_id in add_concentrator_id_list:
        node = etree.Element("node")
        node.set('eui', to_eui(ac_id))
        g3app = etree.Element("g3app")
        tun = etree.Element("tun")
        tun.text = to_prefix(ac_id)
        g3app.append(tun)
        node.append(g3app)
        node_config.append(node)

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

    with open (file_name, "wb") as output :
        tree.write(output, encoding='utf-8', xml_declaration=True)

def test():
    node_count = 8
    node_list = []
    for i in range (0, node_count):
        n = Node(i)
        if i==0:
            l = Link(0, 1, 128, -1)
            l.setSuccessRate(256)
            n.addLink(l)
        elif i==1:
            l1 = Link(1, 0, 128, -1)
            l2 = Link(1, 2, 128, -1)
            l1.setSuccessRate(256)
            l2.setSuccessRate(256)
            n.addLink(l1)
            n.addLink(l2)
            n.hop_from_main = 1
        elif i==2:
            l1 = Link(2, 1, 128, -1)
            l2 = Link(2, 3, 128, -1)
            l1.setSuccessRate(256)
            l2.setSuccessRate(256)
            n.addLink(l1)
            n.addLink(l2)
            n.hop_from_main = 2
        elif i==3:
            l1 = Link(3, 2, 128, -1)
            l2 = Link(3, 4, 128, -1)
            l3 = Link(3, 5, 128, -1)
            l4 = Link(3, 6, 128, -1)
            l1.setSuccessRate(256)
            l2.setSuccessRate(256)
            l3.setSuccessRate(256)
            l4.setSuccessRate(256)
            n.addLink(l1)
            n.addLink(l2)
            n.addLink(l3)
            n.addLink(l4)
            n.hop_from_main = 3
        elif i==4:
            l = Link(4, 3, 128, -1)
            l.setSuccessRate(256)
            n.addLink(l)
            n.hop_from_main = 4
        elif i==5:
            l = Link(5, 3, 128, -1)
            l.setSuccessRate(256)
            n.addLink(l)
            n.hop_from_main = 4
        elif i==6:
            l1 = Link(6, 3, 128, -1)
            l2 = Link(6, 7, 128, -1)
            l1.setSuccessRate(256)
            l2.setSuccessRate(256)
            n.addLink(l1)
            n.addLink(l2)
            n.hop_from_main = 4
        else:
            l = Link(7, 6, 128, -1)
            l.setSuccessRate(256)
            n.addLink(l)
            n.hop_from_main = 5
        n.success_rate = 100.0
        node_list.append(n)
    
    # print_to_terminal(node_list)

    # ac_list = ac_on_furthest(node_count, node_list)
    ac_list = ac_by_total_count(node_count, node_list)
    print("Selected Node: ", str(ac_list[0]))

    
    return None

def main():
    if "-t" in sys.argv:
        test()
        return None
    
    # Get the total number of nodes
    node_count = get_node_count(sys.argv[1])

    # Create a list of nodes
    node_list = []
    for i in range (0, node_count):
        node_list.append(Node(i))

    # Get the info of nodes from log files
    get_info_from_files(sys.argv[1], node_list, node_count)

    ac_list = ac_on_furthest(node_count, node_list)

    write_to_xml_with_ac(node_list, node_count, ac_list, "topo_tun.xml")

if __name__ == "__main__":  
    main()
