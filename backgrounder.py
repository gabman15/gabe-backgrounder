#!/usr/bin/python

import argparse
import json
import requests
from base64 import b64encode
import random
import os
import sys

def set_bg(img):
    if (os.getenv('WAYLAND_DISPLAY') is not None):
        os.system('swaymsg output "*" bg ' + img + " fit")
    else:
        os.system("feh --bg-max " + img)

def get_total(szuru_api_url: str, headers: dict) -> int:
    query_url = szuru_api_url + '/posts/?query=gabe_background'
    response_json = requests.get(query_url, headers=headers)
    response = response_json.json()
    return response['total']

def download_post(szuru_url: str, headers: dict, num: int, loc: str, alt_img: str) -> str:
    szuru_api_url = szuru_url + '/api'
    offset = num - (num % 100)
    query_url = szuru_api_url + '/posts/?offset=' + str(offset) + '&query=gabe_background%20sort%3Arandom&limit=100'

    response_json = requests.get(query_url, headers=headers)
    response = response_json.json()
    #print(response['total'])
    results = response['results']

    result = results[(num % 100)]

    filename = result['contentUrl'][10:]

    if filename == alt_img:
        return ""

    dl_url = szuru_url + '/' + result['contentUrl']

    img = requests.get(dl_url)

    open(loc + filename, 'wb').write(img.content)

    return filename

def encode_auth_headers(user: str, token: str) -> dict:
    """Creates an authentication header from the user and token.

    This header is needed to interact with the szurubooru API.

    Args:
        szuru_user (str): The szurubooru user which interacts with the API.
        szuru_token (str): The API token from `szuru_user`.

    Returns:
        dict: The request header with the encoded base64 authentication token.
    """

    return {'Content-Type': 'application/json', 'Accept': 'application/json',
               'Authorization': 'Token ' + b64encode(f'{user}:{token}'.encode()).decode('ascii')}

def download_start(szuru_url: str, headers: dict, loc: str, alt_img: str) -> str:
    szuru_api_url = szuru_url + '/api'

    total = get_total(szuru_api_url, headers)

    random.seed()

    return gen_random_img(szuru_url, headers, loc, alt_img, total)

def gen_random_img(szuru_url, headers, loc, alt_img, total) -> str:
    while True:
        num = int(random.randint(0,total - 1))
        img = download_post(szuru_url, headers, num, loc, alt_img)
        if img != "":
            break
    return img

def check_connection(szuru_url, headers) -> bool:
    try:
        requests.get(szuru_url + '/api/info', headers=headers)
        return True
    except:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='backgrounder')
    parser.add_argument('-c', '--config', default="config.json")
    parser.add_argument('-d', '--directory', default="/tmp/backgrounder")
    args = parser.parse_args()
    img_loc = args.directory

    config = open(args.config, 'r')
    config_data = json.load(config)
    url = config_data['url']
    user = config_data['user']
    token = config_data['token']

    headers = encode_auth_headers(user, token)

    if (not check_connection(url, headers)):
        sys.exit("Couldn't connect to szurubooru")

    # directory = os.path.dirname(img_loc)
    os.makedirs(img_loc, exist_ok=True)

    if (not os.path.isfile(img_loc + '/bg.json')):
        bg_file = open(img_loc + '/bg.json', 'w')
        bg_file.write(json.dumps({'current':0}))
        bg_file.close()
    bg_file = open(img_loc + '/bg.json', 'r')
    bg_data = json.load(bg_file)

    if (bg_data['current'] == 1):
        set_bg(img_loc + bg_data['2'])
        os.remove(img_loc + bg_data['1'])
        bg_data['1'] = download_start(url, headers, img_loc, bg_data['2'])
        bg_data['current'] = 2
    elif (bg_data['current'] == 2):
        set_bg(img_loc + bg_data['1'])
        os.remove(img_loc + bg_data['2'])
        bg_data['2'] = download_start(url, headers, img_loc, bg_data['1'])
        bg_data['current'] = 1
    else:
        bg_data['1'] = download_start(url, headers, img_loc, "")
        set_bg(img_loc + bg_data['1'])
        bg_data['2'] = download_start(url, headers, img_loc, bg_data['1'])
        bg_data['current'] = 1

    bg_file = open(img_loc + '/bg.json', 'w')
    json.dump(bg_data, bg_file)
