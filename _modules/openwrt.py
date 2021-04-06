# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import Salt Libs
import salt.utils.platform

log = logging.getLogger(__name__)

__virtualname__ = 'openwrt'

def __virtual__():
    '''
    Will load for the openwrt proxy minions.
    '''
    try:
        if salt.utils.platform.is_proxy() and \
           __opts__['proxy']['proxytype'] == 'openwrt':
            return __virtualname__
    except KeyError:
        pass

    return False, 'The openwrt execution module can only be loaded for openwrt proxy minions.'


def update_pkgs():
    '''
    Update the list of available packages
    '''
    _, _, ret = __proxy__['openwrt.ssh_check']('opkg update')
    return ret == 0

def list_pkgs():
    '''
    Retrieve a list of installed packages from the openwrt host
    '''
    pkgs = {}
    out, _, ret = __proxy__['openwrt.ssh_check']('opkg list-installed')
    if ret == 0:
        for line in out.split('\n'):
            pkg, version = line.split(' - ')
            pkgs[pkg] = version
    return pkgs

def remove_pkg(pkg):
    '''
    Remove an installed package
    '''
    _, _, ret = __proxy__['openwrt.ssh_check']('opkg remove %s' % (pkg,))
    return ret == 0


def network_restart():
    '''
    Restart the network, reconfigures all interfaces
    '''
    _, _, ret = __proxy__['openwrt.ssh_check']('/etc/init.d/network restart')
    return ret == 0

def network_reload():
    '''
    Reload the network, reload interfaces as needed
    '''
    _, err, ret = __proxy__['openwrt.ssh_check']('/etc/init.d/network reload')
    return ret == 0

def interface_list():
    '''
    Fetch a list of existing interfaces
    '''
    intfs = []
    out, _, ret = __proxy__['openwrt.ssh_check']('ubus list')
    if ret == 0:
        for line in out.split('\n'):
            if line.startswith('network.interface.'):
                intfs.append('.'.join(line.split('.')[2:]))
        return intfs
    return False


def network_dev_status(intf):
    '''
    Dump hardware state and counters of given network device ifname
    '''
    return __proxy__['openwrt.ubus']('network.device', 'status', {'name': intf})


def interface_status(intf):
    '''
    Dump network configuration of given network device ifname
    '''
    return __proxy__['openwrt.ubus']('network.interface.%s' % (intf,), 'status')


def config_dump():
    '''
    Dump the whole uci config tree
    '''
    out, err, ret =  __proxy__['openwrt.ssh_check']('uci show')
    if ret != 0:
        return False
    return _parse_uci(out)

def config_get(key):
    '''
    Return uci value for key
    '''
    out, _, ret =  __proxy__['openwrt.ssh_check']('uci get {}'.format(key))
    if ret == 0:
        return out
    return False


def config_set(key, value):
    '''
    Set uci value for key and commit config
    '''
    _, _, ret =  __proxy__['openwrt.ssh_check']('uci set {}={}'.format(key, value))
    if ret != 0:
        return False

    _, _, ret =  __proxy__['openwrt.ssh_check']('uci commit')
    return ret == 0

def config_reload():
    '''
    Reload router configuration
    '''
    _, _, ret =  __proxy__['openwrt.ssh_check']('reload_config')
    return ret == 0

def _parse_uci(data):
    '''
    Parse the UCI output into a dict
    '''
    uci = {}
    for line in data.split('\n'):
        key, value = line.split('=', 1)
        path = key.split('.')
        uci[key] = value
    return uci


def run(command):
    '''
    Run command
    '''
    out, err, ret = __proxy__['openwrt.ssh_check'](command)
    return ({'stdout': out, 'stderr': err, 'exitcode': ret})


def reboot():
    '''
    Reboot openwrt device
    '''
    return __proxy__['openwrt.ubus']('system', 'reboot')
