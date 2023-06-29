import requests
import string
import time
import itertools
import os
import random
import socks
import socket
from requests.auth import HTTPDigestAuth

# The Mojang API URL to get UUID for a username
UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"

# The Mojang API URL to get the skin for a UUID
SKIN_URL = "https://crafatar.com/skins/{uuid}"

# Set whether to use proxies
USE_PROXIES = True

# Set whether to use only alphabets for usernames (A-Z)
ONLY_ALPHABETS = True

# Get the UUID for a username
def get_uuid(username, proxies=None):
    response = requests.get(UUID_URL.format(username=username), proxies=proxies)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return None

# Download and save the skin to a file
def download_skin(uuid, path, proxies=None):
    url = SKIN_URL.format(uuid=uuid)
    response = requests.get(url, stream=True, proxies=proxies)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response:
                file.write(chunk)

# Set the delay for downloading skins (in seconds)
delay = 1

# Check if proxy.txt exists, if not, create a default one
if not os.path.exists("proxy.txt"):
    with open("proxy.txt", "w") as file:
        file.write("127.0.0.1:8080:username:password\n")

# Load proxies from file
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

# Generate all possible 3-letter combinations based on ONLY_ALPHABETS
if ONLY_ALPHABETS:
    all_combinations = [''.join(i) for i in itertools.product(string.ascii_lowercase, repeat=3)]
else:
    all_combinations = [''.join(i) for i in itertools.product(string.ascii_lowercase + string.digits + '_', repeat=3)]

# Shuffle the combinations to get them in random order
random.shuffle(all_combinations)

# Make sure the skins directory exists
os.makedirs("skins", exist_ok=True)

# Iterate over all 3-letter combinations
for username in all_combinations:
    proxies = random.choice(proxies_list) if USE_PROXIES else None  # Select a random proxy if USE_PROXIES is True
    uuid = get_uuid(username, proxies)
    if uuid is not None:
        download_skin(uuid, f"skins/{username}.png", proxies)
        print(f"Username: {username}, Skin downloaded")
    time.sleep(delay)  # Delay between lookups
