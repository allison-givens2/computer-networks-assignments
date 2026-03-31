#!/usr/bin/env python3
"""
Assignment 7 — UDP Fragmentation & Reassembly over Overlay
-----------------------------------------------------------
Goal:
    Extend your PeerNode overlay to handle large binary transfers
    (e.g., model deltas).
"""

import os
import time
import base64
import hashlib
import tempfile
from typing import Tuple

from udp_overlay import PeerNode, BROADCAST_IP, PORT

MAX_UDP = 60000


def create_dummy_delta(size_bytes: int = 300000) -> Tuple[str, str, int]:
    """Create a dummy binary file for testing fragmentation."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
    data = os.urandom(size_bytes)
    tmp.write(data)
    tmp.close()
    sha = hashlib.sha256(data).hexdigest()
    return tmp.name, sha, size_bytes


def announce_model_meta(node: PeerNode, ver: str, size: int, chunks: int, sha: str):
    """Announce model metadata to the network."""
    body = f"ver={ver};size={size};chunks={chunks};sha256={sha}"
    pkt = node._make_packet("MODEL_META", body)
    node._send(pkt, (BROADCAST_IP, PORT))
    print(f"[META] Announced {ver}: {size} bytes → {chunks} chunks")


def fragment_and_send(node: PeerNode, ver: str, filepath: str, addr: Tuple[str, int]):
    """
    Fragment a binary file into chunks and send via UDP.
    
    Args:
        node: PeerNode instance for sending packets
        ver: Version identifier for this model delta
        filepath: Path to the binary file to send
        addr: Destination address (ip, port) tuple
    
    Points: 5
    - Correct fragmentation logic (3 pts)
    - Proper message header & encoding (2 pts)
    """
    # Read the entire file into memory
    with open(filepath, "rb") as f:
        data = f.read()
    
    # Calculate total number of chunks needed
    # Each chunk can be up to MAX_UDP bytes
    total_chunks = (len(data) + MAX_UDP - 1) // MAX_UDP
    
    # Fragment and send each chunk
    for idx in range(total_chunks):
        # Extract the chunk for this index
        start_offset = idx * MAX_UDP
        end_offset = min((idx + 1) * MAX_UDP, len(data))
        chunk = data[start_offset:end_offset]
        
        # Encode chunk as Base64 for safe transmission over UDP
        b64 = base64.b64encode(chunk).decode('utf-8')
        
        # Build message body with metadata
        body = f"ver={ver};idx={idx};total={total_chunks};b64={b64}"
        
        # Create packet using PeerNode's packet format
        pkt = node._make_packet("MODEL_CHUNK", body)
        
        # Send the packet to the destination
        node._send(pkt, addr)
        
        # Print debug header (1-indexed for readability)
        print(f"[SEND] TYPE=MODEL_CHUNK SRC={node.id} IDX={idx+1}/{total_chunks}")
    
    print(f"[DONE] Sent {total_chunks} chunks for {ver}")


def handle_incoming_chunk(node: PeerNode, msg: str, addr: Tuple[str, int]):
    """
    Parse and reassemble incoming MODEL_CHUNK messages.
    
    Args:
        node: PeerNode instance (used for accessing _model_buffers)
        msg: Raw packet string received
        addr: Source address (ip, port) tuple
    
    Points: 5
    - Correct reassembly order (3 pts)
    - SHA verification correctness (2 pts)
    """
    # Parse the message to extract header and body
    # Message format: [TYPE]|SENDER|SEQ|TIMESTAMP|MODEL_VER|TTL|BODY|CRC
    parts = msg.split("|")
    if len(parts) < 7:
        print(f"[ERROR] Malformed MODEL_CHUNK packet")
        return
    
    # Extract body (everything between TTL and CRC)
    # Body starts at index 6, CRC is the last element
    body = "|".join(parts[6:-1])
    
    # Parse body fields (format: ver=...;idx=...;total=...;b64=...)
    fields = {}
    for field in body.split(";"):
        if "=" in field:
            key, value = field.split("=", 1)
            fields[key] = value
    
    # Extract metadata
    ver = fields.get("ver")
    idx = int(fields.get("idx", 0))
    total = int(fields.get("total", 0))
    b64_data = fields.get("b64")
    
    if not ver or b64_data is None:
        print(f"[ERROR] Missing required fields in MODEL_CHUNK")
        return
    
    # Decode Base64 chunk back to binary
    try:
        chunk_data = base64.b64decode(b64_data.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Failed to decode Base64 data: {e}")
        return
    
    # Print receive header (1-indexed for readability)
    print(f"[RECV] VER={ver} IDX={idx+1}/{total}")
    
    # Initialize buffer for this version if it doesn't exist
    if ver not in node._model_buffers:
        node._model_buffers[ver] = {
            "total": total,
            "parts": {},
            "sha256": None
        }
    
    # Store the chunk in the buffer
    buf = node._model_buffers[ver]
    buf["parts"][idx] = chunk_data
    
    # Check if all chunks have been received
    if len(buf["parts"]) == buf["total"]:
        # Reassemble in correct order (CRITICAL: must be sorted by index)
        ordered = [buf["parts"][i] for i in range(buf["total"])]
        assembled = b"".join(ordered)
        
        # Compute SHA-256 hash of the reassembled data
        sha = hashlib.sha256(assembled).hexdigest()
        
        print(f"[OK] Reassembled model {ver} ({len(assembled)} bytes)")
        
        # Verify SHA-256 if we have the expected hash
        if buf.get("sha256"):
            if buf["sha256"] == sha:
                print(f"[OK] SHA verified: {sha}")
            else:
                print(f"[WARN] SHA mismatch: expected {buf.get('sha256')} got {sha}")
        else:
            # No expected hash provided, just report what we got
            print(f"[INFO] Computed SHA: {sha}")
        
        # Save the reassembled file to disk
        tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".reassembled.bin")
        tmp_out.write(assembled)
        tmp_out.close()
        print(f"[SAVED] → {tmp_out.name}")


if __name__ == "__main__":
    # Initialize node
    node = PeerNode("Pi-1")
    node._model_buffers = {}
    
    # Step 1: Create a dummy delta file
    path, sha, size = create_dummy_delta(300000)
    version = f"v{int(time.time())}"
    total_chunks = (size + MAX_UDP - 1) // MAX_UDP
    print(f"[INIT] Created delta {version} ({size} bytes, {total_chunks} chunks)")
    
    # Step 2: Announce metadata
    announce_model_meta(node, version, size, total_chunks, sha)
    node._model_buffers[version] = {"total": total_chunks, "parts": {}, "sha256": sha}
    
    # Step 3: Send delta in fragments
    print(f"\n[STEP 3] Sending delta in fragments …")
    fragment_and_send(node, version, path, (BROADCAST_IP, PORT))
    
    # Step 4: Simulate receive and reassembly
    print(f"\n[STEP 4] Simulating receive and reassembly …")
    with open(path, "rb") as f:
        data = f.read()
    total = (len(data) + MAX_UDP - 1) // MAX_UDP
    
    for i in range(total):
        part = data[i * MAX_UDP : (i + 1) * MAX_UDP]
        b64 = base64.b64encode(part).decode()
        body = f"ver={version};idx={i};total={total};b64={b64}"
        msg = node._make_packet("MODEL_CHUNK", body)
        
        # Print the expected header format
        print(f"[RECV] TYPE=MODEL_CHUNK VER={version} IDX={i+1}/{total}")
        
        # Process the chunk
        handle_incoming_chunk(node, msg, ("127.0.0.1", PORT))
    
