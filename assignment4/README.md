[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zHILemQe)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20878661&assignment_repo_type=AssignmentRepo)
# Assignment: Reliable File Transfer with Retransmissions over UDP

## Objective
Implement a reliable file transfer protocol on top of UDP.  
You will extend the provided skeleton client and server to handle:  
- Packet loss (simulated in the server)  
- Retransmissions (implemented in the client)  
- Final checksum validation before writing the file  

---

## Packet Format

### Header (always present)
| Field | Size | Description |
|-------|------|-------------|
| MAGIC | 2B   | Constant `0xC0DE` |
| VER   | 1B   | Protocol version (`1`) |
| TYPE  | 1B   | `0=DATA`, `1=ACK` |
| SEQ   | 4B   | Sequence number (starts at 0, increments per packet) |
| LEN   | 2B   | Payload length (≤ 1000 bytes) |
| CHK   | 4B   | CRC32 of header + payload |

### Extra (last packet only)
| Field | Size | Description |
|-------|------|-------------|
| FCHK  | 4B   | CRC32 of the entire file |

### Payload
- **DATA packets**: up to 1000 bytes of file data  
- **ACK packets**: empty payload  

### Byte Layout
```

Normal packet:
+--------+-----+------+----------+------+----------+----------------+
| MAGIC  | VER | TYPE |   SEQ    | LEN  |   CHK    |   [Payload]   |
|  2B    | 1B  | 1B   |   4B     | 2B   |   4B     |   LEN bytes   |
+--------+-----+------+----------+------+----------+----------------

Final packet only:
+--------+-----+------+----------+------+----------+----------------+---------+
| MAGIC  | VER | TYPE |   SEQ    | LEN  |   CHK    |   [Payload]   |  FCHK   |
|  2B    | 1B  | 1B   |   4B     | 2B   |   4B     |   LEN bytes   |   4B    |
+--------+-----+------+----------+------+----------+----------------+---------+

````

---

## Steps

### Client
1. Split file into 1000-byte chunks.  
2. Create packets with `Packet.create`.  
3. Include `FCHK` in the last packet.  
4. Send packets sequentially.  
5. Wait for an ACK (`TYPE_ACK`, matching `SEQ`).  
6. Use **packet-level timeout** (via `time.time()`, not `socket.settimeout`).  
7. Retransmit up to `N` times, else raise `RuntimeError`.  

### Server
1. Simulate packet loss with probability `loss_rate`.  
2. Buffer received chunks by sequence number.  
3. Send an ACK for each successfully received packet.  
4. On the final packet:  
   - Concatenate all buffered data  
   - Verify against `FCHK`  
   - If match → write file to disk  
   - Else → discard buffer  

---

## Tests

### Public (student-visible)
1. Client/server basic communication  
2. Packet header parsing works  
3. Sequence numbers are correct  
4. Retransmission triggers on loss  
5. Final checksum is validated  
6. Client uses packet-level timeout (not just `socket.settimeout`)  

### Private (grading only, hints)
1. High loss rate (0.5) still delivers  
2. Missing ACK triggers retry  
3. Large file (>1 MB) transfer works  
4. Corrupted packet is retransmitted  
5. Max retries exceeded → raises `RuntimeError`  
6. Delayed ACK handled correctly  

---

## Rubric (10 pts)
- Packet format correct — 2  
- Server simulates loss + sends ACKs — 2  
- Client retransmission with packet-level timers — 2  
- Final checksum validated — 2  
- Works under high loss and large files — 2  

---

## Tips
- Compute checksum:  
  ```python
  zlib.crc32(data) & 0xFFFFFFFF
- Implement stop-and-wait ARQ (one packet at a time).
- Use `time.time()` to manage per-packet timers.
- Do **not** modify `packet.py`.
- Public tests will fail until you implement the TODOs.


