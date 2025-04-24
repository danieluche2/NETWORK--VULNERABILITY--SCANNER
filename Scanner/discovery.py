import ipaddress
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from .config import PING_TIMEOUT, THREADS

class NetworkDiscovery:
    def __init__(self):
        self.timeout = PING_TIMEOUT
        self.max_threads = THREADS
    
    def discover(self, target):
        """Discover live hosts in a network range"""
        try:
            if '/' in target:  # CIDR notation
                return self.scan_network(target)
            elif '-' in target:  # IP range
                return self.scan_ip_range(target)
            else:  # Single IP
                return [target] if self.host_alive(target) else []  # Changed from is_host_alive to host_alive
        except Exception as e:
            raise ValueError(f"Invalid target format: {target}. Error: {e}") from e
    
    def scan_network(self, cidr):
        """Scan all IPs in a CIDR range"""
        network = ipaddress.ip_network(cidr, strict=False)
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            results = executor.map(self.host_alive, network.hosts())  # Changed here too
            return [str(ip) for ip, alive in zip(network.hosts(), results) if alive]
    
    def host_alive(self, ip):  # This is the correct method name
        """Check if a host is alive using ICMP ping"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', str(self.timeout), str(ip)]
        return subprocess.call(command, stdout=subprocess.DEVNULL) == 0