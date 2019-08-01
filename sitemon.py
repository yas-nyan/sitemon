from lib.monitor import Monitor
from lib.slack import Slack
from multiprocessing.pool import ThreadPool as Pool
from config import *
from python_hosts.hosts import Hosts, HostsEntry
import time
from datetime import datetime
import yaml


def nextCycle(monitor):
    return monitor.cycle()


def slackNotification(slack, result):
    username = SLACK_USERNAME
    icon = SLACK_SUCCESS_ICON if result["status"] else SLACK_FAILED_ICON
    now_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    text = f"[{now_string}] STATE CHANGED: {result['name']} \n Monitor target: {result['target']} ({result['monitor_type']})\n current state: {'up' if result['status'] else 'down' }"

    slack.notify(text=text, icon_emoji=icon, username=username)


def changedEvent(result):
    # slack notification
    if 'SLACK_URL' in globals():
        slack = Slack(url=SLACK_URL)
        slackNotification(slack, result)
    print(f"CHANGED: {result['name']}  {result['target']}")


if __name__ == "__main__":
    hosts = []
    with open(HOST_FILE_PATH, "r") as f:
        '''
        - monitor_targets:
            ipv4: 8.8.8.8
            ipv6: 2001:4860:4860::8888
        name: googleDNS
        '''
        hosts = yaml.safe_load(f)

    # マルチプロス用の引数群
    parameters = []

    for host in hosts:
        name = host["name"]
        for target_key, target_value in host["monitor_targets"].items():
            # 種別ごとにパラメーターに追加する。
            monitor_type = ""
            if target_key in ("ipv4", "ipv6"):
                monitor_type = "fping" if USE_FPING else "ping"
            else:
                monitor_type = target_key

            parameter = {
                "name": name,
                "target": target_value,
                "monitor_type": monitor_type,
                "TLS_CERT_EXPIRATION_DATES": TLS_CERT_EXPIRATION_DATES if "TLS_CERT_EXPIRATION_DATES" in globals() else 7  # default 7 days
            }

            parameters.append(parameter)

    # generate monitors
    monitors = [Monitor(parameter) for parameter in parameters]

    # status chache table
    privious_status = {}
    for monitor in monitors:
        privious_status[str(monitor.id)] = monitor.status

    while True:
        print(
            f'[{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}] Cycle start monitortargets: {len(parameters)} host')

        with Pool(PROCESS_POOL) as pool:
            all_result = []
            # monitorsは各プロセス用にハードコピーされる。そのためchangedは更新されるはずがない。
            for result in pool.imap_unordered(nextCycle, monitors):
                # 前回のステータスと比較して
                if result["status"] != privious_status[str(result["id"])]:
                    changedEvent(result)

                # ステータス更新
                privious_status[str(result["id"])] = result["status"]

        if SLEEP_TIME > 0:
            time.sleep(SLEEP_TIME)
