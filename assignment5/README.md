[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4awjcTfj)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20951284&assignment_repo_type=AssignmentRepo)
# Assignment: AIMD Reliable File Transfer over UDP

## Objective
Implement reliable file transfer over UDP using AIMD (Additive Increase / Multiplicative Decrease) congestion control.  
You will extend the provided skeleton client and server to handle:
- Reliable delivery despite packet loss
- Dynamic window-based transmission
- Additive window growth and multiplicative reduction
- Retransmissions for dropped packets
- Final checksum verification before writing the file

---

## Packet Format
| Field | Size | Description |
|-------|------|-------------|
| MAGIC | 2B | Constant `0xC0DE` |
| VER | 1B | Protocol version (1) |
| TYPE | 1B | `0=DATA`, `1=ACK` |
| SEQ | 4B | Sequence number |
| LEN | 2B | Payload length ≤ 1000 |
| CHK | 4B | CRC32 of header+payload |
| FCHK | 4B | File checksum (last packet only) |

### Byte Layout

Normal packet:
[MAGIC|VER|TYPE|SEQ|LEN|CHK|DATA]
Final packet:
[MAGIC|VER|TYPE|SEQ|LEN|CHK|DATA|FCHK]


---

## Client (UDPClient)
You will implement the AIMD sending algorithm in `client.py`.

### Steps
1. Split the file into 1000-byte chunks.
2. Create packets with `Packet.create(seq, chunk, TYPE_DATA)`.
3. Send up to `window` packets at a time (initially `window=1`).
4. Wait for ACKs from the server.
5. Apply AIMD control:
   - Additive Increase: Increase `window += 1` after successful round (all ACKed).
   - Multiplicative Decrease: On timeout or missing ACKs, reduce. Use ssthreshold, max of 1 or window//2.
   - If you don't use ssthresh, you will end up with window size in fraction. Not fun.
6. Retransmit unacknowledged packets after timeout or loss.
7. Repeat until all packets are acknowledged.
8. Validate and print that transfer finished successfully.
9. (Optional) If the `--plot` flag is provided, record and plot window size per round.

---

## Server (UDPServer)
You will implement the server logic in `server.py`.

### Steps
1. Receive incoming packets and parse them using `Packet.parse`.
2. Store each chunk in a buffer, keyed by sequence number.
3. Drop ACKs randomly based on `loss_rate` to simulate network loss:
4. Send ACKs for received packets.
5. Detect final packet (one with FCHK).
6. Concatenate all chunks in order.
7. Verify file checksum.
8. Reset buffer after successful or failed verification.
