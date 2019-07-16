from lib.monitor import Monitor
from lib.slack import Slack
from multiprocessing import Pool
from config import *
from python_hosts.hosts import Hosts, HostsEntry
import time
from datetime import datetime


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

    # generate monitors
    monitors = [Monitor(parameter) for parameter in parameters]

    # status chache table
    privious_status = {}
    for monitor in monitors:
        privious_status[str(monitor.id)] = monitor.status

    while True:
        print(f'[{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}] Cycle start')

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
