# dhcp-stats-prometheus
Prometheus exporter for DHCP stats, uses dhcpd-pools to fetch stats. I have included a pre-built dhcpd-pools with the package but nothing stops you from compiling your own version yourself.

You may acquire dhcpd-pools from http://dhcpd-pools.sourceforge.net/ for your own compiling needs. Debian stretch also seems to include a version of dhcpd-pools.

## Usage
```
./dhcp-stats-prometheus.py -R 10.0.0.1 -R fd00:1337::1 -p 12331 -b /usr/bin/dhcpd-pools
```

## Configuring ISC-DHCP server and interpreting results
dhcpd.conf should be split into shared-network declarations to get sane names for the subnets, see example below:
```
shared-network vlan200 {
  subnet 10.0.0.0 netmask 255.255.255.0 {
    ... your subnet declarations here ...
  }
}
```

## Exported information
Above configuration should yield following export. Used is number of leases in use, free is number of leases free and usage is percentage [0-1.0] of the used leases.
```
dhcp_pool_used{ip_version="4",network="vlan200-party"} 1
dhcp_pool_free{ip_version="4",network="vlan200-party"} 1002
dhcp_pool_usage{ip_version="4",network="vlan200-party"} 0.0009970089730807576
dhcp_pool_used{ip_version="6",network="vlan200-party"} 0
dhcp_pool_free{ip_version="6",network="vlan200-party"} 65535
dhcp_pool_usage{ip_version="6",network="vlan200-party"} 0.0
```
