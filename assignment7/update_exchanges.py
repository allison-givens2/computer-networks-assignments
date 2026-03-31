python
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
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
    data = os.urandom(size_bytes)
    tmp.write(data)
    tmp.close()
    sha = hashlib.sha256(data).hexdigest()
    return tmp.name, sha, size_bytes


def announce_model_meta(node: PeerNode, ver: str, size: int, chunks: int, sha: str):
    body = f"ver={ver};size={size};chunks={chunks};sha256={sha}"
    pkt = node._make_packet("MODEL_META", body)
    node._send(pkt, (BROADCAST_IP, PORT))
    print(f"[META] Announced {ver}: {size} bytes → {chunks} chunks")


def fragment_and_send(node: PeerNode, ver: str, filepath: str, addr: Tuple[str, int]):
    with open(filepath, "rb") as f:
        data = f.read()

    total_chunks = (len(data) + MAX_UDP - 1) // MAX_UDP

    for idx in range(total_chunks):
        chunk = data[idx * MAX_UDP : (idx + 1) * MAX_UDP]
        b64 = base64.b64encode(chunk).decode()
        body = f"ver={ver};idx={idx};total={total_chunks};b64={b64}"
        pkt = node._make_packet("MODEL_CHUNK", body)
        node._send(pkt, addr)
        print(f"[SEND] TYPE=MODEL_CHUNK SRC={node.id} IDX={idx+1}/{total_chunks}")
    print(f"[DONE] Sent {total_chunks} chunks for {ver}")


def handle_incoming_chunk(node: PeerNode, msg: str, addr: Tuple[str, int]):
    parts = msg.split(";", 1)
    if len(parts) < 2:
        return
    header, body = parts
    fields = dict(field.split("=", 1) for field in body.split(";") if "=" in field)

    ver = fields.get("ver")
    idx = int(fields.get("idx", 0))
    total = int(fields.get("total", 0))
    b64_data = fields.get("b64")

    chunk_data = base64.b64decode(b64_data.encode())

    print(f"[RECV] VER={ver} IDX={idx+1}/{total}")

    if ver not in node._model_buffers:
        node._model_buffers[ver] = {"total": total, "parts": {}, "sha256": None}

    buf = node._model_buffers[ver]
    buf["parts"][idx] = chunk_data

    if len(buf["parts"]) == buf["total"]:
        ordered = [buf["parts"][i] for i in range(buf["total"])]
        assembled = b"".join(ordered)
        sha = hashlib.sha256(assembled).hexdigest()

        print(f"[OK] Reassembled model {ver} ({len(assembled)} bytes)")
        if buf.get("sha256") == sha:
            print(f"[OK] SHA verified: {sha}")
        else:
            print(f"[WARN] SHA mismatch: expected {buf.get('sha256')} got {sha}")

        tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".reassembled.bin")
        tmp_out.write(assembled)
        tmp_out.close()
        print(f"[SAVED] → {tmp_out.name}")

if __name__ == "__main__":
    node = PeerNode("Pi-1")
    node._model_buffers = {}

    path, sha, size = create_dummy_delta(300000)
    version = f"v{int(time.time())}"
    total_chunks = (size + MAX_UDP - 1) // MAX_UDP
    print(f"[INIT] Created delta {version} ({size} bytes, {total_chunks} chunks)")

    announce_model_meta(node, version, size, total_chunks, sha)
    node._model_buffers[version] = {"total": total_chunks, "parts": {}, "sha256": sha}

    print("\n[STEP 3] Sending delta in fragments …")
    fragment_and_send(node, version, path, (BROADCAST_IP, PORT))

    print("\n[STEP 4] Simulating receive and reassembly …")
    with open(path, "rb") as f:
        data = f.read()
    total = (len(data) + MAX_UDP - 1) // MAX_UDP
    for i in range(total):
        part = data[i * MAX_UDP : (i + 1) * MAX_UDP]
        b64 = base64.b64encode(part).decode()
        body = f"ver={version};idx={i};total={total};b64={b64}"
        msg = node._make_packet("MODEL_CHUNK", body)
        header = f"[RECV] TYPE=MODEL_CHUNK VER={version} IDX={i+1}/{total}"
        print(header)
        handle_incoming_chunk(node, msg, ("127.0.0.1", PORT))

    print("\n[TEST DONE] If implemented correctly, you should see:")
    print("  • '[SEND]' logs for each fragment")
    print("  • '[RECV]' header lines showing chunk numbers")
    print("  • '[OK] SHA verified' once all chunks received")

