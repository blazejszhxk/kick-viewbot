import asyncio
import random
import threading
import time
import traceback
import curl_cffi
from curl_cffi import requests, AsyncSession

def load_proxies(file_path="proxies.txt"):
    try:
        with open(file_path, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            print(f"Missing proxies: '{file_path}' is empty.")
            exit(1)
        print(f"Loaded {len(proxies)} proxies from: {file_path}")
        return proxies
    except FileNotFoundError:
        print(f"Missing proxies file: {file_path}")
        exit(1)
    except Exception as e:
        print(f"Proxy load error: {e}")
        exit(1)

proxies_list = load_proxies()

def pick_proxy():
    proxy = random.choice(proxies_list)
    try:
        ip, port, user, pwd = proxy.split(":")
        full_url = f"http://{user}:{pwd}@{ip}:{port}"
        proxy_dict = {"http": full_url, "https": full_url}
        return proxy_dict, full_url
    except ValueError:
        print(f"Bad proxy format: {proxy}, (use ip:port:user:pass)")
        return None, None
    except Exception as e:
        print(f"Proxy error: {proxy}, {e}")
        return None, None

def get_channel_id(channel_name):
    max_attempts = 5
    for _ in range(max_attempts):
        s = requests.Session(impersonate="firefox135")
        proxy_dict, _ = pick_proxy()
        if not proxy_dict:
            continue
        s.proxies = proxy_dict
        try:
            r = s.get(f"https://kick.com/api/v2/channels/{channel_name}")
            if r.status_code == 200:
                return r.json().get("id")
            else:
                print(f"Channel ID: {r.status_code}, retrying...")
        except Exception as e:
            print(f"Channel ID: {e}, retrying...")
        time.sleep(1)
    print("Channel ID: Failed after retries.")
    return None

def get_token():
    max_attempts = 5
    for _ in range(max_attempts):
        s = requests.Session(impersonate="firefox135")
        proxy_dict, proxy_url = pick_proxy()
        if not proxy_dict:
            continue
        s.proxies = proxy_dict
        try:
            s.get("https://kick.com")
            s.headers["X-CLIENT-TOKEN"] = "e1393935a959b4020a4491574f6490129f678acdaa92760471263db43487f823"
            r = s.get('https://websockets.kick.com/viewer/v1/token')
            if r.status_code == 200:
                token = r.json()["data"]["token"]
                return token, proxy_url
            else:
                print(f"Token: {r.status_code}, trying another proxy...")
        except Exception as e:
            print(f"Token: {e}, trying another proxy...")
        time.sleep(1)
    return None, None

def start_connection_thread(channel_id, index):
    async def connection_handler():
        max_retries = 5
        for _ in range(max_retries):
            token, proxy_url = get_token()
            if not token:
                print(f"[{index}] Failed to get token, retrying...")
                await asyncio.sleep(3)
                continue

            print(f"[{index}] Got token: {token} using proxy: {proxy_url}")
            try:
                async with AsyncSession() as session:
                    ws = await session.ws_connect(
                        f"wss://websockets.kick.com/viewer/v1/connect?token={token}",
                        proxy=proxy_url)
                    counter = 0
                    while True:
                        counter += 1
                        if counter % 2 == 0:
                            await ws.send_json({"type": "ping"})
                            print(f"[{index}] ping")
                        else:
                            await ws.send_json({
                                "type": "channel_handshake",
                                "data": {"message": {"channelId": channel_id}}
                            })
                            print(f"[{index}] handshake")
                        delay = 11 + random.randint(2, 7)
                        print(f"[{index}] waiting {delay}s")
                        await asyncio.sleep(delay)
            except curl_cffi.CurlError as e:
                print(f"[{index}] Proxy error: {e}. Trying another proxy...")
                await asyncio.sleep(random.randint(4, 8))
            except Exception as e:
                print(f"[{index}] Unexpected error: {e}")
                traceback.print_exc()
                await asyncio.sleep(3)

    asyncio.run(connection_handler())

if __name__ == "__main__":
    channel = input("Channel link or name: ").split("/")[-1]
    total_views = int(input("How many viewers to send: "))

    channel_id = get_channel_id(channel)
    if not channel_id:
        print("Channel not found.")
        exit(1)

    threads = []
    for i in range(total_views):
        t = threading.Thread(target=start_connection_thread, args=(channel_id, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()