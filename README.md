# NetSentinel

## Intelligent Network Behavior Monitoring System

NetSentinel is a network monitoring and behavior analysis system designed to capture, analyze, store, and report network traffic.

The project combines practical Computer Networks concepts with packet-level analysis, flow tracking, persistent storage, traffic intelligence, background monitoring, and automated reporting.

The long-term goal is to evolve NetSentinel toward intelligent network behavior analysis and anomaly detection.

---

## Current Focus

The current development focuses on building a reliable network monitoring core before adding advanced intelligence.

The implemented system currently covers:

- Network packet capture
- Packet parsing and protocol analysis
- IP address and port analysis
- TCP flag extraction
- Direction-independent network flow tracking
- Packet and flow statistics
- Persistent storage of network observations
- Traffic analysis and statistical queries
- Continuous background monitoring
- Automated traffic report generation
- SMTP-based email reporting
- Scheduled report execution

---

## System Architecture

The current monitoring pipeline is:

    Network Traffic
          |
          v
    Packet Capture
          |
          v
    Packet Parsing
          |
          v
    Flow Tracking
          |
          v
    SQLite Database
          |
          v
    Traffic Analysis
          |
          v
    Traffic Report
          |
          v
    SMTP Email

Background execution is separated into two systemd components:

    netsentinel.service
            |
            | Continuous packet capture
            v
    SQLite Database


    netsentinel-report.timer
            |
            | Scheduled execution
            v
    netsentinel-report.service
            |
            v
    Generate 6-hour report
            |
            v
    Send email

Packet capture and reporting are intentionally separated so that reporting or email failures do not directly interfere with continuous packet capture.

---

# Implemented Features

## 1. Packet Capture

NetSentinel uses Scapy to capture network packets from the system.

Captured packet information includes:

- Timestamp
- Source IP
- Destination IP
- Protocol
- Source port
- Destination port
- Packet size
- TCP flags

The packet capture component runs continuously as a background system service.

---

## 2. Packet Parsing

Raw packets are converted into structured packet information before being passed to the analysis layer.

The parser currently handles:

- IPv4 packets
- TCP packets
- UDP packets
- ICMP packets

The parser extracts useful metadata while avoiding unnecessary storage of complete raw packets.

---

## 3. Flow Tracking

Instead of analyzing every packet independently, NetSentinel groups packets into network flows.

A flow tracks:

- Source IP
- Destination IP
- Source port
- Destination port
- Protocol
- Start time
- End time
- Packet count
- Total bytes

The flow key is direction-independent so that traffic between two endpoints can be represented as one logical flow rather than treating each direction as a separate flow.

This allows NetSentinel to perform higher-level traffic analysis instead of treating every packet as an independent observation.

---

## 4. SQLite Persistence

Network observations are stored persistently using SQLite.

The database contains structures for:

- Flows
- Packets
- Anomalies

Indexes have been added for commonly queried fields.

The database allows NetSentinel to retain historical network observations rather than losing information when the capture process stops.

---

## 5. Traffic Intelligence

NetSentinel contains database queries for analyzing captured traffic.

Current analysis includes:

- Total packet count
- Total traffic volume
- Packet count by flow
- Flow packet statistics
- Protocol distribution
- Top source IPs
- Top destination IPs
- Top source ports
- Bandwidth usage
- Traffic over time
- Most active flows
- Overall traffic summaries

These queries form the foundation for the future anomaly-detection layer.

---

# Background Monitoring

NetSentinel uses Linux systemd to run packet capture continuously in the background.

The capture service is:

    netsentinel.service

Its responsibility is limited to continuous packet capture and database updates.

The service is configured to restart automatically if the capture process fails.

The intended behavior is:

    netsentinel.service starts
            |
            v
    Continuous packet capture
            |
            v
    Packets parsed and analyzed
            |
            v
    SQLite database updated

---

# Automated Reporting

NetSentinel can generate a traffic report covering the previous six hours.

The report currently includes:

- Reporting period
- Total packets
- Total traffic volume
- Protocol distribution
- Top source IPs
- Top destination IPs
- Traffic statistics

