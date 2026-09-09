from dataclasses import dataclass

@dataclass
class PacketInfo:
    timestamp : float
    src_ip : str
    dst_ip : str
    protocol:str
    src_port: int | None
    dst_port: int | None
    size:int
    tcp_flags: str|None
