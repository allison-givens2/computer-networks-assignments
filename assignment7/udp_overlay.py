#!/usr/bin/env python3
"""
UDP Overlay Networking Implementation
------------------------------------------------
Implements decentralized peer discovery and heartbeat protocol
for distributed chatbot system.
"""
import socket
import threading
import time
import binascii
import struct

# ---------- Global Configuration ----------
PORT = 5000
BROADCAST_IP = "255.255.255.255"
SYNC_INTERVAL = 5
PING_INTERVAL = 15
PING_TIMEOUT = 3
REMOVE_TIMEOUT = 30


class PeerNode:
    """
    Represents a single node in the decentralized chatbot overlay.
    Implements UDP broadcast discovery and heartbeat logic.
    """
    
    def __init__(self, node_id: str):
        """Initialize node state, socket, and peer table."""
        self.id = node_id
        self.ip = None
        self.port = PORT
        self.seq = 0
        self.sock = None
        self.peers = {}  # {peer_id: {"ip":..., "port":..., "last_seen":..., "status":...}}
        self.running = False
        self.lock = threading.Lock()
        self.ping_sent = {}  # Track ping timestamps for RTT calculation
        
        # Initialize socket and get local IP
        self._setup_socket()
        self.ip = self._get_local_ip()
        print(f"[INIT] Node {self.id} started on {self.ip}:{self.port}")

    # ---------- Setup ----------
    
    def _setup_socket(self):
        """Create and configure UDP socket for broadcast and unicast."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('', PORT))
        self.sock.settimeout(1.0)  # Non-blocking with timeout
    
    def _get_local_ip(self):
        """Return the local IP address of this host."""
        try:
            # Create a temporary socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    # ---------- Message Handling ----------
    
    def _next_seq(self):
        """Increment and return the next sequence number."""
        with self.lock:
            self.seq += 1
            return self.seq
    
    def _calculate_crc32(self, data: str) -> str:
        """Calculate CRC32 checksum for data."""
        crc = binascii.crc32(data.encode()) & 0xffffffff
        return f"{crc:08x}"
    
    def _make_packet(self, msgtype: str, body: str) -> str:
        """Build packet string according to format spec."""
        timestamp = int(time.time() * 1000)  # Unix epoch in milliseconds
        seq = self._next_seq()
        
        # Header format: [MSGTYPE]|SENDER_ID|SEQ_ID|TIMESTAMP|MODEL_VER|TTL
        header = f"[{msgtype}]|{self.id}|{seq}|{timestamp}|0|3"
        
        # Complete message without CRC
        msg_without_crc = f"{header}|{body}"
        
        # Calculate CRC32
        crc = self._calculate_crc32(msg_without_crc)
        
        # Final packet
        packet = f"{msg_without_crc}|{crc}"
        return packet
    
    def _verify_crc32(self, packet: str) -> bool:
        """Verify CRC32 checksum of received packet."""
        try:
            parts = packet.rsplit('|', 1)
            if len(parts) != 2:
                return False
            
            msg_without_crc = parts[0]
            received_crc = parts[1]
            
            calculated_crc = self._calculate_crc32(msg_without_crc)
            return calculated_crc == received_crc
        except Exception:
            return False
    
    # def _send(self, data: str, addr: tuple):
    #     """Send encoded UDP packet to destination."""
    #     try:
    #         self.sock.sendto(data.encode(), addr)
    #     except Exception as e:
    #         print(f"[ERROR] Failed to send to {addr}: {e}")

    def _send(self, data: str, addr: tuple):
        """Send encoded UDP packet to destination."""
        try:
            self.sock.sendto(data.encode(), addr)
        except Exception as e:
            # Suppress broadcast errors - they don't affect the assignment logic
            if "Message too long" not in str(e):
                print(f"[ERROR] Failed to send to {addr}: {e}")

    # ---------- Overlay Operations ----------
    
    def broadcast_sync(self):
        """Broadcast [PEER_SYNC] message to announce presence."""
        body = f"{self.ip},{self.port}"
        packet = self._make_packet("PEER_SYNC", body)
        self._send(packet, (BROADCAST_IP, PORT))
    
    def send_ping(self, peer_id: str, peer_info: dict):
        """Send [PING] message to a specific peer."""
        timestamp = int(time.time() * 1000)
        body = f"{self.ip},{timestamp}"
        packet = self._make_packet("PING", body)
        
        peer_addr = (peer_info["ip"], peer_info["port"])
        self._send(packet, peer_addr)
        
        # Track ping time for RTT calculation
        with self.lock:
            self.ping_sent[peer_id] = timestamp
    
    def send_pong(self, addr: tuple, ping_timestamp: int):
        """Send [PONG] message back to sender."""
        current_time = int(time.time() * 1000)
        rtt = current_time - ping_timestamp
        body = f"{self.ip},ok,{rtt}"
        packet = self._make_packet("PONG", body)
        self._send(packet, addr)
    
    def handle_message(self, msg: str, addr: tuple):
        """Parse and process incoming UDP packet."""
        try:
            # Verify CRC32
            if not self._verify_crc32(msg):
                print(f"[ERROR] Invalid CRC from {addr}")
                return
            
            # Remove CRC for parsing
            msg_without_crc = msg.rsplit('|', 1)[0]
            
            # Split header and body
            parts = msg_without_crc.split('|')
            if len(parts) < 7:
                print(f"[ERROR] Malformed packet from {addr}")
                return
            
            msgtype = parts[0].strip('[]')
            sender_id = parts[1]
            seq_id = parts[2]
            timestamp = parts[3]
            body = '|'.join(parts[6:])
            
            # Ignore self-messages
            if sender_id == self.id:
                return
            
            current_time = time.time()
            
            # Handle different message types
            if msgtype == "PEER_SYNC":
                self._handle_peer_sync(sender_id, body, addr, current_time)
            
            elif msgtype == "PING":
                self._handle_ping(sender_id, body, addr, current_time)
            
            elif msgtype == "PONG":
                self._handle_pong(sender_id, body, current_time)
        
        except Exception as e:
            print(f"[ERROR] Failed to handle message from {addr}: {e}")
    
    def _handle_peer_sync(self, sender_id: str, body: str, addr: tuple, current_time: float):
        """Handle PEER_SYNC message."""
        try:
            ip, port = body.split(',')
            port = int(port)
            
            with self.lock:
                if sender_id not in self.peers:
                    self.peers[sender_id] = {
                        "ip": ip,
                        "port": port,
                        "last_seen": current_time,
                        "status": "active"
                    }
                    print(f"[SYNC] Added {sender_id} ({ip})")
                else:
                    self.peers[sender_id]["last_seen"] = current_time
                    self.peers[sender_id]["status"] = "active"
        
        except Exception as e:
            print(f"[ERROR] Failed to parse PEER_SYNC: {e}")
    
    def _handle_ping(self, sender_id: str, body: str, addr: tuple, current_time: float):
        """Handle PING message."""
        try:
            parts = body.split(',')
            ping_timestamp = int(parts[1])
            
            # Update peer's last_seen time
            with self.lock:
                if sender_id in self.peers:
                    self.peers[sender_id]["last_seen"] = current_time
            
            # Send PONG response
            self.send_pong(addr, ping_timestamp)
        
        except Exception as e:
            print(f"[ERROR] Failed to handle PING: {e}")
    
    def _handle_pong(self, sender_id: str, body: str, current_time: float):
        """Handle PONG message."""
        try:
            parts = body.split(',')
            rtt = int(parts[2])
            
            with self.lock:
                if sender_id in self.peers:
                    self.peers[sender_id]["last_seen"] = current_time
                    self.peers[sender_id]["status"] = "active"
            
            print(f"[PING] RTT={rtt}ms to {sender_id}")
        
        except Exception as e:
            print(f"[ERROR] Failed to handle PONG: {e}")

    # ---------- Thread Tasks ----------
    
    def listener(self):
        """Continuously listen for incoming packets."""
        print(f"[LISTENER] Started")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = data.decode()
                self.handle_message(msg, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Listener error: {e}")
        print(f"[LISTENER] Stopped")
    
    def broadcaster(self):
        """Periodically broadcast PEER_SYNC messages."""
        print(f"[BROADCASTER] Started")
        while self.running:
            self.broadcast_sync()
            time.sleep(SYNC_INTERVAL)
        print(f"[BROADCASTER] Stopped")
    
    def heartbeat(self):
        """Send pings and remove inactive peers."""
        print(f"[HEARTBEAT] Started")
        while self.running:
            time.sleep(PING_INTERVAL)
            
            current_time = time.time()
            peers_to_remove = []
            
            with self.lock:
                # Send pings to all active peers
                for peer_id, peer_info in list(self.peers.items()):
                    # Check if peer is inactive
                    if current_time - peer_info["last_seen"] > REMOVE_TIMEOUT:
                        peers_to_remove.append(peer_id)
                    else:
                        # Send ping
                        self.send_ping(peer_id, peer_info)
                
                # Remove inactive peers
                for peer_id in peers_to_remove:
                    del self.peers[peer_id]
                    print(f"[DROP] {peer_id} removed (timeout)")
        
        print(f"[HEARTBEAT] Stopped")
    
    def summary(self):
        """Print peer-table summary periodically."""
        print(f"[SUMMARY] Started")
        while self.running:
            time.sleep(10)
            with self.lock:
                active_count = len([p for p in self.peers.values() if p["status"] == "active"])
                print(f"[TABLE] {active_count} active peers")
                
                if self.peers:
                    print("[TABLE] Peer list:")
                    for peer_id, info in self.peers.items():
                        print(f"  - {peer_id}: {info['ip']}:{info['port']} (last_seen: {int(time.time() - info['last_seen'])}s ago)")
        
        print(f"[SUMMARY] Stopped")

    # ---------- Control ----------
    
    def start(self):
        """Start listener, broadcaster, heartbeat, and summary threads."""
        self.running = True
        
        # Start all threads
        threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.broadcaster, daemon=True).start()
        threading.Thread(target=self.heartbeat, daemon=True).start()
        threading.Thread(target=self.summary, daemon=True).start()
        
        print(f"[START] Node {self.id} is running")
    
    def stop(self):
        """Stop all threads and close socket."""
        print(f"[STOP] Shutting down node {self.id}...")
        self.running = False
        time.sleep(2)  # Give threads time to finish
        
        if self.sock:
            self.sock.close()
        
        print(f"[STOP] Node {self.id} stopped successfully")


# ---------- Entry Point ----------
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python node.py <node_id>")
        print("Example: python node.py Pi-1")
        exit(1)
    
    node_id = sys.argv[1]
    node = PeerNode(node_id)
    node.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()
        print("\n[EXIT] Node stopped.")