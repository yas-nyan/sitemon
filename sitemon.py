from lib.monitor import Monitor
from multiprocessing import Pool
from config import *
from python_hosts.hosts import Hosts, HostsEntry


def genMonitor(parameter):
    '''
    parameter = {
        "name": task's name
        "target": target ip address or URL,
        "monitor_type": AVAILABLE_TYPES = ("ping", "ping6", "http")
    }
    '''
    mon = Monitor(parameter)

    return mon.cycle()


if __name__ == "__main__":
    hosts = Hosts(path=HOST_FILE_PATH).entries

    # マルチプロス用の引数群
    parameters = []

    for host in hosts:
        parameter = {
            "name": host.names[0],
            "target": host.address,
            "monitor_type": "fping" if USE_FPING else "ping"
        }
        parameters.append(parameter)

    with Pool(PROCESS_POOL) as pool:
        for result in pool.imap_unordered(genMonitor, parameters):
            print(result)
