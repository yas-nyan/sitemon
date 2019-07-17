# sitemon

## target file format
```
- monitor_targets:
    ipv4: 8.8.8.8
    ipv6: 2001:4860:4860::8888
  name: googleDNS
- monitor_targets:
    ipv4: 1.1.1.1
    ipv6: 2606:4700:4700::1111
  name: cloudflare
```

## config.py
```
HOST_FILE_PATH = "hosts.d/hosts.yml"
PROCESS_POOL = 16

USE_FPING = True
SLEEP_TIME = 5  # seconds


# For slack notification
# SLACK_URL = ""
# SLACK_USERNAME = "GENBA Cat"
# SLACK_FAILED_ICON = ":genbaneko_moving:"
# SLACK_SUCCESS_ICON = ":genbaneko:"
```

## start
```
pipenv install
pipenv run sitemon
```
