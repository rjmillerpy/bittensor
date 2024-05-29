import requests
import time
from datetime import datetime
import json
import argparse

from recycle_amount_parser import get_recycle_amount

slack_token = '<your-token-here>'
channel = '<your-channel-here>'


def get_args():
    parser = argparse.ArgumentParser(description="Process the netuid value.")
    parser.add_argument('--netuid', type=str, default='20', help='NetUID to use for fetching recycle amounts')
    args = parser.parse_args()
    return args


def send_notification(message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": message
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def update_cost(low, super_low):
    low = {"low": low, "super_low": super_low}
    with open('cost.json', 'w', encoding='utf-8') as cj_file:
        json.dump(low, cj_file)


def get_low():
    with open('cost.json', 'r', encoding='utf-8') as cj_file:
        low = json.load(cj_file)["low"]
    return low


def get_super_low():
    with open('cost.json', 'r', encoding='utf-8') as cj_file:
        super_low = json.load(cj_file)["super_low"]
    return super_low


def check_cost():
    current_time = datetime.now()
    timestamp = current_time.strftime("%B %d, %Y %H:%M:%S")
    args = get_args()
    netuid = args.netuid
    try:
        cost = get_recycle_amount(netuid=netuid)
        if cost <= 1.6:
            if cost > 0.5:
                msg = f"🏷️✂️💸  Cost Low! We're So Fucking Back! - {cost} $TAO"
                sr_msg = f"🏷️✂️💸 Cost Still Reasonable - {cost} $TAO"
                log = f"Cost Low! - {cost} $COMAI"
                if get_low() == 0:
                    send_notification(msg)
                if get_super_low() == 1:
                    send_notification(sr_msg)
                update_cost(1, 0)
            else:
                msg = f"💸💸💸 Cost Super Low! Register Now! - {cost} $TAO"
                log = f"Cost Super Low! - {cost} $TAO"
                if get_super_low() == 0:
                    send_notification(msg)
                update_cost(1, 1)
        else:
            msg = f"😢 It's Over. It's Never Been More Over - {cost} $TAO"
            log = f"It's Over - {cost} $TAO"
            if get_low() == 1:
                send_notification(msg)
            update_cost(0, 0)
        print(f"[{timestamp}] - {log}")
    except ValueError as ve:
        print(f"[{timestamp}] - ValueError (error parsing cost): {ve}")
    except Exception as e:
        print(f"[{timestamp}] - Exception: {e}")


if __name__ == "__main__":
    while True:
        check_cost()
        time.sleep(300)
