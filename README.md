<div align="center">
  <img src="assets/banner.svg" alt="VADER - Brother Program of Maul" width="100%"/>
</div>

---

### *By a Star Wars Nerd*

> **"I find your lack of security disturbing."** - Darth Vader

A memory-efficient mass IP scanner designed to map entire countries, ASNs, and IP blocks for network reconnaissance and security research.

## Overview

Vader scans massive IP ranges by breaking them into blocks and processing one block at a time. Each block gets its own dynamically-sized BloomFilter to prevent duplicate scans while keeping memory usage minimal. This allows you to scan entire countries without running out of RAM.

## Key Features

- **Country-based scanning** - Map all IPs within a specific country
- **ASN filtering** - Target specific autonomous systems within countries
- **Memory-efficient** - Iterates through IP blocks one at a time without loading all addresses into memory
- **Multi-threaded** - High-performance concurrent scanning (default: 250 threads)
- **Deduplication** - BloomFilter prevents scanning the same IP twice in global (non-country) mode
- **GeoIP lookup** - Optional geolocation via local MaxMind DB or ipinfo.io API
- **Device presets** - Built-in port lists for cameras, IoT, routers, NAS, databases, and remote access

## How It Works

1. Loads all IP blocks for the target country/ASN
2. Processes blocks sequentially (pops from queue)
3. Iterates through each block's IPs using a lazy iterator (no full list in memory)
4. Scans target ports via TCP connect on each IP
5. When a block is exhausted, moves to the next one
6. Tracks progress: scanned IPs, active IPs, blocks completed

For global scans (no `--country`), random IPs are generated and deduplicated with a BloomFilter (default capacity: 100M, configurable with `--bloom-size`).

## Installation

```bash
git clone https://github.com/nsm-barii/vader.git
cd vader/src
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Scan entire country
```bash
sudo venv/bin/python main.py --country Iran -p 80 -t 500
```

### Scan specific ASNs within country
```bash
sudo venv/bin/python main.py --country Iran --asn 44244 -p 22,80,443
sudo venv/bin/python main.py --country Iran --asn "215892,214735,214145" -p 80
```

### Save results
```bash
sudo venv/bin/python main.py --country Iran -p 8080 --save
```

## Options

```
-p PORT              Port(s) to scan (comma-separated)
-t THREADS           Max threads (default: 250)
--save               Save active IPs to database/saved_ips
--x NAME             Custom filename for saved IPs
--country NAME       Target country (e.g., Iran, China, Russia)
--asn NUMBERS        Filter by ASN (comma-separated, e.g., 215892,214735)
--bloom-size SIZE    BloomFilter capacity for global scans (default: 100000000)
--geo [local|ipinfo] Enable IP geolocation lookup
--ipinfo KEY         ipinfo.io API key (optional)
--paths [nas|router|camera]  Set directory bruteforce wordlist
--show-all           Display all active IPs found
```

## Preset Port Modes

```bash
--camera     # IP cameras (RTSP, ONVIF, web interfaces)
--iot        # IoT devices (MQTT, CoAP, mDNS)
--router     # Routers (admin panels, SSH, Telnet)
--nas        # NAS devices (SMB, Synology, web panels)
--remote     # Remote access (RDP, VNC, SSH, FTP)
--database   # Databases (MySQL, PostgreSQL, MongoDB, Redis)
```

## About

Created by **NSM-Barii** - Star Wars nerd | Cybersecurity enthusiast

**NSM Toolset:**
- **Vader** - Recon & discovery (this tool)
- **Maul** - Infrastructure mapping ([github.com/nsm-barii/maul](https://github.com/nsm-barii/maul))

---

## Disclaimer

For authorized security testing and research only. Unauthorized network scanning may be illegal in your jurisdiction. Users are responsible for obtaining proper permissions.

MIT License
