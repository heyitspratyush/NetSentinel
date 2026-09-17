import time
from datetime import datetime

from src.database.queries import (
    get_traffic_summary,
    get_protocol_distribution,
    get_top_src_ips,
    get_top_dst_ips,
    get_top_src_port,
    get_top_dst_port,
    get_most_active_flows,
)


def generate_report(hours=6):
    end_timestamp = time.time()
    start_timestamp = end_timestamp - (hours * 60 * 60)

    total_packets, total_bytes, unique_sources, unique_destinations = (
        get_traffic_summary(start_timestamp)
    )

    protocols = get_protocol_distribution(start_timestamp)
    top_sources = get_top_src_ips(start_timestamp)
    top_destinations = get_top_dst_ips(start_timestamp)
    top_src_ports = get_top_src_port(start_timestamp)
    top_dst_ports = get_top_dst_port(start_timestamp)

    start_time = datetime.fromtimestamp(start_timestamp)
    end_time = datetime.fromtimestamp(end_timestamp)

    report = []

    report.append("=" * 55)
    report.append("             NetSentinel Traffic Report")
    report.append("=" * 55)
    report.append("")

    report.append("REPORTING PERIOD")
    report.append("-" * 55)
    report.append(f"Start : {start_time}")
    report.append(f"End   : {end_time}")
    report.append("")

    report.append("TRAFFIC SUMMARY")
    report.append("-" * 55)
    report.append(f"Total Packets          : {total_packets}")
    report.append(f"Total Bytes            : {total_bytes}")
    report.append(f"Unique Source IPs      : {unique_sources}")
    report.append(f"Unique Destination IPs : {unique_destinations}")
    report.append("")

    report.append("PROTOCOL DISTRIBUTION")
    report.append("-" * 55)

    for protocol, count in protocols:
        report.append(f"{str(protocol):20} : {count}")

    report.append("")

    report.append("TOP SOURCE IPs")
    report.append("-" * 55)

    for ip, count in top_sources[:5]:
        report.append(f"{str(ip):20} : {count} packets")

    report.append("")

    report.append("TOP DESTINATION IPs")
    report.append("-" * 55)

    for ip, count in top_destinations[:5]:
        report.append(f"{str(ip):20} : {count} packets")

    report.append("")

    report.append("TOP SOURCE PORTS")
    report.append("-" * 55)

    for port, count in top_src_ports[:5]:
        report.append(f"{str(port):20} : {count} packets")

    report.append("")

    report.append("TOP DESTINATION PORTS")
    report.append("-" * 55)

    for port, count in top_dst_ports[:5]:
        report.append(f"{str(port):20} : {count} packets")

    report.append("")

    report.append("MOST ACTIVE FLOWS")
    report.append("-" * 55)

    active_flows = get_most_active_flows(start_timestamp)

    for flow_id, packets, bytes_count in active_flows:
        report.append(
            f"Flow {flow_id}: {packets} packets, {bytes_count} bytes"
        )

    report.append("")
    report.append("=" * 55)

    return "\n".join(report)