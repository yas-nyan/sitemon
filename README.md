# sitemon
Simple and multithread monitoring deamon with python

## before starting
### For mac users
- please ensure ```OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES```
```
env | grep OBJC
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## config gile format
```yaml
slack: 
  url: URLURLURL
targets:
- name: example
  value: example.com
  type: http
- name: example-ip
  value: example.com
  type: icmp
- name: down host
  value: 2001:db8::1
  type: icmp
- name: GoogleDNS
  value: 2001:4860:4860::8888
  type: dns
```

tips: `etc_hosts_to_yaml.py` can convert hosts file to config format.


## install and start
### local

```
poetry install
```

```
python3 
```

### docker
```
docker compose up -d
```

## start
