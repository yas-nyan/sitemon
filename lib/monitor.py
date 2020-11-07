import subprocess
import ipaddress
import os
import requests
from requests.exceptions import ConnectionError
from datetime import datetime, timedelta
import ssl
import OpenSSL
import socket
socket.setdefaulttimeout(3)  # ハードコーディングでタイムアウト設定


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
    AVAILABLE_TYPES = ("ping", "ping6", "fping", "http", "tls")

    def __init__(self, parameters):
        self.name = parameters["name"]
        self.status = True  # initial value is True
        self.id = id(self)

        if parameters["monitor_type"] in self.AVAILABLE_TYPES:
            self.monitor_type = parameters["monitor_type"]
        else:
            raise ValueError(f"monitor type : {self.AVAILABLE_TYPES}")

        if self.monitor_type == "http":
            # HTTP
            if not self.isValidHTTPURL(parameters["target"]):
                # add http://
                self.target = "http://" + parameters["target"]
            else:
                self.target = parameters["target"]
            self.isHTTPS = True if "https://" in self.target else False
        elif self.monitor_type == "tls":
            # TLS
            _splited = parameters["target"].split(":")  # ["example.com","443"]
            if not self.isValidPort(_splited[1]) or len(_splited) != 2:
                raise ValueError(
                    f"tls target is invalid: {parameters['target']}")

            self.target = _splited[0]
            self.target_port = _splited[1]
            # 証明書の有効期限確認用
            self.TLS_CERT_EXPIRATION_DATES = parameters["TLS_CERT_EXPIRATION_DATES"]
        else:
            # ping
            self.target = parameters["target"]

    def cycle(self):
        if self.monitor_type == "ping":
            addr_type = self.whichIPAddr(self.target)
            if addr_type ==  4:
                status = self.isPingOK()
            elif addr_type == 6:
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
        elif self.monitor_type == "tls":
            status = self.isTLSOK()
        else:
            raise NotImplementedError(
                f"{self.monitor_type} is not implemented")

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
        if self.isHTTPS:
            print(f"{self.target} is HTTPS")

        with requests.Session() as s:
            try:
                response = s.get(self.target, verify=self.isHTTPS)
                return response.status_code == requests.codes.ok
            except ConnectionError:
                return False

    def isTLSOK(self):
        try:
            cert = ssl.get_server_certificate((self.target, self.target_port))
            # 証明書の形に変換
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert)
            start_datetime = datetime.strptime(
                x509.get_notBefore().decode(), '%Y%m%d%H%M%SZ')
            end_datetime = datetime.strptime(
                x509.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
            valid_datetime = datetime.now() + timedelta(days=7)
            # 有効期限確認
            if end_datetime <= valid_datetime:
                raise ValueError("")
            else:
                return True

        except ConnectionError:
            print(f"TLS: {self.target}:{self.port} connection error ")
            return False
        except ValueError:
            print(f"TLS: {self.target}:{self.port} expiration date error ")
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

    @classmethod
    def isValidPort(cls, port_text):
        try:
            port = int(port_text)
            if 0 < port and port < 65535:
                return True
            else:
                return False
        except ValueError:
            return False
