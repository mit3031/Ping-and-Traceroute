# Homework 2 – Ping and Traceroute

## Overview

The project includes:

- `my_ping.py` – Sends ICMP Echo Request packets and measures round trip time
- `my_traceroute.py` – Sends UDP probes with increasing TTL values and listens for ICMP responses to discover intermediate routers

Both programs manually construct or process ICMP packets using raw sockets

---


# Running The program

## my_ping.py

This program sends ICMP Echo Request packets to a destination host and waits for ICMP Echo Replies

### Basic Usage

```bash
sudo python3 my_ping.py <destination>
```

Example:

```bash
sudo python3 my_ping.py google.com
```

---

### Command Line Options

- `-c`, `--count`  
  Stop after sending a specific number of packets

- `-i`, `--wait`  
  Time to wait between sending packets  
  Default: 1 second

- `-s`, `--packetsize`  
  Number of data bytes to send in each ICMP packet  
  Default: 56 bytes

- `-t`, `--timeout`  
  Timeout in seconds before a request is considered lost  
  Default: 2 seconds

---

### Example Commands

Send 4 packets with a 0.5 second interval:

```bash
sudo python3 my_ping.py google.com -c 4 -i 0.5
```

Send packets with a custom payload size:

```bash
sudo python3 my_ping.py 8.8.8.8 -s 100
```

Run with a timeout of 5 seconds:

```bash
sudo python3 my_ping.py google.com -t 5
```

---

## my_traceroute.py

This discovers the route to a destination by sending UDP probes with increasing TTL values. When a router drops a packet because TTL reaches 0, it sends back an ICMP time exceeded message. This allows the program to identify each hop along the path

The maximum hop count is 30

---

### Basic Usage

```bash
sudo python3 my_traceroute.py <destination>
```

Example:

```bash
sudo python3 my_traceroute.py google.com
```

---

### Command Line Options

- `-n`  
  Display hop IP addresses numerically only

- `-q`, `--nqueries`  
  Number of probes to send per hop 
  
  Default: 3

- `-S`, `--summary`  
  Display how many probes were unanswered per hop

---

### Example Commands

Standard traceroute:

```bash
sudo python3 my_traceroute.py google.com
```

Traceroute with numeric output and 2 probes per hop:

```bash
sudo python3 my_traceroute.py 8.8.8.8 -n -q 2
```

Traceroute with summary of lost probes:

```bash
sudo python3 my_traceroute.py google.com -S
```