The reporting process is implemented as a separate systemd oneshot service:

    netsentinel-report.service

The service:

1. Generates the traffic report
2. Converts the report into an email
3. Sends it through SMTP
4. Exits after completing the task

Because it is a Type=oneshot service, the expected state after successful completion is:

    Active: inactive (dead)

This means the one-time task has completed successfully; it does not indicate a failure.

---

# SMTP Email Reporting

NetSentinel uses Gmail SMTP to deliver traffic reports automatically.

The reporting process follows:

    SQLite Database
          |
          v
    generate_report()
          |
          v
    EmailMessage
          |
          v
    Gmail SMTP
          |
          v
    Report Email

Email configuration is stored using environment variables rather than hard-coded credentials.

The configuration uses:

    NETSENTINEL_SMTP_HOST
    NETSENTINEL_SMTP_PORT
    NETSENTINEL_EMAIL
    NETSENTINEL_EMAIL_PASSWORD
    NETSENTINEL_REPORT_TO

Sensitive configuration is stored in .env.

The .env file is excluded from Git using .gitignore so that SMTP credentials are not committed to the repository.

---

# Automated 6-Hour Reporting

A separate systemd timer is used to schedule report generation:

    netsentinel-report.timer

The timer activates:

    netsentinel-report.service

The current automation is:

    netsentinel-report.timer
            |
            | Every 6 hours
            v
    netsentinel-report.service
            |
            v
    Generate report
            |
            v
    Send email

The timer is enabled through systemd so that it can be started automatically as part of the system configuration.

The current implementation uses elapsed timer-based scheduling.

A future version can make the reporting interval dependent on verified actual packet-capture time.

---

# Engineering Problems and Solutions

NetSentinel was developed incrementally, and several real implementation problems were encountered and solved during development.

These problems helped shape the final architecture.

---

## 1. Direction-Dependent Flow Problem

### Problem

Network communication has two directions.

For example:

    192.168.1.10 -> 8.8.8.8

and:

    8.8.8.8 -> 192.168.1.10

could incorrectly be treated as two separate flows.

This would make packet counts, byte counts, and flow statistics inaccurate.

### Solution

A direction-independent flow key was implemented.

The endpoints are normalized before creating the flow identity so that traffic in both directions belongs to the same logical flow.

---

## 2. Packet Timestamp Handling Problem

### Problem

During development and testing, the database contained different kinds of timestamps.

Some controlled test data used values such as:

    1000.0
    1001.0

while real packet capture produced Unix epoch timestamps.

This created complications for time-based queries and report generation.

### Solution

Database queries were adjusted to explicitly treat timestamps numerically where required.

SQLite casting was used for time-based comparisons and grouping where necessary.

This allowed controlled test data and real packet-capture data to be handled correctly.

---

## 3. Flow ID and Session Handling Problem

### Problem

During testing, parts of the implementation expected a session_id when generating flow IDs, while older test and integration paths were not providing it.

This produced errors such as:

    TypeError: create_flow_id() missing session_id

The integration path also had mismatches involving packet processing, the flow tracker, and session information.

### Solution

The flow and session information was traced through the capture, flow-tracking, database, and integration layers so that the required state was passed consistently between components.

This exposed an important architectural issue that was not obvious when individual components were tested independently.

---

## 4. Duplicate Flow Database Problem

### Problem

When NetSentinel was first run continuously through systemd, duplicate flow records produced SQLite UNIQUE constraint errors.

The long-running capture environment exposed flow-identity cases that were less obvious during isolated testing.

### Solution

The flow identity and persistence path were examined so that database flow identifiers were handled consistently across the capture and storage layers.

This was particularly important when moving from short test executions to continuous monitoring.

---

## 5. Report Timestamp and Time-Window Problem

### Problem

The report operates over a specific time window, such as:

    Last 6 hours

However, the database contained both controlled test timestamps and real packet-capture timestamps.

This required careful handling of:

    start_timestamp
    end_timestamp

### Solution

The reporting layer calculates the current time and derives the reporting window from it.

