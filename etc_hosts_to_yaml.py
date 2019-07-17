import yaml
from ..lib.monitor import Monitor
from ..lib.dig import dig
from python_hosts.hosts import Hosts, HostsEntry


'''
loaded_hosts = {}

with open("hosts.d/hosts.yml", "r") as f:
    loaded_hosts = yaml.safe_load(f)

print(loaded_hosts)

'''

hosts = Hosts(path="hosts.d/target_hosts").entries

yaml_hosts = []

for host in hosts:
    ipv6 = dig.getv6(dig.getPTR(host.address))
    record = {
        "name": host.names[0],
        "monitor_targets": {
            'ipv4': host.address
        }
    }
    if ipv6 is not None:
        record["monitor_targets"]['ipv6'] = ipv6

    yaml_hosts.append(record)
with open("hosts.d/hosts.yml", "w") as f:
    f.write(yaml.dump(yaml_hosts))
