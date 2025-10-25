#!/bin/bash
# Fix DNS for Mininet by temporarily switching away from systemd-resolved stub

echo "Backing up current resolv.conf..."
sudo cp -L /etc/resolv.conf /etc/resolv.conf.backup

echo "Switching to Google DNS..."
sudo rm /etc/resolv.conf
sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
sudo bash -c 'echo "nameserver 8.8.4.4" >> /etc/resolv.conf'

echo "DNS fixed! Now run:"
echo "  sudo mn --custom as2dns.py --topo dnsline --nat"
echo ""
echo "After exiting Mininet, restore DNS with:"
echo "  ./restore_dns.sh"
