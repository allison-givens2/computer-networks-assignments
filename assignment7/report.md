### Decentralized Chatbot: UDP Networking & Overlay Foundation

---

## 1. What We Worked On

| Name | Task / Component | Description of Work |
|------|------------------|---------------------|
| Student 1 | Networking Setup | Configured UDP socket, tested broadcast, implemented base message structure |
| Student 2 | Peer Table Logic | Handled parsing of PEER_SYNC, maintained liveness timestamps |
| Student 3 | Logging & Analysis | Collected RTT, packet counts, verified discovery timing |

*(Each member must fill in their own contributions.)*

---

## 2. Observations

- **Nodes discovered:**  
- **Average discovery time:** ___ seconds  
- **Average RTT between peers:** ___ ms  
- **Packet loss rate (approx.):** ___ %  
- **Peer tables converged after:** ___ seconds  

**Example Log Snippet**
```

[SYNC] Pi-2 joined (192.168.0.12)
[PING] RTT=21ms
[TABLE] 3 active peers

```

**Summary:**  
Describe how the network behaved — stability, timing, convergence, and any unexpected results.

---

## 3. Problems and Fixes

| Issue | Cause | Resolution / Next Step |
|--------|--------|-----------------------|
| Broadcast not received | Firewall blocking UDP broadcast | Disabled local firewall and retested |
| Duplicate entries | Missing self-filter check | Added condition to ignore own ID |
| Timeouts too short | Ping interval < network delay | Increased timeout to 3 seconds |

Summarize any persistent or unresolved issues.

---

## 4. Notes / Future Work

- Planned improvements for Assignment 2 (e.g., ACK/NACK, message ordering).  
- Additional metrics to log for trust and reliability analysis later.

