# salt_openwrt
Saltstack openwrt proxy minion

Only works when multiprocessing is set in /etc/salt/proxy as follow:
```
multiprocessing: False
```

## Example

### Pillar config

```yaml
---

proxy:
  proxytype: openwrt
  host: a.b.c.d
  username: root
  password: SuperPassword!

openwrt_config:
  config:
    system.ntp.server: a.b.c.d
```

Password should be encrypted with GPG salt-master public key for security reasons


### Sample SLS state

```yaml

---

{% set openwrt_config = salt['pillar.get']('openwrt_config', default={}) %}

{% for c in openwrt_config.config|default({}) %}
openwrt-config-{{loop.index}}:
  openwrt.config_set:
    - name: {{c}}
    - value: {{openwrt_config.config[c]}}
    - watch_in:
        - openwrt-reload
{% endfor %}

openwrt-reload:
  module.wait:
    - name: openwrt.config_reload
```
