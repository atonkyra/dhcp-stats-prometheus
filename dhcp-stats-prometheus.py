#!/usr/bin/env python3
import logging
import argparse
import bottle
from bottle import route, run, template, response
import subprocess
import json
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s %(levelname)-8s %(name)-12s %(message)s'
)
logger = logging.getLogger('dhcp-stats-prometheus')

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)
dhcpd_pools_educated_guess = "%s/external/dhcpd-pools" % (fullpath)
parser = argparse.ArgumentParser(description='dhcp pool stats exporter for prometheus')
parser.add_argument('-l', '--listen-address', required=False, help='listen-address', default='::')
parser.add_argument('-p', '--listen-port', required=False, help='listen-port', default=9991)
parser.add_argument('-b', '--binary', required=False, help='dhcpd-pools-binary', default=dhcpd_pools_educated_guess)
parser.add_argument('-c4', '--dhcp4-config', required=False, help='dhcp4 config path', default='/etc/dhcp/dhcpd.conf')
parser.add_argument('-c6', '--dhcp6-config', required=False, help='dhcp6 config path', default='/etc/dhcp/dhcpd6.conf')
parser.add_argument('-l4', '--dhcp4-leases', required=False, help='dhcp4 leases path', default='/var/lib/dhcp/dhcpd.leases')
parser.add_argument('-l6', '--dhcp6-leases', required=False, help='dhcp6 leases path', default='/var/lib/dhcp/dhcpd6.leases')
args = parser.parse_args()

def exec_command(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('ascii', errors='ignore')

@route('/metrics')
def prometheus_metrics():
    dhcpstat = json.loads(exec_command([args.binary, '-c', args.dhcp4_config, '-l', args.dhcp4_leases, '-f', 'j']))
    dhcp6stat = json.loads(exec_command([args.binary, '-c', args.dhcp6_config, '-l', args.dhcp6_leases, '-f', 'j']))
    data = []
    for shared_network in dhcpstat['shared-networks']:
        data.append('dhcp_pool_used{ip_version="%s",network="%s"} %s' % (4,shared_network['location'],shared_network['used']))
        data.append('dhcp_pool_free{ip_version="%s",network="%s"} %s' % (4,shared_network['location'],shared_network['free']))
        data.append('dhcp_pool_usage{ip_version="%s",network="%s"} %s' % (4,shared_network['location'],float(shared_network['used'])/float(shared_network['defined'])))
    for shared_network in dhcp6stat['shared-networks']:
        data.append('dhcp_pool_used{ip_version="%s",network="%s"} %s' % (6,shared_network['location'],shared_network['used']))
        data.append('dhcp_pool_free{ip_version="%s",network="%s"} %s' % (6,shared_network['location'],shared_network['free']))
        data.append('dhcp_pool_usage{ip_version="%s",network="%s"} %s' % (6,shared_network['location'],float(shared_network['used'])/float(shared_network['defined'])))
    response.content_type = 'text/plain'
    return '%s\n' % ('\n'.join(data))

run(host=args.listen_address, port=9991)