The database queries then use that calculated range to retrieve the relevant observations.

---

## 6. Python email.py Naming Conflict

### Problem

The project originally contained:

    src/reporting/email.py

Python's standard library also contains a package named:

    email

When the project attempted to import:

    from email.message import EmailMessage

Python incorrectly resolved the project's local email.py instead of Python's standard-library email package.

This produced an error similar to:

    ModuleNotFoundError:
    No module named 'email.message';
    'email' is not a package

### Solution

The local module was renamed from:

    email.py

to:

    email_sender.py

The reporting command was then changed to:

    python -m src.reporting.email_sender

This removed the naming conflict with Python's standard library.

---

## 7. Email Report Body Was Empty

### Problem

The email implementation initially used the equivalent of:

    message.set_content(print(generate_report(6)))

The problem was that print() displays a value but returns None.

Therefore, None was being passed as the email body instead of the generated report.

### Solution

The report was first stored:

    report = generate_report(6)

and then passed directly to the email:

    message.set_content(report)

This allowed the complete generated traffic report to appear in the email.

---

## 8. Systemd Service and Timer Separation

### Problem

There was a design question about whether the existing continuous capture service should also handle reporting.

Combining both responsibilities would make the capture service responsible for:

    Packet capture
    +
    Report generation
    +
    SMTP communication

A reporting or email failure could therefore unnecessarily affect the capture process.

### Solution

The responsibilities were separated:

    netsentinel.service
            |
            v
    Continuous packet capture


    netsentinel-report.service
            |
            v
    One-time report generation and email


    netsentinel-report.timer
            |
            v
    Schedules report service

This gives each systemd component a clear responsibility.

---

## 9. Systemd Unit Filename Typo

### Problem

During creation of the reporting service, the service file was initially created with:

    netsentinel-report.sevice

instead of:

    netsentinel-report.service

systemd consequently reported that the intended service could not be found.

### Solution

The filename was corrected and systemd was reloaded using:

    sudo systemctl daemon-reload

The service was then successfully started and tested.

---

## 10. SMTP Configuration and Credential Handling

### Problem

Email reporting requires SMTP authentication, but credentials should not be placed directly inside the Python source code.

Hard-coding credentials could expose the account credentials and could result in them being committed to Git.

### Solution

SMTP configuration was moved into environment variables loaded from .env.

The repository's .gitignore protects .env from being committed.

The project uses a Gmail App Password for SMTP authentication rather than the normal Gmail account password.

---

## 11. Systemd Report Service Verification

The reporting service was tested independently through systemd.

The service successfully returned:

    status=0/SUCCESS

and produced:

    Mail sent successfully to <receiver>

The service is configured as:

    Type=oneshot

because it performs one reporting task and then exits.

Therefore, after a successful run:

    Active: inactive (dead)

is expected behavior rather than an error.

---

## 12. Systemd Timer Verification

The reporting timer was validated using systemd tools.

The timer successfully showed:

    netsentinel-report.timer

as the active timer and:

    netsentinel-report.service

as the service it activates.

The report service was also manually executed through systemd and successfully delivered the report email.

---

# Testing

NetSentinel has been tested at multiple levels during development.

Testing has included:

- Flow tracking tests
- Database tests
- Integration testing
- Real packet capture
- SQLite persistence verification
- Traffic query verification
- Report generation
- SMTP email delivery
- systemd service execution
- systemd timer configuration

The reporting service has been successfully executed through systemd and has successfully delivered a real traffic report through Gmail SMTP.

---

# Current Project Structure

    NetSentinel/
    |
    +-- config/
    +-- data/
    +-- docs/
    |
    +-- src/
    |   |
    |   +-- capture/
    |   |   +-- capture.py
    |   |
    |   +-- parser/
    |   |   +-- packet.py
    |   |   +-- parser.py
    |   |
    |   +-- analyzer/
    |   |   +-- flow.py
    |   |   +-- flow_tracker.py
    |   |
    |   +-- database/
    |   |   +-- database.py
    |   |   +-- queries.py
    |   |
    |   +-- reporting/
    |       +-- report.py
    |       +-- email_sender.py
    |
    +-- tests/
    +-- requirements.txt
    +-- README.md
    +-- .gitignore

