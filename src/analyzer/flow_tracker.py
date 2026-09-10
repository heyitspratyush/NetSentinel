from src.parser.packet import PacketInfo
from src.analyzer.flow import Flow, get_flow_key

class FlowTracker:
    def __init__(self):
        self.flows = {}
    
    def process_packet(self,packet: PacketInfo):
        key = get_flow_key(packet)
        if key not in self.flows:
            flow = Flow(
                src_ip = packet.src_ip,
                src_port=packet.src_port,
                dst_ip= packet.dst_ip,
                dst_port = packet.dst_port,
                protocol = packet.protocol
            )
            self.flows[key] = flow

        self.flows[key].add_packet(packet)
        
    def get_flows(self):
        return self.flows.values()