# Network Stress & Monitoring Suite

This repository contains a suite of Python-based tools for network stress testing and proactive performance monitoring. These tools are designed for security researchers and network administrators to assess network resilience and detect anomalies in real-time.

## Disclaimer

**This software is intended for educational and ethical purposes only.** Performing stress tests on networks or servers you do not own or have explicit permission to test is illegal. The author is not responsible for any misuse or damage caused by this program. Always act responsibly and within the law.

-----

## Features

### `stress.py` - Advanced Network Stress Tester

  * **High-Performance Floods**: Capable of TCP, UDP, and HTTP flood attacks.
  * **Real-time Feedback**: Displays live statistics during an attack, including elapsed time, total packets sent, and the current packets-per-second (PPS) rate.
  * **Multi-threaded**: Utilizes a `ThreadPoolExecutor` for high-performance, concurrent traffic generation.
  * **Configurable Payloads**: Allows specifying the packet size (in bytes) for UDP floods using the `--size` argument.
  * **Graceful Shutdown**: Handles `Ctrl+C` (KeyboardInterrupt) to stop attacks cleanly and provide a final summary.

### `monitor.py` - Real-time Network Monitor & Alerter

  * **Real-time Rate Calculation**: Monitors network traffic and calculates current throughput (KB/s) and packet rates (pps) in real-time.
  * **Threshold-Based Alerting**: Proactively monitors incoming traffic and triggers a console alert if the packet-per-second rate exceeds a user-defined threshold (e.g., `--pps-threshold 2000`).
  * **Configurable Endpoints**: Allows users to specify the targets for connectivity checks via command-line arguments (`--ping-target` and `--http-target`).
  * **Actionable Display**: Provides a clean, single-line console output showing the most critical metrics: traffic rates, latency, and service availability.
  * **Data Logging**: Saves all collected statistics, including rates and timestamps, to a CSV file (e.g., `network_stats.csv`) for later analysis.

-----

## Installation

1.  Clone the repository:

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  Create and activate a Python virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  Install the required Python packages from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

    If you do not have a `requirements.txt`, create one with this content:

    ```
    requests
    ping3
    psutil
    ```

    Then run `pip install -r requirements.txt`.

-----

## Usage

### `stress.py` - Running Stress Tests

**Note**: This script may require root/administrator privileges to send packets effectively.

**TCP Flood Attack**

```bash
# Usage: python3 stress.py tcp <target_ip> <port> [-d DURATION] [-t THREADS]
python3 stress.py tcp 192.168.1.100 80 -d 120 -t 100
```

**UDP Flood Attack (with custom packet size)**

```bash
# Usage: python3 stress.py udp <target_ip> <port> [-d DURATION] [-t THREADS] [-s SIZE]
python3 stress.py udp 192.168.1.100 53 -d 120 -t 100 -s 1400
```

**HTTP Flood Attack**

```bash
# Usage: python3 stress.py http <target_url> [-d DURATION] [-t THREADS]
python3 stress.py http https://example.com -d 60 -t 50
```

### `monitor.py` - Monitoring & Alerting

This command will start monitoring, check connectivity to `1.1.1.1`, and trigger an alert if incoming traffic exceeds 2000 packets-per-second.

```bash
# Usage: python3 monitor.py [-i INTERVAL] [-d DURATION] [-o OUTPUT.csv] [--pps-threshold PPS] [--ping-target TARGET] [--http-target URL]

# Example:
python3 monitor.py -i 2 -d 3600 -o netlog.csv --pps-threshold 2000 --ping-target 1.1.1.1 --http-target https://my-service.com
```

**Example Console Output:**

```
Starting network monitoring for 3600 seconds...
Alerting when incoming PPS > 2000
Press Ctrl+C to stop early.
[2025-10-24 15:30:12] | In: 120.45 KB/s (85.5 pps) | Latency: 12.34 ms | Ping: Up | HTTP: Available
```

**Example Alert Output:**

```
!!!!!!!!!!!!!!!!!! HIGH TRAFFIC ALERT @ 2025-10-24 15:31:18 !!!!!!!!!!!!!!!!!!
  Incoming packets per second (2345) exceeded threshold of 2000
  This could indicate a potential network scan or a flood attack.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

-----

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
