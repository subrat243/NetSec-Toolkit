#!/usr/bin/env python3
import time
import psutil
import requests
from ping3 import ping
from datetime import datetime
import csv
import os
import argparse

class NetworkMonitor:
    def __init__(self, interval=5, output_file="network_stats.csv", pps_threshold=1000, ping_target="8.8.8.8", http_target="https://www.google.com"):
        self.interval = interval
        self.output_file = output_file
        self.headers_written = False
        self.last_stats = None
        # --- IMPROVEMENT: Alerting and Configuration ---
        self.pps_threshold = pps_threshold
        self.ping_target = ping_target
        self.http_target = http_target

    def get_network_stats(self):
        """Collects cumulative network statistics from psutil."""
        io = psutil.net_io_counters()
        return {
            'timestamp': time.time(),
            'bytes_sent': io.bytes_sent, 'bytes_recv': io.bytes_recv,
            'packets_sent': io.packets_sent, 'packets_recv': io.packets_recv,
            'err_in': io.errin, 'err_out': io.errout,
            'drop_in': io.dropin, 'drop_out': io.dropout
        }

    def save_stats(self, stats_to_save):
        """Saves a dictionary of statistics to the CSV file."""
        file_exists = os.path.isfile(self.output_file)
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=stats_to_save.keys())
            if not file_exists or not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            # Format timestamp for CSV
            stats_to_save['timestamp'] = datetime.fromtimestamp(stats_to_save['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(stats_to_save)

    def monitor(self, duration=3600):
        """Main monitoring loop with rate calculation and alerting."""
        start_time = time.time()
        end_time = start_time + duration

        print(f"Starting network monitoring for {duration} seconds...")
        print(f"Alerting when incoming PPS > {self.pps_threshold}")
        print("Press Ctrl+C to stop early.")

        try:
            while time.time() < end_time:
                current_stats = self.get_network_stats()
                
                # --- IMPROVEMENT: Calculate real-time rates ---
                rates = {}
                if self.last_stats:
                    elapsed = current_stats['timestamp'] - self.last_stats['timestamp']
                    if elapsed > 0:
                        rates['recv_kbps'] = (current_stats['bytes_recv'] - self.last_stats['bytes_recv']) / elapsed / 1024
                        sent_kbps = (current_stats['bytes_sent'] - self.last_stats['bytes_sent']) / elapsed / 1024
                        rates['recv_pps'] = (current_stats['packets_recv'] - self.last_stats['packets_recv']) / elapsed
                        sent_pps = (current_stats['packets_sent'] - self.last_stats['packets_sent']) / elapsed
                
                # Add other metrics
                latency = ping(self.ping_target, unit='ms')
                http_available = self._check_http_service()

                # --- IMPROVEMENT: Check for alerts ---
                if 'recv_pps' in rates:
                    self._check_alerts(rates)

                # Combine all data for display and saving
                display_data = {**current_stats, **rates, 'latency': latency, 'http_available': http_available}
                self.display_stats(display_data)
                self.save_stats(display_data)

                self.last_stats = current_stats
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        
        print("Monitoring completed.")

    def _check_http_service(self):
        try:
            return requests.get(self.http_target, timeout=5).status_code == 200
        except requests.RequestException:
            return False

    def _check_alerts(self, rates):
        """Checks calculated rates against defined thresholds."""
        if rates['recv_pps'] > self.pps_threshold:
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            alert_msg = (
                f"\n{'!'*10} HIGH TRAFFIC ALERT @ {timestamp_str} {'!'*10}\n"
                f"  Incoming packets per second ({rates['recv_pps']:.0f}) exceeded threshold of {self.pps_threshold}\n"
                f"  This could indicate a potential network scan or a flood attack.\n"
                f"{'!'*50}"
            )
            print(alert_msg)

    def display_stats(self, stats):
        """Displays current statistics in a readable format."""
        ts = datetime.fromtimestamp(stats['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        recv_kbps_str = f"{stats.get('recv_kbps', 0):.2f} KB/s"
        recv_pps_str = f"{stats.get('recv_pps', 0):.1f} pps"
        latency_str = f"{stats.get('latency', 0):.2f} ms" if stats.get('latency') is not None else "N/A"
        connectivity_str = "Up" if stats.get('latency') is not None else "Down"
        http_str = "Available" if stats.get('http_available') else "Unavailable"
        
        print(
            f"\r[{ts}] | In: {recv_kbps_str} ({recv_pps_str}) | Latency: {latency_str} | "
            f"Ping: {connectivity_str} | HTTP: {http_str}",
            end=""
        )

def main():
    parser = argparse.ArgumentParser(description="Network Monitoring and Alerting Tool")
    parser.add_argument('-i', '--interval', type=int, default=5, help='Monitoring interval in seconds')
    parser.add_argument('-d', '--duration', type=int, default=3600, help='Total monitoring duration in seconds')
    parser.add_argument('-o', '--output', default="network_stats.csv", help='Output CSV file name')
    # --- IMPROVEMENT: Command-line arguments for thresholds and targets ---
    parser.add_argument('--pps-threshold', type=int, default=2000, help='Incoming packets-per-second threshold for alerts')
    parser.add_argument('--ping-target', default="8.8.8.8", help='IP or domain to ping for connectivity checks')
    parser.add_argument('--http-target', default="https://www.google.com", help='URL to check for HTTP service availability')
    
    args = parser.parse_args()
    
    monitor = NetworkMonitor(
        interval=args.interval, 
        output_file=args.output,
        pps_threshold=args.pps_threshold,
        ping_target=args.ping_target,
        http_target=args.http_target
    )
    monitor.monitor(duration=args.duration)

if __name__ == "__main__":
    main()
