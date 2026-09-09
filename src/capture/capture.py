from scapy.all import sniff,IP,TCP,UDP

def capture_packets(interface,count):
    return sniff(iface=interface,count= count)


def print_packet_info(packets):
    for packet in packets:
        if IP in packet:
            ip_layer = packet.getlayer(IP)
            if TCP in packet:
                protocol = "TCP"
                transport_layer = packet.getlayer(TCP)
            elif UDP in packet:
                protocol = "UDP"
                transport_layer = packet.getlayer(UDP)
            else:
                continue


            print(protocol,ip_layer.src,":",transport_layer.sport, "->", ip_layer.dst,":",transport_layer.dport)

if __name__ == "__main__":
    interface = "Intel(R) Wi-Fi 6E AX211 160MHz"
    packets=capture_packets(interface,10)
    print_packet_info(packets)
