import requests
import string
import time
import itertools
import os
import random
import socks
import socket
from requests.auth import HTTPDigestAuth

UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"
SKIN_URL = "https://crafatar.com/skins/{uuid}"
USE_PROXIES = True
ONLY_ALPHABETS = True

def get_uuid(username, proxies=None):
    response = requests.get(UUID_URL.format(username=username), proxies=proxies)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return None

def download_skin(uuid, path, proxies=None):
    url = SKIN_URL.format(uuid=uuid)
    response = requests.get(url, stream=True, proxies=proxies)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response:
                file.write(chunk)

delay = 1

if not os.path.exists("proxy.txt"):
    with open("proxy.txt", "w") as file:
        file.write("127.0.0.1:8080:username:password\n")

proxies_list = []
if USE_PROXIES:
    with open("proxy.txt", "r") as file:
        for line in file:
            host, port, user, password = line.strip().split(":")
            proxies = {
                "http": f"socks5://{user}:{password}@{host}:{port}",
                "https": f"socks5://{user}:{password}@{host}:{port}",
            }
            proxies_list.append(proxies)

if ONLY_ALPHABETS:
    all_combinations = [''.join(i) for i in itertools.product(string.ascii_lowercase, repeat=3)]
else:
    all_combinations = [''.join(i) for i in itertools.product(string.ascii_lowercase + string.digits + '_', repeat=3)]

random.shuffle(all_combinations)
os.makedirs("skins", exist_ok=True)

# Create or load 'scraped_usernames.txt'
if not os.path.exists("scraped_usernames.txt"):
    with open("scraped_usernames.txt", "w") as file:
        pass
with open("scraped_usernames.txt", "r") as file:
    scraped_usernames = [line.strip() for line in file]

for username in all_combinations:
    if username in scraped_usernames:  # Skip usernames already viewed
        print(f"Username: {username} already viewed. Skipping.")
        continue
    proxies = random.choice(proxies_list) if USE_PROXIES else None
    uuid = get_uuid(username, proxies)
    if uuid is not None:
        download_skin(uuid, f"skins/{username}.png", proxies)
        with open("scraped_usernames.txt", "a") as file:  # Append scraped username to 'scraped_usernames.txt'
            file.write(f"{username}\n")
        print(f"Username: {username}, Skin downloaded")
    time.sleep(delay)

# If all combinations have been viewed, print a message and exit
if set(scraped_usernames) == set(all_combinations):
    if ONLY_ALPHABETS:
        print("All alphabet usernames have been scraped.")
    else:
        print("All alphanumeric and underscore usernames have been scraped.")
    exit()
