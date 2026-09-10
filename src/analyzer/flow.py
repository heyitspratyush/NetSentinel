from dataclasses import dataclass

from src.parser.packet import PacketInfo

@dataclass
class Flow:
    src_ip : str
    src_port: int|None
    dst_ip:str
    dst_port:int| None
    protocol: str
    packet_count: int = 0
    total_bytes: int =0
    start_time: float|None = None
    end_time: float| None = None

    def add_packet(self,packet:PacketInfo):
        self.packet_count += 1
        self.total_bytes+= packet.size
        if (self.start_time == None or  self.start_time > packet.timestamp):
            self.start_time  = packet.timestamp
        if (self.end_time == None or  self.end_time < packet.timestamp):
            self.end_time  = packet.timestamp

def get_flow_key(packet: PacketInfo):
    endpoint_a = (packet.src_ip, packet.src_port)
    endpoint_b = (packet.dst_ip, packet.dst_port)

    endpoints = tuple(sorted([endpoint_a, endpoint_b]))

    return endpoints[0], endpoints[1], packet.protocol
