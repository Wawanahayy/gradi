import json
import requests
import datetime
import urllib3
from loguru import logger

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


GET_POINT_URL = "https://api.gradient.network/api/point/stats"

# Create a session for requests
session = requests.Session()

# Set common request headers
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Priority": "u=1, i",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

def login(username, password):
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
    data = {
        "username": username,
        "password": password,
        "logindata": {
            "_v": "1.0.7",
            "datetime": current_time
        }
    }
    login_data = json.dumps(data)
    logger.info(f'[2] Login Data: {login_data}')
    try:
        response = session.post(LOGIN_URL, data=login_data, headers=HEADERS, verify=False)
        response.raise_for_status()  # Raise error for HTTP errors
        r = response.json()
        token = r['data']['token']
        logger.success(f'[√] Successfully obtained AuthToken: {token}')
        return token
    except Exception as e:
        logger.error(f'[x] Login failed, error: {e}')
        return None

def keep_alive(username, token):
    data = {"username": username, "extensionid": "caacbgbklghmpodbdafajbgdnegacfmo", "numberoftabs": 0, "_v": "1.0.1"}
    json_data = json.dumps(data)
    HEADERS['authorization'] = "Bearer " + str(token)
    try:
        response = session.post(KEEP_ALIVE_URL, data=json_data, headers=HEADERS, verify=False)
        response.raise_for_status()
        logger.info(f'[3] Keeping connection alive: {response.json()}')
    except Exception as e:
        logger.error(f'[x] KeepAlive failed, error: {e}')

def get_point(token):
    HEADERS['authorization'] = "Bearer " + str(token)
    try:
        response = session.get(GET_POINT_URL, headers=HEADERS, verify=False)
        response.raise_for_status()
        r = response.json()
        logger.success(f'[√] Successfully obtained points: {r}')
    except Exception as e:
        logger.error(f'[x] Failed to get points, error: {e}')

def main(username, password):
    token = login(username, password)
    if token:
        while True:
            try:
                keep_alive(username, token)
                get_point(token)
            except KeyboardInterrupt:
                logger.info("[*] Exiting the script.")
                break
            except Exception as e:
                logger.error(e)

if __name__ == '__main__':
    try:
        with open('password.txt', 'r') as f:
            username, password = f.readline().strip().split(':')
        main(username, password)
    except FileNotFoundError:
        logger.error('[x] Password file not found. Please ensure it exists.')
    except ValueError:
        logger.error('[x] Invalid format in password file. Ensure it is in the format username:password.')
