import subprocess
import ipaddress
import os
import requests
from requests.exceptions import ConnectionError


class Monitor:
    '''
    class Monitor:
    sst name: name
    str monitor_type:  [
        "ping",
        "ping6",
        "http"
    ]
    str target: IPv4 Addr / IPv6 addr / http URL

    '''
    AVAILABLE_TYPES = ("ping", "ping6", "fping", "http")

    def __init__(self, parameters):
        self.name = parameters["name"]
        self.status = True  # initial value is True
        self.id = id(self)

        if parameters["monitor_type"] in self.AVAILABLE_TYPES:
            self.monitor_type = parameters["monitor_type"]
        else:
            raise ValueError(f"monitor type : {self.AVAILABLE_TYPES}")

        # add http://
        if self.monitor_type == "http" and not self.isValidHTTPURL(parameters["target"]):
            self.target = "http://" + parameters["target"]
        else:
            self.target = parameters["target"]

    def cycle(self):
        if self.monitor_type == "ping":
            addr_type = self.whichIPAddr(self.target)
            if addr_type is 4:
                status = self.isPingOK()
            elif addr_type is 6:
                status = self.isPingOK(isv6=True)
            else:
                # domain name not implemented
                raise NotImplementedError(
                    "domain name resolve is not implemented")
        elif self.monitor_type == "fping":
            status = self.isPingOK(usefping=True)
        elif self.monitor_type == "http":
            # http://が頭についてない場合つける
            status = self.isHTTPOK()

        self.status = status

        return self.__dict__
        '''
        self.__dict__ -> {
            "status": status,
            "name": self.name,
            "target": self.target,
            "monitor_type": self.monitor_type
        }
        '''

    def isPingOK(self, isv6=False, usefping=False):
        if not self.whichIPAddr(self.target):
            raise ValueError(f"target: {self.target} is not valid ip addr")

        if usefping is True:
            ping_func = "fping"
            options = "-q -i 0.2 -r 10"
        else:
            ping_func = "ping6" if isv6 else "ping"
            options = "-i 0.2 -c 10"

        response = subprocess.call(
            f"{ping_func} {options} {self.target}", shell=True, stdout=open(os.devnull, 'wb'))

        return True if response == 0 else False

    def isHTTPOK(self):
        with requests.Session() as s:
            try:
                response = s.get(self.target)
                return response.status_code == requests.codes.ok
            except ConnectionError:
                return False

    @classmethod
    def whichIPAddr(cls, target):
        try:
            addr = ipaddress.ip_address(target)
            return addr.version

        except ValueError:
            return False

        return False

    @classmethod
    def isValidHTTPURL(cls, url):
        return url.startswith("http://") or url.startswith("https://")
