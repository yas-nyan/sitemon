import socket
import dns.resolver
import dns.reversename
import subprocess


class dig:
    @classmethod
    def getv4(cls, name):
        try:
            return cls.query(name, "A")
        except:
            # somtiong error occurs
            return None

    @classmethod
    def getv6(cls, name):
        try:
            return cls.query(name, "AAAA")
        except:
            # somtiong error occurs
            return None

    @classmethod
    def getPTR(cls, name):
        try:
            return cls.query(name, "PTR")
        except:
            # somtiong error occurs
            return None

    @staticmethod
    def query(data, option):
        result = ""
        if "PTR" in option:
            data = dns.reversename.from_address(data).to_text()
        # Basic query
        for rdata in dns.resolver.query(data, option):
            result = rdata.to_text()

        return result
