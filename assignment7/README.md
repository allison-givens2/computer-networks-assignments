[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/dHbmPJkk)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21557697&assignment_repo_type=AssignmentRepo)
# CSC4200 — Assignment 7  
### UDP Fragmentation & Reassembly over Overlay  
**Total: 10 points**

---

## Objective

Extend your `PeerNode` overlay to support **large binary transfers** — for example, model deltas in a federated learning system.

You will:

- Fragment and send binary data across UDP (`≤ 60 KB` per packet)  
- Reassemble and verify data integrity using SHA-256  
- Use your existing `udp_overlay.PeerNode` for sending and receiving  

---

## Background

Your overlay currently supports small text messages.  
However, model updates can be much larger — up to hundreds of kilobytes.  
Since UDP packets have a size limit, large binary files must be **fragmented** and then **reassembled** by receivers.

This assignment simulates a distributed environment where peers exchange model updates using your UDP overlay.

---

## Learning Goals

- Implement **application-level fragmentation** for UDP  
- Implement **message-based reassembly** with integrity checks  
- Encode binary data using **Base64**  
- Integrate with the **peer-to-peer overlay network**

---

## Tasks (10 pts total)

| Function | Description | Points |
|-----------|--------------|--------|
| `fragment_and_send()` | Split a file into ≤ 60 KB Base64 chunks and send each via UDP. Print message headers for debugging. | 5 |
| `handle_incoming_chunk()` | Parse incoming chunks, reassemble in order, compute SHA-256, and verify integrity. Print headers and verification results. | 5 |

---

## Example Output

```
[INIT] Created delta v1762468120 (300000 bytes, 5 chunks)
[META] Announced v1762468120: 300000 bytes → 5 chunks

[STEP 3] Sending delta in fragments …
[SEND] TYPE=MODEL_CHUNK SRC=Pi-1 IDX=1/5
[SEND] TYPE=MODEL_CHUNK SRC=Pi-1 IDX=2/5
[SEND] TYPE=MODEL_CHUNK SRC=Pi-1 IDX=3/5
[SEND] TYPE=MODEL_CHUNK SRC=Pi-1 IDX=4/5
[SEND] TYPE=MODEL_CHUNK SRC=Pi-1 IDX=5/5

[STEP 4] Simulating receive and reassembly …
[RECV] TYPE=MODEL_CHUNK VER=v1762468120 IDX=1/5
[RECV] TYPE=MODEL_CHUNK VER=v1762468120 IDX=2/5
[RECV] TYPE=MODEL_CHUNK VER=v1762468120 IDX=3/5
[RECV] TYPE=MODEL_CHUNK VER=v1762468120 IDX=4/5
[RECV] TYPE=MODEL_CHUNK VER=v1762468120 IDX=5/5
[OK] SHA verified for v1762468120

[TEST DONE] ✔ All fragments received and verified
```

---

## Tips

* Always print message headers to debug fragmentation logic.
* Track received chunks using `node._model_buffers`.
* Reassemble in **correct order** before computing the SHA hash.
* Compare your computed SHA256 with the `MODEL_META` announcement.

---

## Grading Breakdown

| Criterion                        | Points     |
| -------------------------------- | ---------- |
| Correct fragmentation logic      | 3          |
| Proper message header & encoding | 2          |
| Correct reassembly order         | 3          |
| SHA verification correctness     | 2          |
| **Total**                        | **10 pts** |



