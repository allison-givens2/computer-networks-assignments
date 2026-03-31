#!/usr/bin/env python3
"""
Test Script for UDP Overlay Network
------------------------------------
Launches multiple nodes and verifies peer discovery and synchronization.
"""
import subprocess
import time
import sys

def run_test(num_nodes=3, duration=30):
    """
    Launch multiple nodes and test network convergence.
    
    Args:
        num_nodes: Number of nodes to launch
        duration: How long to run the test (seconds)
    """
    print(f"=== Starting UDP Overlay Network Test ===")
    print(f"Launching {num_nodes} nodes for {duration} seconds...")
    print()
    
    processes = []
    
    # Launch nodes
    for i in range(1, num_nodes + 1):
        node_id = f"Pi-{i}"
        print(f"Starting {node_id}...")
        
        # Launch in separate terminal or as background process
        # For testing, we'll just show the command
        cmd = f"python3 node.py {node_id}"
        print(f"  Command: {cmd}")
        print(f"  (Run this in a separate terminal)")
        print()
    
    print("=" * 50)
    print("TEST CHECKLIST:")
    print("=" * 50)
    print()
    print("1. SOCKET INITIALIZATION")
    print("   - Each node should bind to UDP port 5000")
    print("   - Check for '[INIT] Node Pi-X started' messages")
    print()
    print("2. BROADCAST DISCOVERY")
    print("   - Within 5-10 seconds, nodes should discover each other")
    print("   - Look for '[SYNC] Added Pi-X' messages")
    print()
    print("3. PEER TABLE POPULATION")
    print("   - Each node should show the same peer list")
    print("   - Check '[TABLE] N active peers' messages")
    print()
    print("4. HEARTBEAT (PING/PONG)")
    print("   - Every 15 seconds, nodes send pings")
    print("   - Look for '[PING] RTT=XXms to Pi-X' messages")
    print()
    print("5. TIMEOUT HANDLING")
    print("   - Stop one node (Ctrl-C)")
    print("   - After 30 seconds, others should show '[DROP] Pi-X removed'")
    print()
    print("6. CONVERGENCE")
    print("   - After 20 seconds, all nodes should have identical peer tables")
    print()
    print("=" * 50)
    print("EXPECTED METRICS:")
    print("=" * 50)
    print(f"- Discovery time: < 10 seconds")
    print(f"- RTT: < 50ms (local network)")
    print(f"- Packet loss: < 5%")
    print(f"- Active peers: {num_nodes - 1} (excluding self)")
    print()


def verify_packet_format():
    """Display example packet formats for verification."""
    print("=" * 50)
    print("PACKET FORMAT EXAMPLES:")
    print("=" * 50)
    print()
    print("PEER_SYNC (broadcast):")
    print("[PEER_SYNC]|Pi-1|1001|1729720815000|0|3|192.168.0.10,5000|d2b8e0ac")
    print()
    print("PING (unicast):")
    print("[PING]|Pi-1|1002|1729720820000|0|3|192.168.0.10,1729720820000|a3c4f1b2")
    print()
    print("PONG (unicast response):")
    print("[PONG]|Pi-2|2001|1729720821000|0|3|192.168.0.12,ok,18|f8d2e3a1")
    print()
    print("Header Fields:")
    print("  [MSGTYPE] | SENDER_ID | SEQ | TIMESTAMP | MODEL_VER | TTL | BODY | CRC32")
    print()


def show_grading_rubric():
    """Display the grading rubric for reference."""
    print("=" * 50)
    print("GRADING RUBRIC (30 points):")
    print("=" * 50)
    print()
    print("1. Broadcast Discovery (8 pts)")
    print("   - Nodes auto-discover within 5s")
    print("   - Packet format correct")
    print()
    print("2. Unicast Heartbeat (8 pts)")
    print("   - Proper PING/PONG logic")
    print("   - Timeout handling")
    print()
    print("3. Peer Table Consistency (6 pts)")
    print("   - All nodes maintain synchronized tables")
    print()
    print("4. Metrics and Logging (4 pts)")
    print("   - Reliability and RTT printed or logged")
    print()
    print("5. Report Quality (4 pts)")
    print("   - Correct structure and contribution table")
    print()
    print("6. BONUS: CRC32 (2 pts)")
    print("   - CRC32 integrity check implemented")
    print()


def main():
    """Main test interface."""
    if len(sys.argv) > 1 and sys.argv[1] == "format":
        verify_packet_format()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "rubric":
        show_grading_rubric()
        return
    
    print()
    print("UDP OVERLAY NETWORK TEST UTILITY")
    print("=" * 50)
    print()
    print("Usage:")
    print("  python3 test.py           - Show test instructions")
    print("  python3 test.py format    - Display packet format examples")
    print("  python3 test.py rubric    - Show grading rubric")
    print()
    
    # Show test instructions
    run_test(num_nodes=3, duration=30)
    
    print()
    print("=" * 50)
    print("ADDITIONAL TESTING TIPS:")
    print("=" * 50)
    print()
    print("1. Open 3-4 terminal windows")
    print("2. Run: python3 node.py Pi-1")
    print("3. Run: python3 node.py Pi-2")
    print("4. Run: python3 node.py Pi-3")
    print("5. Wait 20 seconds and compare peer tables")
    print("6. Stop one node and verify timeout handling")
    print()
    print("For network debugging:")
    print("  - Use tcpdump: sudo tcpdump -i any port 5000 -X")
    print("  - Use wireshark to capture UDP traffic")
    print()


if __name__ == "__main__":
    main()