# ASSIGNMENT 2: Computer Networks
## DNS Query Resolution

**Authors:** A. V. S. Manoj (23110025) & N. Eshwar Karthikeya (23110215)  
**Course:** CS 331 - Computer Networks  
**Date:** October 28, 2025

---

## Overview

This assignment implements and analyzes DNS resolution using both direct NAT-based queries and a custom DNS resolver with caching capabilities. The project demonstrates DNS resolution mechanics, caching optimization, and network traffic analysis using Mininet.

**Key Achievements:**
- Simulated DNS topology in Mininet with successful connectivity
- Extracted 400 unique DNS queries from 4 PCAP files (100 per file)
- Implemented custom DNS resolver using dnsmasq on host 10.0.0.5
- Demonstrated DNS caching with **4.73x average speedup** and **80% latency reduction**
- Full DNS resolution chain tracing (Root → TLD → Authoritative servers)

---

## Table of Contents
1. [Topology Setup](#topology-setup)
2. [DNS Configuration Scripts](#dns-configuration-scripts)
3. [Part A: Domain Extraction](#part-a-domain-extraction)
4. [Part B: DNS Resolution via Default Resolver](#part-b-dns-resolution-via-default-resolver)
5. [Part C: Custom DNS Resolver Setup](#part-c-custom-dns-resolver-setup)
6. [Part D: DNS Resolution with Caching](#part-d-dns-resolution-with-caching-analysis)
7. [Part E: Recursive Resolution Mode (BONUS)](#part-e-recursive-resolution-mode-bonus)
8. [Part F: DNS Caching (BONUS)](#part-f-dns-caching-bonus)
9. [Results & Analysis](#results--analysis)
10. [Key Findings](#key-findings)

---

## Topology Setup

We built the basic topology in Python using the mininet library. The topology includes hosts, switches, and respective links between them.

### Network Topology


**Topology Details:**
- **4 Hosts:** H1, H2, H3, H4 (10.0.0.1 - 10.0.0.4)
- **4 Switches:** S1, S2, S3, S4 (linear chain)
- **1 DNS Resolver:** 10.0.0.5 (connected to S2)
- **Access Links:** 2ms delay, 100 Mbps (host to switch)
- **Core Links:** 5ms, 8ms, 10ms delays, 100 Mbps (between switches)
- **DNS Link:** 1ms delay, 100 Mbps (DNS to S2)

### Topology Initialization
```bash
sudo mn --custom as2dns.py --topo dnsline --nat
```

### Connectivity Verification
Checked connectivity using commands:
- `net` - Display network topology
- `pingall` - Test connectivity between all hosts
- `pingallfull` - Detailed ping test between all hosts

---

## DNS Configuration Scripts

Before running Mininet, we use helper scripts to manage system DNS configuration:

### 1. `fix_dns_for_mininet.sh`
- Removes systemd-resolved symlink from `/etc/resolv.conf`
- Sets Google DNS (8.8.8.8, 8.8.4.4) as system resolvers
- **Required** to enable internet connectivity in Mininet with `--nat` flag

### 2. `restore_dns.sh`
- Restores original systemd-resolved configuration
- **Run after exiting Mininet** to restore normal DNS functionality

### 3. `run_mininet_safe.sh` (Recommended)
- Backs up VM DNS before running Mininet
- Automatically restores DNS after Mininet exits
- Safely changes only Mininet hosts' DNS, not the VM's

**Usage:**
```bash
./scripts/run_mininet_safe.sh
```

---

## Project Structure

```
CN_AS2/
├── as2dns.py
├── extract_all_domains.py
├── part_b_mininet.py
├── part_b_simple.py
├── part_c.py
├── part_d.py
├── part_d_analyze.py
├── domains/
│   ├── domains_PCAP_1_H1.txt  # 100 unique domains
│   ├── domains_PCAP_2_H2.txt
│   ├── domains_PCAP_3_H3.txt
│   ├── domains_PCAP_4_H4.txt
│   ├── resolved_h1.txt         # Part B results
│   ├── resolved_h2.txt
│   ├── resolved_h3.txt
│   └── resolved_h4.txt
├── results/
│   ├── dns_traffic_part_d.pcap
│   ├── part_c_report.txt
│   ├── part_d_analysis_report.txt
│   ├── part_d_detailed_log.json
│   ├── part_d_plots.png
│   ├── part_d_summary.txt
│   ├── resolved_h1_part_d.txt
│   ├── resolved_h2_part_d.txt
│   ├── resolved_h3_part_d.txt
│   └── resolved_h4_part_d.txt
├── scripts/
│   ├── run_mininet_safe.sh
│   ├── fix_dns_for_mininet.sh
│   └── restore_dns.sh
└── README.md
```

---

## Part A: Domain Extraction

### Objective
Extract DNS queries from 4 PCAP files to use for DNS resolution testing.

### Implementation
We wrote a Python script (`extract_all_domains.py`) based on Assignment 1 code that extracts DNS queries from PCAP files.

### Running Instructions
```bash
python3 extract_all_domains.py
```

### Results
- **100 DNS queries** extracted from each PCAP file
- Stored in separate text files in `domains/` directory
- **Total: 400 unique domains** across all PCAPs
- **Domain overlap:** 0 (each PCAP has unique domains)

### Files Generated
```
domains/
├── domains_PCAP_1_H1.txt  (100 unique domains)
├── domains_PCAP_2_H2.txt  (100 unique domains)
├── domains_PCAP_3_H3.txt  (100 unique domains)
└── domains_PCAP_4_H4.txt  (100 unique domains)
```

---

## Part B: DNS Resolution via Default Resolver

### Objective
Resolve URLs specified in each host's respective PCAP file using the **default host resolver** and record performance metrics.

### Implementation
We wrote a Python script (`part_b_mininet.py`) that runs in the Mininet topology to resolve each host's respective URLs using the default host resolver (8.8.8.8 via NAT).

### Configuration
- **DNS Server:** 8.8.8.8 (Google DNS via NAT)
- **Method:** Direct queries through NAT interface using `dig` command
- **Caching:** None (baseline measurements)

### Running Instructions

1. **Build Mininet topology with NAT:**
```bash
sudo mn -c
sudo mn --custom as2dns.py --topo dnsline --nat
```

2. **Test connectivity:**
```bash
mininet> pingall
```

3. **Run DNS resolution script:**
```bash
mininet> py exec(open('part_b_mininet.py').read())
mininet> py part_b(net)
```

### Metrics Recorded
For each host, the script logs:
- Average lookup latency
- Average throughput
- Number of successfully resolved queries
- Number of failed resolutions
- Timestamp, domain name, DNS server IP
- Response IPs, RTT, total resolution time
- Success/failure status

### Output Files
Resolved IP addresses saved in `domains/`:
```
domains/
├── resolved_h1.txt
├── resolved_h2.txt
├── resolved_h3.txt
└── resolved_h4.txt
```


### Summary Generated
The script generates a summary showing all metrics for each host (H1-H4).

**Note:** `part_b_simple.py` is a similar script written to run in a normal terminal using the default host resolver rather than in the Mininet topology for testing purposes. Results are also stored in the `domains/` folder if run.

---

## Part C: Custom DNS Resolver Setup

### Objective
Modify the DNS configuration of all Mininet hosts to use a custom resolver (10.0.0.5) as the primary DNS server instead of the default system resolver.

### Implementation
We created a custom DNS resolver on the 'dns' host (10.0.0.5) using **dnsmasq** and configured all Mininet hosts to use this custom resolver.

We wrote a Python script (`part_c.py`) that automates the setup and verification.

### Configuration Details

| Parameter | Value |
|-----------|-------|
| Custom DNS IP | 10.0.0.5 |
| Upstream Servers | 8.8.8.8, 8.8.4.4 |
| Cache Size | 1000 entries |
| Configured Hosts | h1, h2, h3, h4 |
| Status | OPERATIONAL |

### The Script Performs:
1. Installs dnsmasq on dns host (10.0.0.5)
2. Configures upstream DNS servers: 8.8.8.8, 8.8.4.4
3. Sets cache size: 1000 entries
4. Configures all hosts (h1, h2, h3, h4) to use nameserver 10.0.0.5

### Running Instructions

```bash
sudo mn -c
./scripts/run_mininet_safe.sh
```

Inside Mininet:
```bash
py exec(open('part_c.py').read())
py part_c(net)
```

### Verification Results

The script verifies:
✅ dnsmasq service running on dns host  
✅ All hosts configured with nameserver 10.0.0.5  
✅ DNS resolution functional (tested with google.com)

### Proof of Custom Resolver Usage

**1. dig Command Verification:**
```bash
mininet> h1 dig @10.0.0.5 google.com
```
Shows query to 10.0.0.5 with successful response.

**2. Blocked Upstream Test:**
We blocked direct access to 8.8.8.8 using iptables to prove all DNS traffic routes through the custom resolver:
- Direct query to 8.8.8.8: **BLOCKED** ❌
- Query via 10.0.0.5: **SUCCESSFUL** ✅

This proves all DNS traffic routes through custom resolver (10.0.0.5).

### Result
✅ **Successfully configured custom DNS resolver**  
✅ **All hosts now use 10.0.0.5 as the primary DNS server**  

---

## Part D: DNS Resolution with Caching Analysis

### Objective
Repeat DNS resolution for the given PCAPs using the custom DNS resolver (10.0.0.5), compare results with Part B, and demonstrate caching effectiveness.

Additionally, log the following in the custom DNS resolver:
- a. Timestamp
- b. Domain name queried
- c. Resolution mode
- d. DNS server IP contacted
- e. Step of resolution (Root / TLD / Authoritative / Cache)
- f. Response or referral received
- g. Round-trip time to that server
- h. Total time to resolution
- i. Cache status (HIT / MISS)

**For PCAP_1_H1:** Present graphical plots for the first 10 URLs showing:
- Total number of DNS servers visited
- Latency per query

### Implementation
Part D demonstrates DNS caching by resolving 400 unique domains through the custom resolver, then re-querying a subset to measure cache performance.

### Two-Phase Testing

#### Phase 1: Cache Population (First Query)
- Query **100 domains per host** (400 total)
- All queries are **cache MISS** (cache is empty)
- **First 10 domains per host:** Full DNS trace executed
  - Uses `dig +trace` to capture complete resolution path
  - Logs actual server count and resolution steps
  - Shows Root → TLD → Authoritative chain
  - Captures actual server count and resolution path
- Populates dnsmasq cache with successful resolutions
- Progress updates every 25 domains

#### Phase 2: Cache Testing (Re-query)
- Re-query **20 domains per host** (80 total)
- Tests cache effectiveness
- Compares RTT to Phase 1
- Queries marked as **cache HIT** if RTT < 50% of Phase 1
- Demonstrates caching performance

### Running Instructions

#### Step 1: Clean up and start Mininet
```bash
sudo mn -c
./scripts/run_mininet_safe.sh
```
*For safely changing only Mininet hosts' DNS, not the VM's*

#### Step 2: Inside Mininet - Setup custom DNS resolver (Part C)
```bash
py exec(open('part_c.py').read())
py part_c(net)
```

Wait for confirmation that **dnsmasq is running on 10.0.0.5**.

#### Step 3: Inside Mininet - Run Part D testing
```bash
py exec(open('part_d.py').read())
py part_d(net)
```

**Expected runtime:** ~3-5 minutes
- Phase 1: ~3-4 minutes (tracing adds overhead for first 10 domains)
- Phase 2: ~30-60 seconds (cached responses are fast)

#### Step 4: Exit Mininet
```bash
exit
```

#### Step 5: Generate visualization & analysis
```bash
python3 part_d_analyze.py
```

**Generates:**
- `results/part_d_plots.png` - Visualization (2 subplots)
- `results/part_d_analysis_report.txt` - Detailed breakdown with traced paths

#### Step 6: View results
```bash
# Summary statistics
cat results/part_d_summary.txt

# Detailed analysis
cat results/part_d_analysis_report.txt

# View plots
xdg-open results/part_d_plots.png
```

---

## Part E: Recursive Resolution Mode (BONUS)

### Objective
Implement recursive resolution mode in the custom DNS resolver. Modify the provided PCAP files to set a `recursive_mode` flag to True for all queries. If the resolver supports recursion, it should resolve recursively; otherwise, it should fall back to default resolution mode.

Record: average lookup latency, average throughput, number of successfully resolved queries, % of queries resolved from cache, and number of failed resolutions.

### Implementation Status: ✅ **COMPLETED IN PART D**

The custom DNS resolver (dnsmasq at 10.0.0.5) operates in **recursive mode** by default. When a query is received:

1. **Check Cache:** Resolver first checks its local cache
2. **Recursive Query:** If not cached, resolver recursively queries upstream servers
3. **Follow DNS Hierarchy:** Root → TLD → Authoritative servers
4. **Return Answer:** Final answer returned to client

### Evidence of Recursive Resolution

**DNS Tracing Implementation:**
- First 10 queries per host traced with `dig +trace`
- Captures complete resolution chain
- Records all intermediate DNS servers

**Example Recursive Resolution Trace:**

```
Domain: 2brightsparks.co.uk
─────────────────────────────────────────
Step 1: Query Root Server
  Server: m.root-servers.net (202.12.27.33)
  Response: Referral to .uk TLD servers
  
Step 2: Query TLD Server
  Server: dns3.nic.uk (213.248.220.1)
  Response: Referral to authoritative servers
  
Step 3: Query Authoritative Server
  Server: ns-1782.awsdns-30.co.uk (205.251.198.246)
  Response: Final answer (52.58.101.213)
  
Total Servers Visited: 4 (including local resolver)
Resolution Time: 96.0 ms
```

### Metrics (Part E Requirements)

From `results/part_d_summary.txt`:

| Metric | Value |
|--------|-------|
| **Average Lookup Latency** | 202.58 ms |
| **Average Throughput** | 1.52 queries/sec |
| **Successfully Resolved Queries** | 281/400 (70%) |
| **Failed Resolutions** | 119/400 (30%) |
| **Cache Hit Rate** | 14% overall (67/480 total queries) |

### Resolution Mode Field

All queries include `resolution_mode` field(eg. below):
```json
{
  "resolution_mode": "recursive",
  "servers_visited_count": 4,
  "dns_servers_list": [
    {"type": "Root", "name": "m.root-servers.net", "ip": "202.12.27.33"},
    {"type": "TLD", "name": "dns3.nic.uk", "ip": "213.248.220.1"},
    {"type": "Authoritative", "name": "ns-1782.awsdns-30.co.uk", "ip": "205.251.198.246"}
  ]
}
```

### Verification

To verify recursive resolution:
```bash
# View traced queries in detailed log
cat results/part_d_detailed_log.json | grep -A 20 "full_resolution_path"

# View analysis report with resolution chains
head -100 results/part_d_analysis_report.txt
```

---

## Part F: DNS Caching (BONUS)

### Objective
Implement caching within custom DNS resolver. Store recently resolved domain-to-IP mappings and serve repeated queries directly from cache without contacting external servers.

Record: average lookup latency, average throughput, number of successfully resolved queries, % of queries resolved from cache, and number of failed resolutions.

### Implementation Status: ✅ **COMPLETED IN PART D**

The custom DNS resolver uses **dnsmasq** with a 1000-entry cache. The implementation uses a **two-phase approach** to demonstrate caching effectiveness:

### Caching Architecture

```
Client Query
     ↓
┌─────────────────────────────────────┐
│   Custom DNS Resolver (10.0.0.5)   │
│          dnsmasq cache              │
│        (1000 entries)               │
└─────────────────────────────────────┘
     ↓                    ↓
  Cache HIT          Cache MISS
     ↓                    ↓
Return cached      Query upstream
IP (fast)          (8.8.8.8, 8.8.4.4)
                        ↓
                   Store in cache
                        ↓
                   Return to client
```

### Two-Phase Caching Demonstration

#### Phase 1: Cache Population
- Query 100 domains per host (400 total)
- All queries are **cache MISS** (cache is empty)
- Average RTT: **121.6 ms** (4 servers contacted)
- Stores successful resolutions in dnsmasq cache

#### Phase 2: Cache Testing
- Re-query 20 domains per host (80 total)
- Most queries are **cache HIT** (served from cache)
- Average RTT: **24.4 ms** (1 server contacted)
- No external DNS servers contacted for cache hits

### Cache Detection Logic

```python
def detect_cache_hit(phase1_rtt, phase2_rtt):
    """
    Cache HIT detection using relative comparison
    Cached queries are typically 50%+ faster
    """
    if phase2_rtt < (phase1_rtt * 0.5):
        return True  # Cache HIT
    else:
        return False  # Cache MISS
```

### Metrics (Part F Requirements)

From `results/part_d_summary.txt` and `results/part_d_analysis_report.txt`:

#### Overall Performance

| Metric | Phase 1 (MISS) | Phase 2 (HIT) | Improvement |
|--------|----------------|---------------|-------------|
| **Average Latency** | 121.6 ms | 24.4 ms | **80% reduction** |
| **Servers Contacted** | 4 servers | 1 server | **75% reduction** |
| **Average Speedup** | Baseline | 4.73x | **373% faster** |

#### Cache Hit Rates by Host

| Host | Phase 2 Re-queries | Cache Hits | Hit Rate |
|------|-------------------|------------|----------|
| H1 | 20 | 19 | 95.0% |
| H2 | 20 | 20 | 100.0% |
| H3 | 20 | 17 | 85.0% |
| H4 | 20 | 11 | 55.0% |
| **Total** | **80** | **67** | **84%** |

#### Overall Query Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Queries** | 480 | 100% |
| **Successfully Resolved** | 281 | 58.5% |
| **Failed Resolutions** | 119 | 24.8% |
| **Cache Hits** | 67 | 14.0% (of all queries) |
| | | 84% (of Phase 2 re-queries) |

#### Performance Highlights

- **Best Speedup:** 19.6x faster (alenpuaca.com: 548ms → 28ms)
- **Average Throughput (Phase 2):** Higher due to cache
- **Latency Reduction:** 80% average (121.6ms → 24.4ms)
- **Server Load Reduction:** 75% (4 servers → 1 server per query)

### Cache Performance Examples

```
Domain: 2brightsparks.co.uk
  Phase 1 (MISS): 96.0 ms  (4 servers)
  Phase 2 (HIT):  24.0 ms  (1 server)
  Speedup: 4.0x faster

Domain: alenpuaca.com
  Phase 1 (MISS): 548.0 ms  (4 servers)
  Phase 2 (HIT):  28.0 ms   (1 server)
  Speedup: 19.6x faster (BEST CASE)

Domain: amgala.com
  Phase 1 (MISS): 112.0 ms  (4 servers)
  Phase 2 (HIT):  24.0 ms   (1 server)
  Speedup: 4.7x faster
```

### Verification

To verify caching implementation:

```bash
# View cache statistics
cat results/part_d_summary.txt

# View detailed cache hit/miss data
python3 -c "
import json
with open('results/part_d_detailed_log.json') as f:
    data = json.load(f)
    phase2 = [q for q in data if q['phase'] == 2]
    hits = [q for q in phase2 if q['cache_hit']]
    print(f'Cache Hits: {len(hits)}/{len(phase2)} ({100*len(hits)/len(phase2):.1f}%)')
"

# View analysis report with cache performance
cat results/part_d_analysis_report.txt | grep -A 5 "Cache HIT"
```

---

## DNS Resolution Tracing

### Overview
The first 10 domains per host undergo full DNS tracing using `dig +trace` to capture the complete recursive resolution chain.

### Cache MISS (First Query)
When a domain is queried for the first time, the complete DNS hierarchy is traversed:

```
Client (h1) 
    ↓
1. Custom Resolver (10.0.0.5) - dnsmasq
    ↓
2. Upstream Resolver (8.8.8.8) - Google DNS
    ↓
3. Root Server (e.g., m.root-servers.net - 202.12.27.33)
    ↓
4. TLD Server (e.g., a.gtld-servers.net - 192.5.6.30 for .com)
    ↓
5. Authoritative Server (e.g., ns1.example.com - 93.184.216.34)
```

**Total Servers:** Typically **4-5 servers**

### Cache HIT (Re-query)
When a domain is re-queried from cache:

```
Client (h1)
    ↓
1. Custom Resolver (10.0.0.5) - Answers from cache
```

**Total Servers:** **1 server**

### Example Traced Output

```
Domain: 2brightsparks.co.uk
Resolution Mode:  Recursive
DNS Server:       10.0.0.5
Resolution Step:  dnsmasq -> upstream (8.8.8.8/8.8.4.4)
Full Resolution Path (Traced):
   → 10.0.0.5 (10.0.0.5)
   → m.root-servers.net (202.12.27.33)
   → dns3.nic.uk (213.248.220.1)
   → ns-1782.awsdns-30.co.uk (205.251.198.246)
Servers Visited:  4 (traced)
Response:         143.204.55.129, 143.204.55.7, 143.204.55.44, 143.204.55.11
RTT:              96.0 ms
Total Time:       2995.58 ms
Cache Status:     MISS (upstream)
```

**Note:** The above is actual traced output from Part D execution showing the complete DNS resolution chain captured using `dig +trace`.

---

### Output Files

#### Logs
- `results/part_d_detailed_log.json` - All queries with full details, traced DNS paths
- `results/part_d_summary.txt` - High-level statistics per host
- `results/resolved_h[1-4]_part_d.txt` - Successfully resolved domains and IPs

#### Network Capture
- `results/dns_traffic_part_d.pcap` - DNS traffic on dns-eth0 interface

#### Analysis & Visualization
- `results/part_d_plots.png` - Two-subplot visualization
  - Plot 1: Latency per query (Phase 1 vs Phase 2 comparison)
  - Plot 2: DNS servers visited (traced data showing 4→1 reduction)
- `results/part_d_analysis_report.txt` - Detailed query-by-query breakdown with full traced resolution paths

---