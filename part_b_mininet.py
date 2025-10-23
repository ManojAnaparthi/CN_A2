"""
Part B for Mininet - Simple version using dig command
Run from Mininet CLI: py exec(open('part_b_mininet.py').read()); test_part_b(net)
"""

def test_part_b(net):
    """Run Part B DNS tests in Mininet"""
    import os
    import time
    
    print("\n" + "="*80)
    print("PART B: DNS Resolution Testing in Mininet")
    print("="*80)
    
    cwd = os.getcwd()
    
    configs = {
        'h1': f'{cwd}/domains/domains_PCAP_1_H1.txt',
        'h2': f'{cwd}/domains/domains_PCAP_2_H2.txt',
        'h3': f'{cwd}/domains/domains_PCAP_3_H3.txt',
        'h4': f'{cwd}/domains/domains_PCAP_4_H4.txt'
    }
    
    all_results = {}
    
    for host_name, domain_file in configs.items():
        print(f"\n{'='*80}")
        print(f"Testing {host_name.upper()}")
        print(f"{'='*80}")
        
        host = net.get(host_name)
        
        # Load domains
        with open(domain_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        
        print(f"Testing {len(domains)} domains...")
        
        successful = 0
        failed = 0
        latencies = []
        resolved_ips = []  # Store domain -> IP mappings
        
        start_time = time.time()
        
        for idx, domain in enumerate(domains, 1):
            # Use dig WITHOUT specifying DNS server - uses system default
            # This will use the host's DNS resolver through Mininet
            query_start = time.time()
            result = host.cmd(f'dig +time=5 +tries=1 {domain}')
            query_time = (time.time() - query_start) * 1000  # in ms
            
            # Check if we got a valid response (not NXDOMAIN, not SERVFAIL)
            if 'ANSWER SECTION' in result and 'NXDOMAIN' not in result and 'SERVFAIL' not in result:
                # Extract the actual query time from dig output
                import re
                time_match = re.search(r'Query time: (\d+) msec', result)
                if time_match:
                    actual_query_time = float(time_match.group(1))
                else:
                    actual_query_time = query_time
                
                # Extract IP addresses from the ANSWER SECTION (only A records)
                # Format: domain.com.  300  IN  A  1.2.3.4
                answer_section = result.split('ANSWER SECTION:')[1].split('\n\n')[0] if 'ANSWER SECTION:' in result else ''
                # Match only lines with A records (not AAAA, not query/server info)
                ip_matches = re.findall(r'\s+IN\s+A\s+((?:\d{1,3}\.){3}\d{1,3})', answer_section)
                # Remove duplicates while preserving order
                ip_matches = list(dict.fromkeys(ip_matches))
                if ip_matches:
                    resolved_ips.append({
                        'domain': domain,
                        'ips': ip_matches,
                        'latency': actual_query_time
                    })
                
                successful += 1
                latencies.append(actual_query_time)
            else:
                failed += 1
            
            if idx % 20 == 0:
                print(f"  Progress: {idx}/{len(domains)} - Success: {successful}, Failed: {failed}")
        
        total_time = time.time() - start_time
        
        # Calculate stats
        total = len(domains)
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
        else:
            avg_latency = min_latency = max_latency = 0
        
        throughput = successful / total_time if total_time > 0 else 0
        
        # Store results
        all_results[host_name] = {
            'total': total,
            'successful': successful,
            'failed': failed,
            'avg_latency': avg_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'throughput': throughput,
            'total_time': total_time,
            'resolved_ips': resolved_ips
        }
        
        # Save resolved IPs to file
        output_file = f'{cwd}/domains/resolved_{host_name}.txt'
        with open(output_file, 'w') as f:
            f.write(f"DNS Resolution Results for {host_name.upper()}\n")
            f.write(f"{'='*70}\n")
            f.write(f"Total: {total}, Successful: {successful}, Failed: {failed}\n")
            f.write(f"Average Latency: {avg_latency:.2f} ms\n")
            f.write(f"{'='*70}\n\n")
            
            for entry in resolved_ips:
                f.write(f"{entry['domain']}\n")
                for ip in entry['ips']:
                    f.write(f"  -> {ip}\n")
                f.write(f"  Latency: {entry['latency']:.2f} ms\n\n")
        
        print(f"  Resolved IPs saved to: {output_file}")
        
        # Print results
        print(f"\nResults for {host_name.upper()}:")
        print(f"  Total queries:     {total}")
        print(f"  Successful:        {successful} ({successful*100/total:.1f}%)")
        print(f"  Failed:            {failed} ({failed*100/total:.1f}%)")
        print(f"  Avg Latency:       {avg_latency:.2f} ms")
        print(f"  Min Latency:       {min_latency:.2f} ms")
        print(f"  Max Latency:       {max_latency:.2f} ms")
        print(f"  Throughput:        {throughput:.2f} queries/sec")
        print(f"  Total time:        {total_time:.2f} sec")
    
    # Summary table with all metrics
    print("\n" + "="*120)
    print("PART B SUMMARY - ALL METRICS")
    print("="*120)
    print(f"{'Host':<6} {'Total':<7} {'Success':<12} {'Failed':<8} {'Avg Lat':<10} {'Min Lat':<10} {'Max Lat':<10} {'Throughput':<13} {'Time (s)':<10}")
    print(f"{'':6} {'':7} {'':12} {'':8} {'(ms)':<10} {'(ms)':<10} {'(ms)':<10} {'(q/s)':<13} {'':10}")
    print("-"*120)
    
    for host_name in ['h1', 'h2', 'h3', 'h4']:
        r = all_results[host_name]
        success_pct = f"{r['successful']} ({r['successful']*100/r['total']:.0f}%)"
        failed_pct = f"{r['failed']} ({r['failed']*100/r['total']:.0f}%)"
        print(f"{host_name.upper():<6} {r['total']:<7} {success_pct:<12} {failed_pct:<8} "
              f"{r['avg_latency']:<10.2f} {r['min_latency']:<10.2f} {r['max_latency']:<10.2f} "
              f"{r['throughput']:<13.2f} {r['total_time']:<10.2f}")
    
    print("\n" + "="*120)
    print("Part B Complete!")
    print("="*120)

if __name__ == "__main__":
    print("Run from Mininet CLI:")
    print("  py exec(open('part_b_mininet.py').read())")
    print("  py test_part_b(net)")
