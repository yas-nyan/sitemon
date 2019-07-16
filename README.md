# sitemon


## config.py
```
HOST_FILE_PATH = "hosts.d/target_hosts"
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