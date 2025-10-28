#!/usr/bin/env python3
"""
Part D: Analysis and Visualization
Compare Part D with Part B and create plots for first 10 URLs

Run outside Mininet: python3 part_d_analyze.py
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('Agg')

def analyze_part_d():
    """Analyze Part D results and create visualizations"""
    
    print("\n" + "="*80)
    print("PART D: Analysis and Visualization")
    print("="*80)
    
    # Load Part D logs from results directory
    log_file = 'results/part_d_detailed_log.json'
    if not os.path.exists(log_file):
        print(f"[FAIL] {log_file} not found")
        print("Please run Part D testing first in Mininet")
        return
    
    with open(log_file, 'r') as f:
        logs = json.load(f)
    
    print(f"\n[*] Loaded {len(logs)} log entries from Part D")
    
    # Get Phase 1 (initial queries) and Phase 2 (re-queries) for H1
    h1_phase1 = [log for log in logs 
                 if log['host'] == 'h1' 
                 and log.get('query_num') != 'requery'
                 and log['success']]
    
    h1_phase2 = [log for log in logs 
                 if log['host'] == 'h1' 
                 and log.get('query_num') == 'requery'
                 and log['success']]
    
    print(f"[*] Found {len(h1_phase1)} Phase 1 queries and {len(h1_phase2)} Phase 2 re-queries")
    
    # Get domains that were re-queried (appear in both phases)
    phase2_domains = [log['domain'] for log in h1_phase2]
    
    # Find matching Phase 1 entries for comparison (limit to first 10 for visualization)
    comparison_data = []
    for domain in phase2_domains[:10]:
        phase1_log = next((log for log in h1_phase1 if log['domain'] == domain), None)
        phase2_log = next((log for log in h1_phase2 if log['domain'] == domain), None)
        
        if phase1_log and phase2_log:
            comparison_data.append({
                'domain': domain,
                'phase1_rtt': phase1_log['rtt_ms'],
                'phase2_rtt': phase2_log['rtt_ms'],
                'phase1_servers': phase1_log.get('servers_visited_count', 4),  # Default to 4 if not traced
                'phase2_cache': 'HIT' in phase2_log['cache_status'],
                'speedup': phase1_log['rtt_ms'] / phase2_log['rtt_ms'] if phase2_log['rtt_ms'] > 0 else 0
            })
    
    if len(comparison_data) < 10:
        print(f"[WARNING] Only {len(comparison_data)} domains available for comparison")
    
    print(f"[*] Analyzing {len(comparison_data)} domains (Phase 1 vs Phase 2 comparison)")
    
    # Extract data for plotting
    domains = [d['domain'][:25] for d in comparison_data]  # Truncate long domains
    phase1_latencies = [d['phase1_rtt'] for d in comparison_data]
    phase2_latencies = [d['phase2_rtt'] for d in comparison_data]
    phase1_servers = [d['phase1_servers'] for d in comparison_data]
    cache_hits = [d['phase2_cache'] for d in comparison_data]
    speedups = [d['speedup'] for d in comparison_data]
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Latency Comparison (Phase 1 vs Phase 2)
    x = np.arange(len(domains))
    width = 0.35
    
    bars1_p1 = ax1.bar(x - width/2, phase1_latencies, width, label='Phase 1 (Cache MISS)', 
                       color='#e74c3c', alpha=0.8)
    bars1_p2 = ax1.bar(x + width/2, phase2_latencies, width, label='Phase 2 (Cache HIT)', 
                       color='#27ae60', alpha=0.8)
    
    ax1.set_xlabel('Domain', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('DNS Query Latency: Phase 1 (Initial) vs Phase 2 (Cached) - First 10 H1 Re-queried Domains', 
                  fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(domains, rotation=45, ha='right')
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add speedup labels
    for i, (p1, p2, speedup) in enumerate(zip(phase1_latencies, phase2_latencies, speedups)):
        ax1.text(i, max(p1, p2) + 5, f'{speedup:.1f}x', ha='center', va='bottom', 
                fontsize=8, fontweight='bold', color='#2c3e50')
    
    # Plot 2: DNS Servers Visited (Phase 1 vs Phase 2)
    bars2_p1 = ax2.bar(x - width/2, phase1_servers, width, label='Phase 1 (Full Recursive)', 
                       color='#e74c3c', alpha=0.8)
    phase2_servers = [1 if hit else 4 for hit in cache_hits]  # 1 for cache, 4 for miss
    bars2_p2 = ax2.bar(x + width/2, phase2_servers, width, label='Phase 2 (From Cache)', 
                       color='#27ae60', alpha=0.8)
    
    ax2.set_xlabel('Domain', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of DNS Servers', fontsize=12, fontweight='bold')
    ax2.set_title('DNS Servers Contacted: Phase 1 vs Phase 2 - Cache Efficiency', 
                  fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(domains, rotation=45, ha='right')
    ax2.legend(fontsize=10)
    ax2.set_yticks(range(0, 6))
    ax2.grid(axis='y', alpha=0.3)
    
    # Add server count labels
    for i, (p1, p2) in enumerate(zip(phase1_servers, phase2_servers)):
        ax2.text(i - width/2, p1 + 0.1, str(p1), ha='center', va='bottom', fontsize=9)
        ax2.text(i + width/2, p2 + 0.1, str(p2), ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_plot = 'results/part_d_plots.png'
    plt.savefig(output_plot, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Plots saved: {output_plot}")
    
    # Print detailed analysis
    print("\n" + "="*80)
    print("DETAILED ANALYSIS - Phase 1 vs Phase 2 Comparison")
    print("="*80)
    print(f"\n{'#':<3} {'Domain':<30} {'Phase 1':<12} {'Phase 2':<12} {'Speedup':<10} {'Servers (P1→P2)':<15}")
    print("-"*90)
    
    for i, d in enumerate(comparison_data, 1):
        p1_servers = d['phase1_servers']
        p2_servers = 1 if d['phase2_cache'] else 4
        print(f"{i:<3} {d['domain']:<30} {d['phase1_rtt']:>6.1f} ms    {d['phase2_rtt']:>6.1f} ms    "
              f"{d['speedup']:>6.1f}x    {p1_servers} → {p2_servers}")
    
    # Statistics
    avg_p1 = sum(d['phase1_rtt'] for d in comparison_data) / len(comparison_data)
    avg_p2 = sum(d['phase2_rtt'] for d in comparison_data) / len(comparison_data)
    avg_speedup = sum(d['speedup'] for d in comparison_data) / len(comparison_data)
    cache_hit_count = sum(1 for d in comparison_data if d['phase2_cache'])
    
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Average Latency (Phase 1):     {avg_p1:.2f} ms")
    print(f"Average Latency (Phase 2):     {avg_p2:.2f} ms")
    print(f"Average Speedup:               {avg_speedup:.2f}x")
    print(f"Phase 2 Cache Hits:            {cache_hit_count}/{len(comparison_data)} ({cache_hit_count/len(comparison_data)*100:.0f}%)")
    print(f"Latency Reduction:             {(1 - avg_p2/avg_p1)*100:.0f}%")
    
    # Compare with Part B if available
    print("\n" + "="*80)
    print("COMPARISON: Part D vs Part B")
    print("="*80)
    
    if os.path.exists('part_b_summary.txt'):
        print("\nPart B used direct/NAT DNS (8.8.8.8)")
        print("Part D uses custom resolver (10.0.0.5) with caching")
        print("\nKey Differences:")
        print("  - Part D has caching capability (reduces latency for repeated queries)")
        print("  - Part D routes all traffic through custom resolver")
        print("  - Part D allows local DNS control and monitoring")
    else:
        print("\n[NOTE] Part B summary not found for comparison")
    
    # Save detailed report
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("PART D: Detailed Analysis Report - Phase 1 vs Phase 2 Comparison")
    report_lines.append("="*80)
    report_lines.append("\nFirst 10 Re-queried Domains from H1:")
    report_lines.append("-"*80)
    
    for i, d in enumerate(comparison_data, 1):
        # Find the Phase 1 log for detailed info
        phase1_log = next((log for log in h1_phase1 if log['domain'] == d['domain']), None)
        phase2_log = next((log for log in h1_phase2 if log['domain'] == d['domain']), None)
        
        report_lines.append(f"\n{i}. {d['domain']}")
        report_lines.append(f"   PHASE 1 (Initial Query - Cache MISS):")
        if phase1_log:
            report_lines.append(f"      Resolution Mode:  {phase1_log['resolution_mode']}")
            report_lines.append(f"      DNS Server:       {phase1_log['dns_server']}")
            report_lines.append(f"      Resolution Step:  {phase1_log['resolution_step']}")
            
            # Show full resolution path if traced
            if 'full_resolution_path' in phase1_log and phase1_log['full_resolution_path']:
                report_lines.append(f"      Full Resolution Path (Traced):")
                for step in phase1_log['full_resolution_path']:
                    report_lines.append(f"         → {step}")
                report_lines.append(f"      Servers Visited:  {phase1_log['servers_visited_count']} (traced)")
            else:
                report_lines.append(f"      Servers Visited:  4 (estimated)")
            
            report_lines.append(f"      Response:         {phase1_log['response']}")
            report_lines.append(f"      RTT:              {phase1_log['rtt_ms']} ms")
            report_lines.append(f"      Total Time:       {phase1_log['total_time_ms']} ms")
        
        report_lines.append(f"\n   PHASE 2 (Re-query - Cache {'HIT' if d['phase2_cache'] else 'MISS'}):")
        if phase2_log:
            report_lines.append(f"      Resolution Step:  {phase2_log['resolution_step']}")
            report_lines.append(f"      Servers Visited:  {1 if d['phase2_cache'] else 4}")
            report_lines.append(f"      Response:         {phase2_log['response']}")
            report_lines.append(f"      RTT:              {phase2_log['rtt_ms']} ms")
            report_lines.append(f"      Total Time:       {phase2_log['total_time_ms']} ms")
            report_lines.append(f"      Speedup:          {d['speedup']:.1f}x faster")
            report_lines.append(f"      Latency Reduction: {(1 - d['phase2_rtt']/d['phase1_rtt'])*100:.0f}%")
    
    report_lines.append("\n" + "="*80)
    report_lines.append("Summary Statistics:")
    report_lines.append(f"  Average Phase 1 Latency:   {avg_p1:.2f} ms")
    report_lines.append(f"  Average Phase 2 Latency:   {avg_p2:.2f} ms")
    report_lines.append(f"  Average Speedup:           {avg_speedup:.2f}x")
    report_lines.append(f"  Cache Hit Rate (Phase 2):  {cache_hit_count}/{len(comparison_data)} ({cache_hit_count/len(comparison_data)*100:.0f}%)")
    report_lines.append(f"  Overall Latency Reduction: {(1 - avg_p2/avg_p1)*100:.0f}%")
    report_lines.append("="*80)
    
    report_file = 'results/part_d_analysis_report.txt'
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n[OK] Report saved: {report_file}")
    
    print("\n" + "="*80)
    print("Analysis Complete!")
    print("="*80)
    print("\nGenerated files in results/:")
    print("  - part_d_plots.png (visualization)")
    print("  - part_d_analysis_report.txt (detailed report)")
    print("="*80 + "\n")

if __name__ == '__main__':
    analyze_part_d()
