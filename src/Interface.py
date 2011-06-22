import subprocess
import re
from random import randint
from sys import platform
find_ip_regexp = re.compile(r'.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

OSX = ['darwin']
LINUX = ['linux2', 'linux']
WINDOWS = ['win32']

def get_ip_address(ifname):
    """
    Returns ip address from local machine. interface name is given as an parameter.
    get_ip_address | <interface>
    e.g. get_ip_address | eth0
    """
    if platform in WINDOWS:
        return _get_windows_ip(ifname)
    process = subprocess.Popen([__get_ifconfig_cmd(), ifname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    return __return_ip_address_from_ifconfig_output(output)

def create_interface_alias(ifname, ip_address, netmask):
    """ Creates interface """
    virtual_if_name = __get_free_interface_alias(ifname)
    print "ifconfig", virtual_if_name, ip_address, "netmask", netmask
    if platform in OSX:
        process = subprocess.Popen([__get_ifconfig_cmd(), virtual_if_name, 'alias', ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen([__get_ifconfig_cmd(), virtual_if_name, ip_address, "netmask", netmask], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return virtual_if_name

def check_interface(ifname):
    """Checks if interface have ip address. Returns False or True"""
    ipaddress= get_ip_address(ifname)
    print "ipaddress=" + ipaddress 
    return ipaddress != ""

def check_interface_for_ip(ifname, ip):
    """checks given network interface for given ip address"""
    cmd = [__get_ifconfig_cmd()]
    if platform not in WINDOWS:
        cmd.append(ifname)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    ips=__return_ip_addresses_from_ifconfig_output(output)
    print ips
    return ip in ips

def del_alias(ifname, ip):
    """Deletes this interface"""
    print "ifconfig", ifname, "down"
    if platform in OSX:
        process = subprocess.Popen([__get_ifconfig_cmd(), ifname, '-alias', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen([__get_ifconfig_cmd(), ifname, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

def __return_ip_addresses_from_ifconfig_output(output):
    addresses = []
    if platform in WINDOWS:
        return ['127.0.0.1']
    else:
        for line in output.split('\n'):
            if 'inet ' in line or 'IPv4 Address' in line:
                ipAddress = find_ip_regexp.match(line).group(1)
                print "ip address is:" + ipAddress
                addresses.append(ipAddress)
        return addresses

def __return_ip_address_from_ifconfig_output(output):
    addresses = __return_ip_addresses_from_ifconfig_output(output)
    if addresses == []:
        return ''
    else:
        return addresses[0]

def __get_free_interface_alias(ifname):
    if platform in OSX: 
        return ifname
    else:
        while True:
            virtual_if_name = ifname + ":" + str(randint(1, 10000))
            if not check_interface(virtual_if_name):
                return virtual_if_name

def __get_ifconfig_cmd():
    if platform in OSX:
        return '/sbin/ifconfig'
    elif platform in WINDOWS:
        return 'ipconfig'
    else:
        return '/sbin/ifconfig'

def _get_windows_ip(ifname):
    process = subprocess.Popen(["ipconfig"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0]
    lines = output.split('\n')
    for number, line in enumerate(lines):
        if "Ethernet adapter" in line and ifname in line:
            for i_line in lines[number+2:]:
                if i_line is '\n':
                    break
                if "IPv4 Address" in i_line:
                    ip = find_ip_regexp.match(i_line).group(1)
                    return ip

