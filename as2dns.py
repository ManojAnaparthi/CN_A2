from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.cli import CLI

class DNSLinear(Topo):
    def build(self):
        # Hosts with fixed IPs
        h1 = self.addHost('h1', ip='10.0.0.1/24')  # H1
        h2 = self.addHost('h2', ip='10.0.0.2/24')  # H2
        h3 = self.addHost('h3', ip='10.0.0.3/24')  # H3
        h4 = self.addHost('h4', ip='10.0.0.4/24')  # H4
        dns = self.addHost('dns', ip='10.0.0.5/24')  # DNS Resolver

        # Switches S1—S4
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Access links host<->switch (100 Mbps, 2 ms)
        self.addLink(h1, s1, cls=TCLink, bw=100, delay='2ms')
        self.addLink(h2, s2, cls=TCLink, bw=100, delay='2ms')
        self.addLink(h3, s3, cls=TCLink, bw=100, delay='2ms')
        self.addLink(h4, s4, cls=TCLink, bw=100, delay='2ms')
        # DNS vertical link from S2 (100 Mbps, 1 ms)
        self.addLink(dns, s2, cls=TCLink, bw=100, delay='1ms')

        # Switch<–>switch links left to right
        self.addLink(s1, s2, cls=TCLink, bw=100, delay='5ms')
        self.addLink(s2, s3, cls=TCLink, bw=100, delay='8ms')
        self.addLink(s3, s4, cls=TCLink, bw=100, delay='10ms')

topos = {'dnsline': (lambda: DNSLinear())}
