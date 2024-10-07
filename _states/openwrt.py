# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals


def config_set(name=None, value=None):
    """
    Manage openwrt UCI named key config
    If value is different, set config value and commit config

    name
        UCI key to manage

    value
        Set UCI key to value
    """

    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    if name is None:
        ret["result"] = False
        ret["comment"] = "Must provide name to openwrt.config_set"
        return ret

    if value is None:
        ret["result"] = False
        ret["comment"] = "Must provide value to openwrt.config_set"
        return ret

    # openwrt: UCI values are strings
    value = str(value)

    openwrt_ret  = __salt__["openwrt.config_get"](name)
    if openwrt_ret == value:
        ret["result"] = True
        ret["comment"] = "UCI key {} already set to {}".format(name, value)
        return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "UCI key {} will change to {}".format(name, value)
        return ret

    openwrt_ret = __salt__["openwrt.config_set"](name, value)
    if openwrt_ret == True:
        ret["result"] = True
        ret["changes"] = {"value": "updated"}
        ret["comment"] = "UCI key {} changed to {}".format(name, value)
        return ret

    ret["comment"] = "Failed to change UCI key {} to {}".format(name, value)
    return ret
