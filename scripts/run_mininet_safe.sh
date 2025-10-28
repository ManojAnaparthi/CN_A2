#!/bin/bash
# Backup VM DNS before running Mininet, restore after
# Run from project root: ./scripts/run_mininet_safe.sh

echo "================================================================================"
echo "DNS Protection Script for Mininet"
echo "================================================================================"

# Backup current DNS
echo "[1/4] Backing up current DNS configuration..."
sudo cp /etc/resolv.conf /tmp/vm_resolv.conf.backup
cat /etc/resolv.conf | grep nameserver
echo ""

# Run Mininet
echo "[2/4] Starting Mininet..."
echo "        You can now run Part C and Part D"
echo "        When done, type 'exit' in Mininet CLI"
echo ""
sudo mn --custom as2dns.py --topo dnsline --nat

# Restore DNS after Mininet exits
echo ""
echo "[3/4] Mininet exited. Restoring VM DNS..."
sudo cp /tmp/vm_resolv.conf.backup /etc/resolv.conf
echo ""

echo "[4/4] Verification:"
echo "VM DNS is now:"
cat /etc/resolv.conf | grep nameserver
echo ""

echo "================================================================================"
echo "Done! Your VM DNS has been restored."
echo "================================================================================"