---

# Technology Stack

## Core Technologies

- Python — Primary implementation language
- Scapy — Packet capture and packet-level analysis
- SQLite — Persistent storage
- systemd — Background service and scheduled execution
- SMTP — Automated email delivery
- python-dotenv — Environment-based configuration
- pytest — Automated testing
- Git & GitHub — Version control

---

# Project Status

Under Development

## Completed

- [x] Networking foundations and project setup
- [x] Network packet capture
- [x] Packet parsing
- [x] Protocol identification
- [x] TCP flag extraction
- [x] Direction-independent flow tracking
- [x] SQLite database persistence
- [x] Database indexing
- [x] Traffic analysis queries
- [x] Traffic statistics
- [x] Continuous background packet capture
- [x] Traffic report generation
- [x] SMTP email reporting
- [x] Environment-based email configuration
- [x] Separate systemd reporting service
- [x] Automated report scheduling
- [x] Systemd reporting service testing
- [x] Automated timer verification

## Planned

- [ ] Network behavior baseline
- [ ] Rule-based anomaly detection
- [ ] Anomaly persistence and analysis
- [ ] Host behavior profiling
- [ ] DNS-based service/domain mapping
- [ ] Historical behavior comparison
- [ ] Real-time monitoring dashboard
- [ ] Network activity visualization
- [ ] Advanced anomaly detection
- [ ] Machine learning-based anomaly detection
- [ ] Advanced alerting
- [ ] Advanced intrusion detection capabilities

---

# Known Limitations and Future Improvements

## NAT / NAPT Awareness

A host-based monitoring system may observe the translated address rather than the original source address when traffic passes through NAT or NAPT.

For example, multiple devices behind the same NAT gateway may appear to NetSentinel as traffic originating from the same translated address.

This means source-IP-based behavior analysis can sometimes represent the NAT device rather than the individual internal device.

This limitation has been identified and will be considered in a future enhancement of the flow and behavior-analysis architecture.

---

## DNS-Based Traffic Attribution

IP addresses alone do not always provide an intuitive description of where traffic originated or which service it represents.

A future DNS-aware component may allow NetSentinel to associate observed network activity with domain or service information where available.

Conceptually:

    IP Address
        |
        v
    DNS Information
        |
        v
    Domain / Service Context

This can make traffic reports easier to interpret.

---

## Capture-Aware Reporting

The current reporting timer is based on elapsed scheduling time.

A future version can track actual capture availability so that a report described as covering six hours represents six hours of verified network observation rather than simply six hours of timer time.

This could also allow the system to explicitly identify periods where packet capture was unavailable.

---

## Intelligent Anomaly Detection

The current system establishes the infrastructure required for anomaly detection but does not yet depend on machine learning.

Future versions may introduce:

- Statistical baselines
- Traffic-volume deviations
- Unusual protocol behavior
- Unexpected port activity
- Host behavior profiling
- Time-based behavioral analysis
- Machine learning-based anomaly detection

The anomaly layer will be built on top of the existing packet, flow, and database infrastructure.

---

# Future Scope

NetSentinel is intended to evolve from a network monitoring system into an intelligent network behavior analysis platform.

Future development may include:

- Behavioral baselines
- Statistical anomaly detection
- DNS-based traffic attribution
- Host profiling
- Real-time dashboards
- Historical traffic analysis
- Machine learning-based anomaly detection
- Advanced alerting
- Improved NAT/NAPT awareness
- Capture-health monitoring
- More sophisticated intrusion detection

The project intentionally prioritizes a reliable monitoring and data-collection foundation before adding advanced intelligence.

---

# Project Vision

NetSentinel aims to evolve from a packet and flow monitoring system into an intelligent network behavior analysis platform.

The long-term objective is to understand normal network activity, identify meaningful deviations from established behavior, and provide useful reports and alerts while maintaining a structured historical record of network observations.