# import yaml
import argparse
from copy import copy
from multiprocessing.pool import ThreadPool as Pool
import subprocess
from unittest import result
import yaml
import time
from datetime import datetime
from slack_sdk.webhook import WebhookClient
from slack_sdk.models.attachments import Attachment
from logzero import logger
import logzero
import os


DEFAULT = {
    "timeoutSeconds": 1,
    "intervalSecond": 0.2,
    "retryCount": 3,
    "dnsSearchDomain": "example.com",
    "processPoolCount": 16,
    "sleepTimeSeconds": 5
}
COMMANDS = {}



def localExcute(command: str) -> bool:
    try: 
        logger.debug(command)
        subprocess.run(command, shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.debug(e)
        return False

def check(target: dict) -> dict: 
    '''
    target = {
        "name": "example",
        "value": "example.com",
        "type: "icmp",
        "lastStatus": bool,
    }
    result = {
        "name": "example",
        "value": "example.com",
        "type: "icmp",
        "lastStatus": bool,
        "status": bool
    }

    '''
    if not target["type"] in COMMANDS.keys():
        raise NotImplementedError(f'{target["type"]} is not implemented')
    result = copy(target)
    cmd = f'{COMMANDS[target["type"]]}{target["value"]}'

    result["status"] = localExcute(cmd)

    return result

def slackNotification(result,slack_webhook):
    now_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    title = f'Sitemon detected: "{result["name"]}" is {"UP" if result["status"] else "DOWN"}'
    text = f"Name: {result['name']} \n {result['value']} ({result['type']})\n current state: {'UP' if result['status'] else 'DOWN' }"
    color = "good" if result["status"] else "danger"

    attachment = Attachment(text=text,color=color,footer=now_string,title=title)

    response = slack_webhook.send(attachments=[attachment])
    if response.status_code != 200 :
        logger.warning(f"Slack webhook send failed. status: {response.status_code} body: {response.body}")
    else:
        logger.info("slack notification send.")


def getFullOptions(options: dict={}):

    outputOptions = {}
    for key, value in DEFAULT.items(): 
        if key in options.keys():
            # user selected value
            outputOptions[key] = options[key]
        else:
            outputOptions[key] = value
    
    return outputOptions
    
    


if __name__ == "__main__":
    if "SITEMON_DEBUG" in  os.environ: 
        logzero.loglevel(logzero.DEBUG)
    else:
        logzero.loglevel(logzero.INFO)
    # parse args
    parser = argparse.ArgumentParser("sitemon options")
    parser.add_argument("config", help="configuration file path")
    args = parser.parse_args()

    config = None
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    if "options" in config.keys():
        options = getFullOptions(options=config["options"])
    else:
        options = getFullOptions()

    COMMANDS = {
        # last character must be space or @
        "http": f"curl --connect-timeout {options['timeoutSeconds']} -I ",
        "icmp": f"fping -q -i {options['intervalSecond']} -r {options['retryCount']}  -t {options['timeoutSeconds']} ",
        "dns": f"dig +time={options['timeoutSeconds']} +tries={options['retryCount']}  {options['dnsSearchDomain']} @"
    }

    logger.debug("Full command")
    logger.debug(COMMANDS)


    # set slack
    try:
        webhook = WebhookClient(config["slack"]["url"])
    except Exception as e:
        logger.info("slack disabled. continue")
        webhook = None
    # set sleep time
    
    targets = copy(config["targets"])

    # set initial status
    for target in targets:
        target["lastStatus"]  = True
    while True:
        logger.info(f"Sitemon cycle start. count: {len(targets)}")
        with Pool(options["processPoolCount"]) as pool:
            all_result = []
            # monitorsは各プロセス用にハードコピーされる。そのためchangedは更新されるはずがない。
            for result in pool.imap_unordered(check, targets):
                all_result.append(result)
            
            # changed check
            for result in all_result:
                # 前回のステータスと比較
                if result["status"] != result["lastStatus"]:
                    logger.info(f"[CHANGED] name:{result['name']}  value:{result['value']} type:{result['type']}")
                    if webhook is not None:
                        slackNotification(result,webhook)

                # ステータス更新
                result["lastStatus"] = result["status"]
                # 今回のステータス削除
                result.pop("status")
        # 次のtargetsを更新
        targets = all_result
        if options["sleepTimeSeconds"] > 0:
            time.sleep(options["sleepTimeSeconds"])