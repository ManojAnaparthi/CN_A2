#!/bin/bash
# Restore original DNS configuration

echo "Restoring original DNS configuration..."
sudo rm /etc/resolv.conf
sudo ln -s /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

echo "DNS restored to systemd-resolved!"
