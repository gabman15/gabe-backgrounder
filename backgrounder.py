import json
import requests
from base64 import b64encode
import random
import os

def get_total(szuru_api_url: str, headers: str) -> int:
    query_url = szuru_api_url + '/posts/?query=gabe_background'
    response_json = requests.get(query_url, headers=headers)
    response = response_json.json()
    return response['total']

def download_post(szuru_url: str, headers: str, num: int, loc: str, alt_img: str) -> str:
    szuru_api_url = szuru_url + '/api'
    offset = num - (num % 100)
    query_url = szuru_api_url + '/posts/?offset='+str(offset)+'&query=gabe_background%20sort%3Arandom&limit=100'

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

    open(loc+filename, 'wb').write(img.content)

    return filename
    
def encode_auth_headers(user: str, token: str) -> str:
        """Creates an authentication header from the user and token.

        This header is needed to interact with the szurubooru API.

        Args:
            szuru_user (str): The szurubooru user which interacts with the API.
            szuru_token (str): The API token from `szuru_user`.

        Returns:
            str: The encoded base64 authentication header.
        """

        return b64encode(f'{user}:{token}'.encode()).decode('ascii')

def download_start(szuru_url: str, szuru_user: str, szuru_token: str, loc: str, alt_img: str) -> str:
    szuru_api_url = szuru_url + '/api'
    
    token = encode_auth_headers(szuru_user, szuru_token)
    
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Token ' + token}

    total = get_total(szuru_api_url, headers)
    
    random.seed()
        
    return gen_random_img(szuru_url, headers, loc, alt_img, total)

def gen_random_img(szuru_url, headers, loc, alt_img, total) -> str:
    while True:
        num = int(random.randint(0,total-1))
        img = download_post(szuru_url, headers, num, loc, alt_img)
        if img != "":
            break
    return img
                    
def _main():
    img_loc = "/home/lord_gabem/Pictures/backgrounds"
    bg_file = open(img_loc+'/bg.json','r')
    config = open("config.json",'r')
    config_data = json.load(config)
    url = config_data['url']
    user = config_data['user']
    token = config_data['token']
    
    bg_data = json.load(bg_file)


    if(bg_data['current'] == 1):
        os.system("feh --bg-max "+img_loc+bg_data['2'])
        os.system("rm "+img_loc+bg_data['1'])
        bg_data['1'] = download_start(url, user, token, img_loc, bg_data['2'])
        bg_data['current'] = 2
    else:
        os.system("feh --bg-max "+img_loc+bg_data['1'])
        os.system("rm "+img_loc+bg_data['2'])
        bg_data['2'] = download_start(url, user, token, img_loc, bg_data['1'])
        bg_data['current'] = 1
    bg_file = open(img_loc+'/bg.json','w')
    json.dump(bg_data, bg_file)
    
_main()
