from analyse import *

def to_prefix(id) -> str:
    if id < 15 :
        return "FD00:0000:0000:000" + format(id+1, 'x') + "::/64"
    elif id < 255:
        return "FD00:0000:0000:00" + format(id+1, 'X') + "::/64"
    else :
        return ""

def ac_on_furthest(node_count, node_list):
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
    
    print(f"Node {selected_node.id}:\nmacAddr: {selected_node.mac_addr}, hop_to_main: {selected_node.hop_from_main}, success_rate: {selected_node.success_rate}\nNeighbours:")
    l = 1
    for link in selected_node.links:
        print("Link {}:".format(l), link.toString())
        l = l + 1

    return None

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

def main():
    # Get the total number of nodes
    node_count = get_node_count(sys.argv[1])

    # Create a list of nodes
    node_list = []
    for i in range (0, node_count):
        node_list.append(Node(i))

    # Get the info of nodes from log files
    get_info_from_files(sys.argv[1], node_list, node_count)

    ac_on_furthest(node_count, node_list)

    ac_list = [42, 62]

    write_to_xml_with_ac(node_list, node_count, ac_list, "topo_tun.xml")

if __name__ == "__main__":  
    main()
