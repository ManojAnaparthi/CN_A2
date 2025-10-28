#!/usr/bin/env python3
"""
Part D: DNS Resolution with Custom Resolver
Resolve all 400 domains using custom resolver with automatic caching

Run from Mininet CLI: py exec(open('part_d.py').read()); part_d(net)
"""

def part_d(net):
    """DNS resolution testing through custom resolver (10.0.0.5) with caching"""
    import os
    import time
    import json
    import re
    from datetime import datetime
    
    def trace_dns_resolution(host, domain):
        """
        Trace full DNS resolution path using dig +trace
        Returns: (server_count, resolution_path_list, servers_list)
        """
        result = host.cmd(f'dig +trace +tries=1 +time=3 {domain} 2>/dev/null')
        
        servers_visited = []
        resolution_steps = []
        
        # Parse dig +trace output to find all servers contacted
        lines = result.split('\n')
        current_step = None
        
        for line in lines:
            # Root servers (.)
            if 'IN\tNS' in line and not current_step:
                current_step = 'Root'
            # TLD servers (.com, .org, etc)
            elif 'IN\tNS' in line and current_step == 'Root':
                current_step = 'TLD'
            # Authoritative answer
            elif 'IN\tA\t' in line and current_step:
                current_step = 'Authoritative'
                
            # Extract server IPs from trace
            if ';; Received' in line:
                # Format: ;; Received 525 bytes from 192.5.5.241#53(f.root-servers.net) in 45 ms
                match = re.search(r'from\s+([\d.]+)#\d+\(([\w.-]+)\)', line)
                if match:
                    server_ip = match.group(1)
                    server_name = match.group(2)
                    if server_ip not in [s[0] for s in servers_visited]:
                        servers_visited.append((server_ip, server_name, current_step or 'Unknown'))
                        resolution_steps.append(f"{current_step or 'Unknown'}: {server_name} ({server_ip})")
        
        return len(servers_visited), resolution_steps, servers_visited
    
    print("\n" + "="*80)
    print("PART D: DNS Resolution with Custom Resolver")
    print("="*80)
    
    cwd = os.getcwd()
    dns_host = net.get('dns')
    
    # Verify custom resolver
    print("\n[*] Verifying custom DNS resolver...")
    pid = dns_host.cmd('pgrep dnsmasq').strip()
    if not pid:
        print("[FAIL] dnsmasq not running. Please run Part C first.")
        return
    print(f"[OK] dnsmasq running (PID: {pid}) with cache-size=1000")
    
    # Clear cache and logs for fresh start
    print("[*] Clearing cache and starting fresh...")
    dns_host.cmd('killall -HUP dnsmasq')  # Clear cache
    dns_host.cmd('echo "" > /var/log/dnsmasq.log 2>/dev/null')
    time.sleep(1)
    
    # Start packet capture
    print("[*] Starting packet capture on dns-eth0...")
    dns_host.cmd('rm -f /tmp/dns_traffic_part_d.pcap')
    dns_host.cmd('tcpdump -i dns-eth0 -w /tmp/dns_traffic_part_d.pcap port 53 > /dev/null 2>&1 &')
    time.sleep(1)
    print("[OK] Ready\n")
    
    configs = {
        'h1': f'{cwd}/domains/domains_PCAP_1_H1.txt',
        'h2': f'{cwd}/domains/domains_PCAP_2_H2.txt',
        'h3': f'{cwd}/domains/domains_PCAP_3_H3.txt',
        'h4': f'{cwd}/domains/domains_PCAP_4_H4.txt'
    }
    
    all_results = {}
    detailed_logs = []
    
    for host_name, domain_file in configs.items():
        print(f"\n{'='*80}")
        print(f"Testing {host_name.upper()} - Custom Resolver (10.0.0.5)")
        print(f"{'='*80}")
        
        host = net.get(host_name)
        
        # Verify DNS configuration
        resolv = host.cmd('cat /etc/resolv.conf | grep nameserver').strip()
        if '10.0.0.5' not in resolv:
            print(f"[FAIL] {host_name} not configured to use 10.0.0.5")
            print(f"Current: {resolv}")
            continue
        print(f"[OK] DNS: {resolv}")
        
        if not os.path.exists(domain_file):
            print(f"[FAIL] Domain file not found: {domain_file}")
            continue
        
        with open(domain_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        
        print(f"[*] Phase 1: Resolving {len(domains)} unique domains...")
        
        stats = {
            'successful': 0,
            'failed': 0,
            'latencies': [],
            'resolved_ips': [],
            'successful_domains': [],  # Track for cache test
            'domain_rtts': {}  # Track Phase 1 RTT for comparison
        }
        
        start_time = time.time()
        
        for idx, domain in enumerate(domains, 1):
            query_start = time.time()
            
            # For first 10 domains, trace full DNS resolution path
            if idx <= 10:
                print(f"  [Tracing] {domain}...")
                server_count, resolution_path, servers_list = trace_dns_resolution(host, domain)
            else:
                server_count = None
                resolution_path = []
                servers_list = []
            
            result = host.cmd(f'dig @10.0.0.5 +time=2 +tries=1 {domain}')
            total_time = (time.time() - query_start) * 1000
            
            if 'ANSWER SECTION' in result and 'NXDOMAIN' not in result and 'SERVFAIL' not in result:
                # Extract query time
                time_match = re.search(r'Query time: (\d+) msec', result)
                rtt = float(time_match.group(1)) if time_match else total_time
                
                # Extract IPs
                answer = result.split('ANSWER SECTION:')[1].split('\n\n')[0] if 'ANSWER SECTION:' in result else ''
                ips = re.findall(r'\s+IN\s+A\s+((?:\d{1,3}\.){3}\d{1,3})', answer)
                ips = list(dict.fromkeys(ips))
                
                # Detect if served from cache (very fast response)
                cache_status = "HIT (cached)" if rtt < 5 else "MISS (upstream)"
                
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'host': host_name,
                    'domain': domain,
                    'query_num': idx,
                    'resolution_mode': 'Recursive',  # dnsmasq does recursive resolution
                    'dns_server': '10.0.0.5',
                    'resolution_step': 'dnsmasq cache' if rtt < 5 else 'dnsmasq -> upstream (8.8.8.8/8.8.4.4)',
                    'response': ', '.join(ips) if ips else 'No IP',
                    'rtt_ms': round(rtt, 2),
                    'total_time_ms': round(total_time, 2),
                    'cache_status': cache_status,
                    'success': True
                }
                
                # Add trace information if available
                if server_count is not None:
                    log_entry['servers_visited_count'] = server_count
                    log_entry['full_resolution_path'] = resolution_path
                    log_entry['dns_servers_list'] = [{'ip': s[0], 'name': s[1], 'type': s[2]} for s in servers_list]
                
                stats['successful'] += 1
                stats['latencies'].append(rtt)
                stats['resolved_ips'].append(f"{domain}: {', '.join(ips)}")
                stats['successful_domains'].append(domain)  # Track for cache test
                stats['domain_rtts'][domain] = rtt  # Track Phase 1 RTT
                detailed_logs.append(log_entry)
            else:
                stats['failed'] += 1
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'host': host_name,
                    'domain': domain,
                    'query_num': idx,
                    'resolution_mode': 'Recursive',
                    'dns_server': '10.0.0.5',
                    'resolution_step': 'Failed',
                    'response': 'NXDOMAIN/SERVFAIL',
                    'rtt_ms': 0,
                    'total_time_ms': round(total_time, 2),
                    'cache_status': 'N/A',
                    'success': False
                }
                detailed_logs.append(log_entry)
            
            if idx % 25 == 0:
                print(f"  Progress: {idx}/{len(domains)} - Success: {stats['successful']}, Failed: {stats['failed']}")
        
        print(f"\n[Phase 1 Complete] {stats['successful']} domains resolved and cached")
        
        # ========================================================================
        # PHASE 2: Re-query subset to demonstrate caching
        # ========================================================================
        requery_count = min(20, len(stats['successful_domains']))
        cache_hits = 0
        
        if requery_count > 0:
            print(f"[*] Phase 2: Re-querying first {requery_count} domains to test cache...")
            requery_domains = stats['successful_domains'][:requery_count]
            
            time.sleep(0.5)  # Brief pause
            
            for domain in requery_domains:
                query_start = time.time()
                result = host.cmd(f'dig @10.0.0.5 +time=2 +tries=1 {domain}')
                total_time = (time.time() - query_start) * 1000
                
                if 'ANSWER SECTION' in result and 'NXDOMAIN' not in result:
                    # Extract query time
                    time_match = re.search(r'Query time: (\d+) msec', result)
                    rtt = float(time_match.group(1)) if time_match else total_time
                    
                    # Extract IPs
                    answer = result.split('ANSWER SECTION:')[1].split('\n\n')[0] if 'ANSWER SECTION:' in result else ''
                    ips = re.findall(r'\s+IN\s+A\s+((?:\d{1,3}\.){3}\d{1,3})', answer)
                    ips = list(dict.fromkeys(ips))
                    
                    # Cache detection: Compare to Phase 1 RTT
                    # Cached responses should be significantly faster (at least 50% faster)
                    first_rtt = stats['domain_rtts'].get(domain, 999)
                    is_cached = (rtt < first_rtt * 0.5)  # 50% or faster = cached
                    cache_status = "HIT (from cache)" if is_cached else "MISS"
                    
                    if is_cached:
                        cache_hits += 1
                    
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'host': host_name,
                        'domain': domain,
                        'query_num': 'requery',
                        'resolution_mode': 'Recursive (cache test)',
                        'dns_server': '10.0.0.5',
                        'resolution_step': 'dnsmasq cache' if is_cached else 'dnsmasq -> upstream',
                        'response': ', '.join(ips),
                        'rtt_ms': round(rtt, 2),
                        'total_time_ms': round(total_time, 2),
                        'cache_status': cache_status,
                        'first_rtt_ms': round(first_rtt, 2),  # For comparison
                        'speedup': f"{first_rtt/rtt:.1f}x" if rtt > 0 else "N/A",
                        'success': True
                    }
                    
                    detailed_logs.append(log_entry)
                
                time.sleep(0.05)  # Small delay
            
            cache_hit_rate = (cache_hits / requery_count * 100) if requery_count > 0 else 0
            print(f"[Phase 2 Complete] Cache hits: {cache_hits}/{requery_count} ({cache_hit_rate:.1f}%)\n")
        
        # Calculate stats
        end_time = time.time()
        total_time = end_time - start_time
        total_queries = stats['successful'] + stats['failed'] + requery_count
        avg_latency = sum(stats['latencies']) / len(stats['latencies']) if stats['latencies'] else 0
        throughput = (stats['successful'] + stats['failed']) / total_time if total_time > 0 else 0
        
        # Save results
        all_results[host_name] = {
            'total_queries': total_queries,
            'phase1_queries': stats['successful'] + stats['failed'],
            'phase2_queries': requery_count,
            'successful': stats['successful'],
            'failed': stats['failed'],
            'avg_latency_ms': round(avg_latency, 2),
            'throughput_qps': round(throughput, 2),
            'total_time_s': round(total_time, 2),
            'cache_hits': cache_hits,
            'cache_hit_rate_percent': round(cache_hit_rate, 1)
        }
        
        # Save resolved IPs to results directory
        import subprocess
        subprocess.run(['mkdir', '-p', f'{cwd}/results'], check=False)
        
        output_file = f'{cwd}/results/resolved_{host_name}_part_d.txt'
        with open(output_file, 'w') as f:
            f.write('\n'.join(stats['resolved_ips']))
        print(f"\n[OK] Saved {len(stats['resolved_ips'])} resolved IPs to results/{output_file.split('/')[-1]}")
        
        print(f"\n{'='*80}")
        print(f"{host_name.upper()} Summary")
        print(f"{'='*80}")
        print(f"Phase 1: {stats['successful'] + stats['failed']} queries ({stats['successful']} successful)")
        print(f"Phase 2: {requery_count} re-queries ({cache_hits} cache hits)")
        print(f"Total queries: {total_queries}")
        print(f"Avg latency (Phase 1): {avg_latency:.2f}ms")
        print(f"Throughput: {throughput:.2f} queries/sec")
        print(f"Cache hit rate: {cache_hits}/{requery_count} ({cache_hit_rate:.1f}%)")
    
    # Stop packet capture
    print(f"\n{'='*80}")
    print("Finalizing...")
    print(f"{'='*80}")
    dns_host.cmd('killall tcpdump 2>/dev/null')
    time.sleep(1)
    
    # Copy PCAP to results directory
    dns_host.cmd(f'mkdir -p {cwd}/results 2>/dev/null')
    dns_host.cmd(f'cp /tmp/dns_traffic_part_d.pcap {cwd}/results/')
    print(f"[OK] Saved packet capture to results/dns_traffic_part_d.pcap")
    
    # Save detailed logs to results
    log_file = f'{cwd}/results/part_d_detailed_log.json'
    with open(log_file, 'w') as f:
        json.dump(detailed_logs, f, indent=2)
    print(f"[OK] Saved detailed logs to results/part_d_detailed_log.json")
    
    # Save summary to results
    summary_file = f'{cwd}/results/part_d_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("PART D: DNS Resolution Summary (Custom Resolver)\n")
        f.write("="*80 + "\n\n")
        
        f.write("Configuration:\n")
        f.write("  DNS Resolver: 10.0.0.5 (dnsmasq)\n")
        f.write("  Cache Size: 1000 entries\n")
        f.write("  Upstream: 8.8.8.8, 8.8.4.4\n\n")
        
        for host_name, result in all_results.items():
            f.write(f"{host_name.upper()}:\n")
            f.write(f"  Phase 1: {result['phase1_queries']} queries ({result['successful']} successful, {result['failed']} failed)\n")
            f.write(f"  Phase 2: {result['phase2_queries']} re-queries ({result['cache_hits']} cache hits)\n")
            f.write(f"  Total queries: {result['total_queries']}\n")
            f.write(f"  Avg latency: {result['avg_latency_ms']:.2f}ms\n")
            f.write(f"  Throughput: {result['throughput_qps']:.2f} queries/sec\n")
            f.write(f"  Cache hit rate: {result['cache_hits']}/{result['phase2_queries']} ({result['cache_hit_rate_percent']:.1f}%)\n\n")
        
        # Overall totals
        total_all = sum(r['total_queries'] for r in all_results.values())
        success_all = sum(r['successful'] for r in all_results.values())
        failed_all = sum(r['failed'] for r in all_results.values())
        cache_hits_all = sum(r['cache_hits'] for r in all_results.values())
        
        f.write(f"{'='*80}\n")
        f.write("OVERALL TOTALS:\n")
        f.write(f"  Total queries: {total_all}\n")
        f.write(f"  Successful: {success_all}\n")
        f.write(f"  Failed: {failed_all}\n")
        f.write(f"  Cache hits: {cache_hits_all} ({cache_hits_all/total_all*100:.1f}%)\n")
    
    print(f"[OK] Saved summary to results/part_d_summary.txt")
    
    print(f"\n{'='*80}")
    print("PART D COMPLETE")
    print(f"{'='*80}")
    print("\nFiles created in results/ directory:")
    print("  - part_d_summary.txt (overview)")
    print("  - part_d_detailed_log.json (all queries)")
    print("  - resolved_h[1-4]_part_d.txt (resolved IPs)")
    print("  - dns_traffic_part_d.pcap (packet capture)")
    print("\nCaching demonstration:")
    print("  - Phase 1: Queries all unique domains (populates cache)")
    print("  - Phase 2: Re-queries 20 domains (demonstrates cache hits)")
    print("  - Expected: ~100% cache hit rate in Phase 2 (responses <5ms)")
    print("  - Note: No overlap between PCAP files, so cache only works within each host")
    print("\nVerify caching:")
    print("  dns cat /var/log/dnsmasq.log | grep cached | head -20")
