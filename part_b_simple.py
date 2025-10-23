"""
Simple Part B Test - Just runs on YOUR HOST machine (not in Mininet)
This is the simplest approach for Part B
"""

import socket
import time
import statistics

def test_dns_resolution(domain_file, host_name):
    """Test DNS resolution for domains in a file"""
    
    # Load domains
    with open(domain_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]
    
    print(f"\nTesting {host_name}: {len(domains)} domains...")
    
    successful = 0
    failed = 0
    latencies = []
    resolved_ips = []  # Store domain -> IP mappings
    
    socket.setdefaulttimeout(5)
    
    for idx, domain in enumerate(domains, 1):
        try:
            start = time.time()
            result = socket.getaddrinfo(domain, None, socket.AF_INET)
            latency = (time.time() - start) * 1000
            
            # Extract IP addresses and remove duplicates (getaddrinfo returns multiple socket types)
            ips = list(dict.fromkeys([addr[4][0] for addr in result]))
            resolved_ips.append({
                'domain': domain,
                'ips': ips,
                'latency': latency
            })
            
            successful += 1
            latencies.append(latency)
        except:
            failed += 1
        
        if idx % 20 == 0:
            print(f"  Progress: {idx}/{len(domains)}")
    
    # Calculate stats
    total = len(domains)
    if latencies:
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        total_time = sum(latencies) / 1000
        throughput = successful / total_time if total_time > 0 else 0
    else:
        avg_latency = min_latency = max_latency = throughput = 0
        total_time = 0
    
    # Print results
    print(f"\nResults for {host_name}:")
    print(f"  Total queries:     {total}")
    print(f"  Successful:        {successful} ({successful*100/total:.1f}%)")
    print(f"  Failed:            {failed} ({failed*100/total:.1f}%)")
    print(f"  Avg Latency:       {avg_latency:.2f} ms")
    print(f"  Min Latency:       {min_latency:.2f} ms")
    print(f"  Max Latency:       {max_latency:.2f} ms")
    print(f"  Throughput:        {throughput:.2f} queries/sec")
    
    # Save resolved IPs to file
    output_file = f'domains/resolved_{host_name.lower()}_simple.txt'
    with open(output_file, 'w') as f:
        f.write(f"DNS Resolution Results for {host_name} (Simple/Standalone)\n")
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
    
    return {
        'host': host_name,
        'total': total,
        'successful': successful,
        'failed': failed,
        'avg_latency': avg_latency,
        'throughput': throughput
    }

def main():
    print("="*80)
    print("CS331 Assignment 2 - PART B: DNS Resolution Testing")
    print("="*80)
    
    # Test all hosts
    host_configs = {
        'H1': 'domains/domains_PCAP_1_H1.txt',
        'H2': 'domains/domains_PCAP_2_H2.txt',
        'H3': 'domains/domains_PCAP_3_H3.txt',
        'H4': 'domains/domains_PCAP_4_H4.txt'
    }
    
    results = []
    
    for host_name, domain_file in host_configs.items():
        print("\n" + "="*80)
        result = test_dns_resolution(domain_file, host_name)
        results.append(result)
    
    # Summary table
    print("\n" + "="*80)
    print("PART B SUMMARY")
    print("="*80)
    print(f"{'Host':<6} {'Total':<7} {'Success':<15} {'Failed':<8} {'Avg Lat (ms)':<14} {'Throughput':<15}")
    print("-"*80)
    
    for r in results:
        success_pct = f"{r['successful']} ({r['successful']*100/r['total']:.1f}%)"
        print(f"{r['host']:<6} {r['total']:<7} {success_pct:<15} {r['failed']:<8} {r['avg_latency']:<14.2f} {r['throughput']:<15.2f}")
    
    print("\n" + "="*80)
    print("Part B Complete!")
    print("="*80)

if __name__ == "__main__":
    main()
